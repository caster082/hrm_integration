odoo.define('hms_integration.tree_view_button', function (require){
    "use strict";

    var ajax = require('web.ajax');
    var ListController = require('web.ListController');

    var rpc = require('web.rpc')

    ListController.include({
        renderButtons: function($node) {
            this._super.apply(this, arguments);
            var self = this;
            if (this.$buttons) {
                $(this.$buttons).find('.oe_new_custom_button_tree').on('click', function() {
                    rpc.query({
                        model: 'sales.order.integration',
                        method: 'connect_function',
                        args: [""],
                    }).then(function(res){
                           self.do_action(res);
                         //console.log(res)
                         //self.reload();
                    })
                });
            }
        },
    });
});