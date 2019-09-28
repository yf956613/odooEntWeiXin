# -*- coding: utf-8 -*-
###################################################################################
#    Copyright (C) 2019 SuXueFeng
###################################################################################
import logging
from wechatpy.enterprise.client.api import WeChatExternalContact
from odoo import api, fields, models
from odoo.exceptions import UserError
from odoo.addons.weixin_ent_base.weixin_ent_tool.wx_tool import app_client, time_stamp
_logger = logging.getLogger(__name__)


class ExternaLcontactTran(models.TransientModel):
    _description = "获取联系人列表"
    _name = 'ent.external.contact.tran'

    employee_id = fields.Many2one(comodel_name='hr.employee', string=u'企业成员',
                                  required=True, domain=[('ent_wx_id', '!=', '')])
    is_info = fields.Boolean(string=u'是否获取详情', default=True)

    @api.multi
    def pull_externa_list(self):
        """
        获取联系人列表
        :return:
        """
        try:
            client = WeChatExternalContact(app_client('ent_wx_el_secret'))
            result = client.list(self.employee_id.ent_wx_id)
        except Exception as e:
            raise UserError(str(e))
        if result['errcode'] != 0:
            raise UserError(result['errmsg'])
        if self.is_info:
            for userid in result['external_userid']:
                ex_result = client.get(userid)
                if ex_result['errcode'] != 0:
                    raise UserError(ex_result['errmsg'])
                external_contact = ex_result['external_contact']
                data = {
                    'name': external_contact.get('name'),
                    'user_id': external_contact.get('external_userid'),
                    'avatar_url': external_contact.get('avatar'),
                    'user_type': external_contact.get('type'),
                    'gender': external_contact.get('gender'),
                    'unionid': external_contact.get('unionid'),
                    'position': external_contact.get('position'),
                    'corp_name': external_contact.get('corp_name'),
                    'corp_full_name': external_contact.get('corp_full_name'),
                }
                follow_list = list()
                for follow_user in ex_result['follow_user']:
                    employee = self.env['hr.employee'].search([('ent_wx_id', '=', follow_user.get('userid'))], limit=1)
                    follow_list.append((0, 0, {
                        'ent_user_id': employee.id if employee else False,
                        'user_remark': follow_user.get('remark'),
                        'user_description': follow_user.get('description'),
                        'remark_corp_name': follow_user.get('remark_corp_name'),
                        'remark_mobiles': str(follow_user.get('remark_mobiles')),
                        'externa_state': follow_user.get('state'),
                        'user_createtime': time_stamp(follow_user.get('createtime')),
                    }))
                data.update({'follow_ids': follow_list})
                externals = self.env['ent.external.contact'].search([('user_id', '=', external_contact.get('external_userid'))], limit=1)
                if externals:
                    externals.write({'follow_ids': [(2, externals.follow_ids.ids)]})
                    externals.sudo().write(data)
                else:
                    self.env['ent.external.contact'].create(data)
        return {'type': 'ir.actions.act_window_close'}
