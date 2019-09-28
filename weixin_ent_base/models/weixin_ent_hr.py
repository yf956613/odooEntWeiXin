# -*- coding: utf-8 -*-
###################################################################################
#    Copyright (C) 2019 SuXueFeng
###################################################################################
import logging
from odoo import api, fields, models
from odoo.exceptions import UserError
from odoo.addons.weixin_ent_base.weixin_ent_tool.wx_tool import request_post, request_get, app_client
from wechatpy.enterprise.client.api import WeChatTag

_logger = logging.getLogger(__name__)


class HrDepartment(models.Model):
    _inherit = 'hr.department'

    ent_wx_id = fields.Char(string='企业微信部门ID', index=True)

    @api.multi
    def create_ent_weixin_department(self):
        """
        创建企业微信部门
        :return:
        """
        url, token = self.env['weixin.ent.parameter'].get_token_and_value('department_create', 'ent_wx_ab_token')
        for res in self:
            self._check_parent_id(res)
            data = {
                'name': res.name,
                'parentid': res.parent_id.ent_wx_id,
            }
            result = request_post(url, token, data)
            if result['errcode'] != 0:
                raise UserError(result['errmsg'])
            res.write({'ent_wx_id': result['id']})
            res.message_post(body=u"已成功同步至企业微信部门", message_type='notification')

    @api.multi
    def write_ent_weixin_department(self):
        """
        修改企业微信部门
        :return:
        """
        url, token = self.env['weixin.ent.parameter'].get_token_and_value('department_update', 'ent_wx_ab_token')
        for res in self:
            if not res.ent_wx_id:
                raise UserError("'%s'不是企业微信部门，请先创建或同步到企业微信！" % res.name)
            self._check_parent_id(res)
            data = {
                'id': res.ent_wx_id,
                'name': res.name,
                'parentid': res.parent_id.ent_wx_id,
            }
            result = request_post(url, token, data)
            if result['errcode'] != 0:
                raise UserError(result['errmsg'])
            res.message_post(body=u"已更新至企业微信部门", message_type='notification')

    @api.multi
    def delete_ent_weixin_department(self):
        """
        删除企业微信部门
        :return:
        """
        url, token = self.env['weixin.ent.parameter'].get_token_and_value('department_delete', 'ent_wx_ab_token')
        for res in self:
            if not res.ent_wx_id:
                raise UserError("'%s'不是企业微信部门，请先创建或同步到企业微信！" % res.name)
            data = {'id': res.ent_wx_id}
            result = request_get(url, token, data)
            if result['errcode'] != 0:
                raise UserError(result['errmsg'])
            res.write({'parent_id': False, 'ent_wx_id': False})
            res.message_post(body=u"已删除部门至企业微信", message_type='notification')

    @api.model
    def _check_parent_id(self, department):
        """
        检查上级部门
        :param department:
        :return:
        """
        if not department.parent_id:
            raise UserError("'%s'必须选择上级部门~" % department.name)
        if not department.parent_id.ent_wx_id:
            raise UserError("'%s'不是企业微信已存在的部门，请重新选择~" % department.name)
        return


