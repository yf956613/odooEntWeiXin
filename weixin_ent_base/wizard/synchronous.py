# -*- coding: utf-8 -*-
###################################################################################
#    Copyright (C) 2019 SuXueFeng
###################################################################################
import logging
from odoo import api, fields, models, tools
from odoo.exceptions import UserError
from odoo.addons.weixin_ent_base.weixin_ent_tool.wx_tool import request_get, request_post

_logger = logging.getLogger(__name__)


class WeiXinEntSynchronous(models.TransientModel):
    _name = 'weixin.ent.data.synchronous'
    _description = "通讯录同步"
    _rec_name = 'employee'

    department = fields.Boolean(string=u'企业微信部门', default=True)
    dept_processing = fields.Selection(string=u'部门重名处理', selection=[('replace', '替换'), ('ignore', '忽略')], default='ignore')
    employee = fields.Boolean(string=u'部门成员详情', default=True)
    emp_processing = fields.Selection(string=u'成员重名处理', selection=[('replace', '替换'), ('ignore', '忽略')], default='ignore')

    @api.multi
    def start_synchronous_data(self):
        """
        通讯录同步
        :return:
        """
        self.ensure_one()
        try:
            if self.department:
                self.synchronous_weixin_ent_department(self.dept_processing)
            if self.employee:
                self.synchronous_weixin_ent_employee(self.emp_processing)
        except Exception as e:
            raise UserError(e)

    @api.model
    def synchronous_weixin_ent_department(self, dept_processing):
        """
        同步企业微信部门
        :param dept_processing:
        :return:
        """
        _logger.info("开始获取企业微信部门列表")
        url, token = self.env['weixin.ent.parameter'].get_token_and_value('department_list', 'ent_wx_ab_token')
        result = request_get(url, token)
        if result['errcode'] != 0:
            raise UserError(result['errmsg'])
        for res_dept in result['department']:
            data = {
                'name': res_dept['name'],
                'ent_wx_id': res_dept['id'],
            }
            department = self.env['hr.department'].search([('ent_wx_id', '=', res_dept['id'])], limit=1)
            # 判断是否选择替换
            if dept_processing == 'replace':
                department = self.env['hr.department'].search([('name', '=', res_dept['name'])], limit=1)
            if not department:
                self.env['hr.department'].sudo().create(data)
            else:
                department.sudo().write(data)
        # 再遍历一次，修改上级部门
        for res_dept in result['department']:
            if res_dept['parentid'] != 0:
                department = self.env['hr.department'].sudo().search([('ent_wx_id', '=', res_dept['id'])], limit=1)
                partner_dept = self.env['hr.department'].search([('ent_wx_id', '=', res_dept['parentid'])])
                self._cr.execute("UPDATE hr_department SET parent_id=%s WHERE id=%s" % (partner_dept.id, department.id))
        _logger.info("结束获取企业微信部门列表")
        return True

    @api.model
    def synchronous_weixin_ent_employee(self, emp_processing):
        """
        获取部门成员详情
        :param emp_processing:
        :return:
        """
        _logger.info("获取部门成员详情")
        # 获取所有部门
        departments = self.env['hr.department'].sudo().search([('ent_wx_id', '!=', ''), ('active', '=', True)])
        url, token = self.env['weixin.ent.parameter'].get_token_and_value('user_list', 'ent_wx_ab_token')
        for department in departments:
            data = {'department_id': department.ent_wx_id, 'fetch_child': 0}
            result = request_get(url, token, data)
            if result['errcode'] != 0:
                raise UserError(result['errmsg'])
            for user in result['userlist']:
                data = {
                    'ent_wx_id': user.get('userid'),
                    'name': user.get('name'),
                    'mobile_phone': user.get('mobile'),
                    'work_email': user.get('email'),
                    'ent_wx_avatar_url': user.get('avatar'),
                    'ent_wx_qr_code_url': user.get('qr_code'),
                    'work_phone': user.get('telephone'),
                    'ent_ex_open_state': user.get('enable'),
                    'ent_ex_alias': user.get('alias'),
                    'ent_wx_status': user.get('status'),
                    'job_title': user.get('external_position'),
                    'work_location': user.get('address'),
                }
                # 查询部门列表
                dept_ids = list()
                for dept in user.get('department'):
                    department = self.env['hr.department'].search([('ent_wx_id', '=', dept)], limit=1)
                    dept_ids.append(department.id)
                data['department_id'] = dept_ids[0] if dept_ids else False
                data['ent_wx_department_ids'] = [(6, 0, dept_ids)]
                # 职位
                hr_job = self.env['hr.job'].search([('name', '=', user.get('position'))])
                if not hr_job:
                    hr_job = self.env['hr.job'].sudo().create({'name': user.get('position')})
                data['job_id'] = hr_job.id
                # 性别
                if user.get('gender') == '1':
                    data['gender'] = 'male'
                elif user.get('gender') == '2':
                    data['gender'] = 'female'
                else:
                    data['gender'] = 'other'
                employee = self.env['hr.employee'].search([('ent_wx_id', '=', user.get('userid'))])
                # 是否替换系统原有成员
                if emp_processing == 'replace':
                    employee = self.env['hr.employee'].search([('name', '=', user.get('name'))])
                if employee:
                    employee.sudo().write(data)
                else:
                    self.env['hr.employee'].create(data)
        _logger.info("获取部门成员详情结束")
        return
