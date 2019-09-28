# -*- coding: utf-8 -*-
###################################################################################
#    Copyright (C) 2019 SuXueFeng
###################################################################################
import logging
from wechatpy.enterprise.client.api import WeChatTag
from odoo import api, fields, models
from odoo.exceptions import UserError
from odoo.addons.weixin_ent_base.weixin_ent_tool.wx_tool import app_client

_logger = logging.getLogger(__name__)


class EmployeeTags(models.TransientModel):
    _description = "成员标签"
    _name = 'hr.employee.tags.tran'

    @api.multi
    def pull_employee_tags(self):
        """
        拉取成员标签
        :return:
        """
        try:
            client = WeChatTag(app_client('ent_wx_ab_secret'))
            result = client.list()
        except Exception as e:
            raise UserError(str(e))
        for res in result:
            data = {
                'name': res['tagname'],
                'wx_ent_id': res['tagid'],
                'api_state': False,  # 标识是同步下来的记录，不再通过创建、修改时上传操作
            }
            tags = self.env['hr.employee.tags'].search([('wx_ent_id', '=', res['tagid'])])
            if tags:
                tags.write(data)
            else:
                self.env['hr.employee.tags'].create(data)
        return {'type': 'ir.actions.client', 'tag': 'reload'}


class AddEmployeeTags(models.TransientModel):
    _description = "添加标签成员"
    _name = 'add.employee.tags.tran'

    tag_id = fields.Char(string='标签id')
    emp_ids = fields.Many2many('hr.employee', string=u'标签成员', domain=[('ent_wx_id', '!=', '')])

    @api.multi
    def add_employee(self):
        """
        将选择的成员添加到标签中
        :return:
        """
        self.ensure_one()
        tag_id = self.tag_id
        tags = self.env['hr.employee.tags'].search([('wx_ent_id', '=', tag_id)])
        tag_emp_ids = tags.employee_ids.ids
        for emp in self.emp_ids:
            tag_emp_ids.append(emp.id)
            try:
                client = WeChatTag(app_client('ent_wx_ab_secret'))
                result = client.add_users(tag_id, emp.ent_wx_id)
            except Exception as e:
                raise UserError(str(e))
            if result['errcode'] != 0:
                raise UserError(result['errmsg'])
        new_ids = list(set(tag_emp_ids))
        tags.write({'employee_ids': [(6, 0, new_ids)]})
        tags.message_post(body=u"已成功添加{}条成员到标签中！".format(len(self.emp_ids)), message_type='notification')
        return {'type': 'ir.actions.act_window_close'}

    @api.model
    def default_get(self, fields):
        record_id = self._context.get('active_id')
        result = super(AddEmployeeTags, self).default_get(fields)
        if record_id:
            tags = self.env['hr.employee.tags'].browse(record_id)
            if 'tag_id' in fields:
                result['tag_id'] = tags.wx_ent_id
        return result


class DeleteEmployeeTags(models.TransientModel):
    _description = "删除标签成员"
    _name = 'delete.employee.tags.tran'

    tag_id = fields.Char(string='标签id')
    emp_ids = fields.Many2many('hr.employee', string=u'删除成员', domain=[('ent_wx_id', '!=', '')])

    @api.multi
    def delete_employee(self):
        """
        删除标签成员方法
        :return:
        """
        self.ensure_one()
        tag_id = self.tag_id
        tags = self.env['hr.employee.tags'].search([('wx_ent_id', '=', tag_id)])
        emp_ex_id = list()
        for emp in self.emp_ids:
            emp_ex_id.append(emp.ent_wx_id)
        try:
            client = WeChatTag(app_client('ent_wx_ab_secret'))
            result = client.delete_users(tag_id, emp_ex_id)
        except Exception as e:
            raise UserError(str(e))
        if result['errcode'] != 0:
            raise UserError(result['errmsg'])
        tags.write({'employee_ids': [(2, 0, self.emp_ids.ids)]})
        tags.message_post(body=u"已成功删除{}条成员！".format(len(self.emp_ids)), message_type='notification')
        return {'type': 'ir.actions.act_window_close'}

    @api.model
    def default_get(self, fields):
        record_id = self._context.get('active_id')
        result = super(DeleteEmployeeTags, self).default_get(fields)
        if record_id:
            tags = self.env['hr.employee.tags'].browse(record_id)
            if 'emp_ids' in fields:
                result['tag_id'] = tags.wx_ent_id
                result['emp_ids'] = [(6, 0, tags.employee_ids.ids)]
        return result