class HrEmployee(models.Model):
    _inherit = 'hr.employee'

    ent_wx_id = fields.Char(string='企业微信用户Id')
    ent_wx_department_ids = fields.Many2many('hr.department', 'weixin_ent_department_rel', string='所属部门')
    ent_wx_avatar = fields.Html('微信头像', compute='_compute_ent_wx_avatar')
    ent_wx_avatar_url = fields.Char('微信头像链接')
    ent_wx_qr_code = fields.Html(string=u'个人二维码', compute='_compute_ent_wx_qr_code')
    ent_wx_qr_code_url = fields.Char('个人二维码链接')
    ent_ex_open_state = fields.Selection(string=u'启用状态', selection=[(1, '启用'), (0, '禁用')], default=0)
    ent_ex_alias = fields.Char(string='别名')
    ent_wx_status = fields.Selection(string=u'激活状态', selection=[(1, '已激活'), (2, '已禁用'), (4, '未激活')])
    ent_ex_user_id = fields.Many2one(comodel_name='res.users', string=u'关联系统用户')

    @api.multi
    @api.depends('ent_wx_avatar_url')
    def _compute_ent_wx_avatar(self):
        for res in self:
            if res.ent_wx_avatar_url:
                res.ent_wx_avatar = """
                <img src="{avatar_url}" style="width:100px; height=100px;">
                """.format(avatar_url=res.ent_wx_avatar_url)
            else:
                res.ent_wx_avatar = False

    @api.multi
    @api.depends('ent_wx_qr_code_url')
    def _compute_ent_wx_qr_code(self):
        for res in self:
            if res.ent_wx_qr_code_url:
                res.ent_wx_qr_code = """
                <img src="{avatar_url}" style="width:120px; height=120px;">
                """.format(avatar_url=res.ent_wx_qr_code_url)
            else:
                res.ent_wx_qr_code = False

    @api.multi
    def create_ent_weixin_employee(self):
        """
        创建企业微信员工
        :return:
        """
        url, token = self.env['weixin.ent.parameter'].get_token_and_value('user_create', 'ent_wx_ab_token')
        for res in self:
            if not res.department_id:
                raise UserError("员工'%s'必须选择部门!" % res.name)
            if not res.department_id.ent_wx_id:
                raise UserError("员工'%s'选择的部门'%s'必须已在企业微信中存在!" % (res.name, res.department_id.name))
            user_id = self.env['ir.sequence'].next_by_code('winxin.ent.employee.code')
            data = {
                'userid': user_id,
                'name': res.name,
                'alias': res.ent_ex_alias if res.ent_ex_alias else '',
                'mobile': res.mobile_phone if res.mobile_phone else '',
                'department': [res.department_id.ent_wx_id],
                'position': res.job_id.name if res.job_id else '',
                'email': res.work_email if res.work_email else '',
                'telephone': res.work_phone if res.work_phone else '',
                'enable': res.ent_ex_open_state,
                'external_position': res.job_title if res.job_title else '',
                'address': res.work_location if res.work_location else '',
            }
            # 性别
            if res.gender == 'male':
                data['gender'] = '1'
            elif res.gender == 'female':
                data['gender'] = '2'
            else:
                data['gender'] = '0'
            result = request_post(url, token, data)
            if result['errcode'] != 0:
                raise UserError(result['errmsg'])
            res.write({'ent_wx_id': user_id})
            res.message_post(body=u"员工信息已上传至企业微信", message_type='notification')

    @api.multi
    def write_ent_weixin_employee(self):
        """
        更新企业微信员工
        :return:
        """
        url, token = self.env['weixin.ent.parameter'].get_token_and_value('user_update', 'ent_wx_ab_token')
        for res in self:
            if not res.ent_wx_id:
                raise UserError("员工'%s'还没有上传到企业微信中，请先上传再修改!" % res.name)
            if not res.department_id:
                raise UserError("员工'%s'必须选择部门!" % res.name)
            if not res.department_id.ent_wx_id:
                raise UserError("员工'%s'选择的部门'%s'必须已在企业微信中存在!" % (res.name, res.department_id.name))
            data = {
                'userid': res.ent_wx_id,
                'name': res.name,
                'alias': res.ent_ex_alias if res.ent_ex_alias else '',
                'mobile': res.mobile_phone if res.mobile_phone else '',
                'department': [res.department_id.ent_wx_id],
                'position': res.job_id.name if res.job_id else '',
                'email': res.work_email if res.work_email else '',
                'telephone': res.work_phone if res.work_phone else '',
                'enable': res.ent_ex_open_state,
                'external_position': res.job_title if res.job_title else '',
                'address': res.work_location if res.work_location else '',
            }
            # 性别
            if res.gender == 'male':
                data['gender'] = '1'
            elif res.gender == 'female':
                data['gender'] = '2'
            else:
                data['gender'] = '0'
            result = request_post(url, token, data)
            if result['errcode'] != 0:
                raise UserError(result['errmsg'])
            res.message_post(body=u"员工信息在企业微信上更新", message_type='notification')

    @api.multi
    def delete_ent_weixin_employee(self):
        """
        删除企业微信员工
        :return:
        """
        url, token = self.env['weixin.ent.parameter'].get_token_and_value('user_delete', 'ent_wx_ab_token')
        for res in self:
            if not res.ent_wx_id:
                raise UserError("'%s'不是企业微信员工，请先创建或同步到企业微信！" % res.name)
            data = {'userid': res.ent_wx_id}
            result = request_get(url, token, data)
            if result['errcode'] != 0:
                raise UserError(result['errmsg'])
            res.write({
                'ent_wx_id': False,
                'ent_wx_qr_code_url': False,
                'ent_wx_avatar_url': False,
                'ent_ex_alias': False,
                'ent_ex_open_state': 0,
                'ent_wx_status': 0,
                'ent_wx_department_ids': [(2, 0, res.ent_wx_department_ids.ids)],
            })
            res.message_post(body=u"已在企业微信上清除员工", message_type='notification')

    @api.multi
    def get_ent_weixin_employee(self):
        """
        获取企业微信员工详情
        :return:
        """
        url, token = self.env['weixin.ent.parameter'].get_token_and_value('user_get', 'ent_wx_ab_token')
        for res in self:
            if not res.ent_wx_id:
                raise UserError("'%s'不是企业微信员工，请先创建或同步到企业微信！" % res.name)
            data = {'userid': res.ent_wx_id}
            result = request_get(url, token, data)
            if result['errcode'] != 0:
                raise UserError(result['errmsg'])
            data = {
                'ent_wx_id': result.get('userid'),
                'name': result.get('name'),
                'mobile_phone': result.get('mobile'),
                'work_email': result.get('email'),
                'ent_wx_avatar_url': result.get('avatar'),
                'ent_wx_qr_code_url': result.get('qr_code'),
                'work_phone': result.get('telephone'),
                'ent_ex_open_state': result.get('enable'),
                'ent_ex_alias': result.get('alias'),
                'ent_wx_status': result.get('status'),
                'job_title': result.get('external_position'),
                'work_location': result.get('address'),
            }
            # 查询部门列表
            dept_ids = list()
            for dept in result.get('department'):
                department = self.env['hr.department'].search([('ent_wx_id', '=', dept)], limit=1)
                dept_ids.append(department.id)
            data['department_id'] = dept_ids[0] if dept_ids else False
            data['ent_wx_department_ids'] = [(6, 0, dept_ids)]
            # 职位
            hr_job = self.env['hr.job'].search([('name', '=', result.get('position'))])
            if not hr_job:
                hr_job = self.env['hr.job'].sudo().create({'name': result.get('position')})
            data['job_id'] = hr_job.id
            # 性别
            if result.get('gender') == '1':
                data['gender'] = 'male'
            elif result.get('gender') == '2':
                data['gender'] = 'female'
            else:
                data['gender'] = 'other'
            res.write(data)
            res.message_post(body=u"已从企业微信中获取信息！", message_type='notification')

    @api.constrains('user_id')
    def _constrains_user_id(self):
        """
        当相关用户字段发生改变时同步至关联系统用户字段
        :return:
        """
        for res in self:
            if res.user_id:
                res.ent_ex_user_id = res.user_id

    @api.constrains('ent_ex_user_id')
    def _constrains_ent_ex_user_id(self):
        """
        同步关联系统用户字段到系统用户res.users表中，用户oauth字段标识
        :return:
        """
        for res in self:
            if res.ent_ex_user_id:
                # 先把原来的id清空
                sql = """UPDATE res_users SET wx_ent_user_id='' WHERE wx_ent_user_id='{}'""".format(res.ent_wx_id)
                self._cr.execute(sql)
                sql = """UPDATE res_users SET wx_ent_user_id='{}' WHERE id={}""".format(res.ent_wx_id, res.ent_ex_user_id.id)
                _logger.info(sql)
                self._cr.execute(sql)


