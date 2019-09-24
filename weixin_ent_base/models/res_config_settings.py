# -*- coding: utf-8 -*-
###################################################################################
#    Copyright (C) 2019 SuXueFeng License(GNU)
###################################################################################
from odoo import fields, models


class ResConfigSettings(models.TransientModel):
    _inherit = 'res.config.settings'

    ent_wx_corp_id = fields.Char(string=u'企业微信CorpId')
    ent_wx_token = fields.Boolean(string="自动获取Token")
    # ------自建应用--------------
    ent_wx_agent_id = fields.Char(string=u'自建应用AgentId')
    ent_wx_secret = fields.Char(string=u'自建应用Secret')
    # ------通讯录--------------
    ent_wx_ab_secret = fields.Char(string='通讯录Secret')

    def get_values(self):
        res = super(ResConfigSettings, self).get_values()
        res.update(
            ent_wx_corp_id=self.env['ir.config_parameter'].sudo().get_param('weixin_ent_base.ent_wx_corp_id'),
            ent_wx_agent_id=self.env['ir.config_parameter'].sudo().get_param('weixin_ent_base.ent_wx_agent_id'),
            ent_wx_secret=self.env['ir.config_parameter'].sudo().get_param('weixin_ent_base.ent_wx_secret'),
            ent_wx_token=self.env['ir.config_parameter'].sudo().get_param('weixin_ent_base.ent_wx_token'),
            ent_wx_ab_secret=self.env['ir.config_parameter'].sudo().get_param('weixin_ent_base.ent_wx_ab_secret'),
        )
        return res

    def set_values(self):
        super(ResConfigSettings, self).set_values()
        self.env['ir.config_parameter'].sudo().set_param('weixin_ent_base.ent_wx_corp_id', self.ent_wx_corp_id)
        self.env['ir.config_parameter'].sudo().set_param('weixin_ent_base.ent_wx_agent_id', self.ent_wx_agent_id)
        self.env['ir.config_parameter'].sudo().set_param('weixin_ent_base.ent_wx_secret', self.ent_wx_secret)
        self.env['ir.config_parameter'].sudo().set_param('weixin_ent_base.ent_wx_token', self.ent_wx_token)
        self.env['ir.config_parameter'].sudo().set_param('weixin_ent_base.ent_wx_ab_secret', self.ent_wx_ab_secret)

    def get_weixin_ent_token(self):
        self.env.ref('weixin_ent_base.get_ent_weixin_token_ir_cron').method_direct_trigger()
