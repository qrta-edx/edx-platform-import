import csv
import logging
import tempfile

from django.core.management.base import BaseCommand
from xmodule.modulestore.django import modulestore
from collections import defaultdict
import gc
import os

log = logging.getLogger(__name__)

class ModuleStoreSerializer(object):
    """
    Class with functionality to serialize a modulestore to CSVs:
    Each csv will have information about one kind of xblock.
    There will also be a "relationships" csv with information about
    which xblocks are children of each other.
    """
    def __init__(self, csv_dir, neo4j_root):
        self.csv_dir = csv_dir
        self.neo4j_root = neo4j_root

        # caches field names for each block type
        self.field_names_by_block_type = {}
        self.all_courses = modulestore().get_course_summaries()

    def upload_to_s3(self):
        """Upload generated csvs to an s3 bucket."""
        pass

    def dump_to_csv(self):
        """
        Dump the modulestore to csv files: one file per kind
        of XBlock, and one file to map the parent-child relationships
        between them.
        """
        number_of_courses = len(self.all_courses)
        for index, course in enumerate(self.all_courses):
            log.info(
                u"dumping course \t\t{}/{}:\t{}".format(
                    index + 1, number_of_courses, unicode(course.id)
                )
            )
            self.dump_course_items_to_csv(course.id)

    def dump_course_items_to_csv(self, course_key):
        """
        Args:
            course_key: a course key

        Returns: None

        For each course, add its serialized items to its appropriate items
        and relationship csvs.
        """
        items = modulestore().get_items(course_key)
        blocks_by_type = self.serialize_items(items, course_key)
        self.dump_blocks_to_csv(blocks_by_type)

        relationships = self.get_relationships_from_items(items)
        self.dump_relationships_to_csv(relationships)

    def dump_blocks_to_csv(self, blocks_by_type):
        """
        Args:
            blocks_by_type: dictionary mapping block types to a list of
            serialized blocks of that type:
            {block_type: [{block_field: value}]}

        Returns: None

        Dump serialized versions of blocks to appropriate csv files.
        """
        for block_type, serialized_xblocks in blocks_by_type.iteritems():
            field_names = self.get_field_names_for_type(block_type, serialized_xblocks)

            rows = []
            for serialized in serialized_xblocks:
                row = [
                    self.normalize_value(serialized[field_name])
                    for field_name
                    in field_names
                ]
                rows.append(row)

            filename = os.path.abspath(
                os.path.join(
                    self.csv_dir,
                    "{block_type}.csv".format(block_type=block_type)
                )
            )

            with open(filename, 'a+') as csvfile:
                writer = csv.writer(csvfile)
                if csvfile.tell() == 0:
                    writer.writerow(field_names)
                writer.writerows(rows)

    def dump_relationships_to_csv(self, relationships):
        rows = []
        rows.extend(relationships)
        filename = os.path.abspath(os.path.join(self.csv_dir, 'relationships.csv'))
        with open(filename, 'a') as csvfile:
            # if this file hasn't been written to yet, add a header
            writer = csv.writer(csvfile)
            if csvfile.tell() == 0:
                writer.writerow([':START_ID', ':END_ID'])

            writer.writerows(rows)

    def normalize_value(self, value):
        if value is None:
            value = 'NULL'
        value = unicode(value).encode('utf-8')
        # neo4j has an annoying thing where it freaks out if a field begins
        # with a quotation mark
        while value.startswith('"') or value.startswith("'"):
            value = value.strip('"')
            value = value.strip("'")

        return value

    def get_field_names_for_type(self, block_type, serialized_xblocks):
        field_names = self.field_names_by_block_type.get(block_type)
        if field_names is None:
            field_names = serialized_xblocks[0].keys()
            field_names.remove('type:LABEL') ## this needs to be first for some reason
            field_names = ['type:LABEL'] + field_names
            self.field_names_by_block_type[block_type] = field_names

        return field_names

    def serialize_item(self, item, course_key):
        # convert all fields to a dict and filter out parent and children field
        fields = dict(
            (field, field_value.read_from(item))
            for (field, field_value) in item.fields.iteritems()
            if field not in ['parent', 'children']
        )

        fields['edited_on'] = unicode(getattr(item, 'edited_on', u''))
        fields['display_name'] = item.display_name_with_default

        fields['location:ID'] = unicode(item.location)
        if "location" in fields:
            del fields['location']

        block_type = item.scope_ids.block_type

        fields['type'] = block_type

        fields['type:LABEL'] = fields['type']
        del fields['type']

        if 'checklists' in fields:
            del fields['checklists']

        fields['org'] = course_key.org
        fields['course'] = course_key.course
        fields['run'] = course_key.run
        fields['course_key'] = unicode(course_key)

        return fields, block_type

    def serialize_items(self, items, course_key):
        blocks_by_type = defaultdict(list)
        for item in items:
            serialized_item, block_type = self.serialize_item(item, course_key)
            blocks_by_type[block_type].append(serialized_item)

        return blocks_by_type

    def get_relationships_from_items(self, items):
        relationships = []
        for item in items:
            if item.has_children:
                for child in item.children:
                    parent_loc = unicode(item.location)
                    child_loc = unicode(child)
                    relationships.append([parent_loc, child_loc])
        return relationships


