define(["underscore", "paging-collection", "js/models/asset"], function(_, PagingCollection, AssetModel) {
    var AssetCollection = PagingCollection.extend({
        assetType: '',
        model : AssetModel,

        state: {
            firstPage: 0,
            pageSize: 50,
            sortKey: 'sort',
            order: null,
            currentPage: null,
            totalRecords: null,
            totalCount: null
        },

        queryParams: {
            currentPage: 'page',
            pageSize: 'page_size',
            sortKey: 'sort',
            order: 'direction',
            directions: {
                asc: 'asc',
                desc: 'desc'
            },
            asset_type: function() { return this.assetType; }
        },

        parse: function(response, options) {
            response.results = response.assets;
            delete response.assets;
            return PagingCollection.prototype.parse.call(this, response, options);
        },

        parseState: function (response, queryParams, state, options) {
            return {
                totalRecords: response[0].totalCount,
                totalPages: Math.ceil(response[0].totalCount / response[0].pageSize)
            };
        },

        getTotalPages: function () {
            return this.state.totalPages;
        },

        getTotalRecords: function () {
            return this.state.totalRecords;
        },

        getPageSize: function () {
            return this.state.pageSize;
        }
    });

    return AssetCollection;
});
