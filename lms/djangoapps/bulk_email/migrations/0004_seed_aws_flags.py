# -*- coding: utf-8 -*-
from __future__ import unicode_literals

import os
from django.db import migrations, models

def forwards_func(apps, schema_editor):
    if os.environ["DJANGO_SETTINGS_MODULE"] == "lms.envs.aws":
        BulkEmailFlag = apps.get_model("bulk_email", "BulkEmailFlag")
        db_alias = schema_editor.connection.alias
        BulkEmailFlag.objects.using(db_alias).create(enabled=True, require_course_email_auth=True)

def reverse_func():
    pass

class Migration(migrations.Migration):

    dependencies = [
        ('bulk_email', '0003_config_model_feature_flag'),
    ]

    operations = [
        migrations.RunPython(forwards_func, reverse_func),
    ]
