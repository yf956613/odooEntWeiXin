/**
 * Copyright (C) 2019 SuXueFeng License(GNU)
 */
odoo.define('hr.employee.tags.tree.button', function (require) {
    "use strict";

    let ListController = require('web.ListController');
    let ListView = require('web.ListView');
    let viewRegistry = require('web.view_registry');

    let HrEmployeeTagsViewController = ListController.extend({
        buttons_template: 'OdooEntWeiXinListView.Hr_EmployeeTags_Tree_Buttton',
        renderButtons: function () {
            this._super.apply(this, arguments);
            if (this.$buttons) {
                let self = this;
                this.$buttons.on('click', '.pull_weixin_ent_employee_tags_but', function () {
                    self.do_action({
                        type: 'ir.actions.act_window',
                        res_model: 'hr.employee.tags.tran',
                        target: 'new',
                        views: [[false, 'form']],
                        context: [],
                    });
                });
            }
        }
    });

    let HrEmployeeTagsCumulativeView = ListView.extend({
        config: _.extend({}, ListView.prototype.config, {
            Controller: HrEmployeeTagsViewController,
        }),
    });

    viewRegistry.add('hr_employee_tags_class', HrEmployeeTagsCumulativeView);
});