class Command(BaseCommand):
    """
    Generates CSVs to be used with neo4j's csv import tool (this is much
    faster for bulk importing than using py2neo, which updates neo4j over
    a REST api)
    """

    def add_arguments(self, parser):
        parser.add_argument('--neo4j_root',
            action='store',
            dest='neo4j_root',
            default="/tmp/neo4j",
            help='where to run neo4j command from'
        )

        parser.add_argument('--csv_dir',
            action='store',
            dest='csv_dir',
            default="/tmp/csvs",
            help='where to dump csv files to'
        )

    def handle(self, *args, **options):
        """
        Management command to dump modulestore data to csvs.
        Also generates the command necessary to import those csvs into neo4j.
        """
        # TODO: switch this to use mkdtemp_clean.
        # https://github.com/edx/edx-platform/blob/master/openedx/core/lib/tempdir.py#L9
        # csv_dir = tempfile.mkdtemp(prefix="csvs_", dir="/tmp")
        csv_dir = os.path.abspath(options['csv_dir'])
        neo4j_root = os.path.abspath(options["neo4j_root"])
        self.clear_csv_dir()

        module_store_serializer = ModuleStoreSerializer(csv_dir, neo4j_root)
        module_store_serializer.dump_to_csv()
        print("Use the following command to import your csvs into neo4j")
        print(self.generate_bulk_import_command(module_store_serializer))

    def generate_bulk_import_command(self, module_store_serializer):
        """
        Generates the command to be used for
        """

        command = "{neo4j_root}/bin/neo4j-import --id-type string"
        for filename in os.listdir(module_store_serializer.csv_dir):
            if filename.endswith(".csv") and filename != "relationships.csv":
                name = filename[:-4]  # cut off .csv
                node_info = " --nodes:{name} {csv_dir}/{filename}".format(
                    csv_dir=module_store_serializer.csv_dir,
                    name=name,
                    filename=filename,
                )
                command += node_info

        command += " --relationships:PARENT_OF relationships.csv"
        command += " --into {neo4j_root}/data/coursegraph"
        command += " --multiline-fields=true"
        command += " --quote=''"
        # we need to set --bad-tolerance because old mongo has a lot of
        # dangling pointers
        command += " --bad-tolerance=1000000"
        return command.format(neo4j_root=module_store_serializer.neo4j_root)

    def clear_csv_dir(self):
        """
        Clear out the csv dir before dumping course data to it.
        Returns: None
        """
        for filename in os.listdir(self.csv_dir):
            filename = os.path.abspath(os.path.join(self.csv_dir, filename))
            # delete csv files if they already exist
            if filename.endswith(".csv"):
                os.unlink(filename)