class EmployeeTags(models.Model):
    _description = "成员标签管理"
    _name = 'hr.employee.tags'
    _order = 'id'
    _inherit = ['mail.thread', 'mail.activity.mixin']

    active = fields.Boolean(default=True)
    name = fields.Char(string='标签名称', index=True, required=True)
    api_state = fields.Boolean(string=u'同步状态', default=True)
    wx_ent_id = fields.Char(string='企业微信标签Id', index=True)
    employee_ids = fields.Many2many('hr.employee', string=u'标签成员')
    department_ids = fields.Many2many('hr.department', string=u'标签部门')

    @api.model
    def create(self, values):
        """
        创建时将标签自动推送到企业微信
        :param values:
        :return:
        """
        if 'api_state' not in values or values['api_state']:
            try:
                client = WeChatTag(app_client('ent_wx_ab_secret'))
                result = client.create(values.get('name'))
            except Exception as e:
                raise UserError(str(e))
            if result['errcode'] != 0:
                raise UserError(result['errmsg'])
            values['wx_ent_id'] = result['tagid']
        values['api_state'] = True
        return super(EmployeeTags, self).create(values)

    @api.multi
    def unlink(self):
        """
        删除标签时同时删除企业微信中的标签
        :return:
        """
        for res in self:
            if res.wx_ent_id:
                try:
                    client = WeChatTag(app_client('ent_wx_ab_secret'))
                    result = client.delete(res.wx_ent_id)
                except Exception as e:
                    raise UserError(str(e))
                if result['errcode'] != 0:
                    raise UserError(result['errmsg'])
            super(EmployeeTags, self).unlink()

    @api.multi
    def update_weixin_ent_tags(self):
        """
        更新标签纸企业微信
        :return:
        """
        for res in self:
            try:
                client = WeChatTag(app_client('ent_wx_ab_secret'))
                result = client.update(res.wx_ent_id, res.name)
            except Exception as e:
                raise UserError(str(e))
            if result['errcode'] != 0:
                raise UserError(result['errmsg'])
            res.message_post(body=u"已更新至企业微信中！", message_type='notification')

    @api.multi
    def get_tags_users(self):
        """
        获取标签成员列表
        :return:
        """
        for res in self:
            user_list = []
            dept_list = []
            try:
                client = WeChatTag(app_client('ent_wx_ab_secret'))
                result = client.get_users(res.wx_ent_id)
            except Exception as e:
                raise UserError(str(e))
            if result['errcode'] != 0:
                raise UserError(result['errmsg'])
            for user in result['userlist']:
                emp = self.env['hr.employee'].search([('ent_wx_id', '=', user.get('userid'))], limit=1)
                if emp:
                    user_list.append(emp.id)
            for party in result['partylist']:
                dept = self.env['hr.department'].search([('ent_wx_id', '=', party)], limit=1)
                if dept:
                    dept_list.append(dept.id)
            res.write({'employee_ids': [(6, 0, user_list)], 'department_ids': [(6, 0, dept_list)]})
            res.message_post(body=u"已成功获取{}条成员信息和{}条部门信息！".format(len(user_list), len(dept_list)), message_type='notification')


