;(function(define) {
    'use strict';

    define(['jquery', 'logger'], function ($, Logger) {
        return function () {
            $("a").click(function(event) {
                var parent_id = $(event.currentTarget).parent(".xblock");
                if (!parent) {
                    parent_id = $(event.currentTarget).parent(".course-navigation");
                }
                Logger.log(
                    "edx.ui.lms.link_clicked",
                    {
                        current_url: window.location.href,
                        target_url: event.currentTarget.href,
                        containing_element: parent_id
                    });
            });
        };
    });
}).call(this, define || RequireJS.define);
