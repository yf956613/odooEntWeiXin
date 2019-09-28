/**
 * Copyright (C) 2019 SuXueFeng License(GNU)
 */
odoo.define('ent.external.contact.tree.button', function (require) {
    "use strict";

    let ListController = require('web.ListController');
    let ListView = require('web.ListView');
    let viewRegistry = require('web.view_registry');

    let EntExternaLcontactViewController = ListController.extend({
        buttons_template: 'OdooEntWeiXinListView.EntExternaLcontact_Tree_Buttton',
        renderButtons: function () {
            this._super.apply(this, arguments);
            if (this.$buttons) {
                let self = this;
                this.$buttons.on('click', '.ent_externa_lcontact_tree_but', function () {
                    self.do_action({
                        type: 'ir.actions.act_window',
                        res_model: 'ent.external.contact.tran',
                        target: 'new',
                        views: [[false, 'form']],
                        context: [],
                    },{
                        on_reverse_breadcrumb: function () {
                            self.reload();
                        },
                        on_close: function () {
                            self.reload();
                        }
                    });
                });
            }
        }
    });

    let EntExternaLcontactCumulativeView = ListView.extend({
        config: _.extend({}, ListView.prototype.config, {
            Controller: EntExternaLcontactViewController,
        }),
    });

    viewRegistry.add('ent_externa_lcontact_class', EntExternaLcontactCumulativeView);
});
