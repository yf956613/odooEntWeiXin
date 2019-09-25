# -*- coding: utf-8 -*-
###################################################################################
#    Copyright (C) 2019 SuXueFeng License GNU
###################################################################################
import logging
from odoo import api, fields, models
from odoo.exceptions import AccessDenied

_logger = logging.getLogger(__name__)


class ResUsers(models.Model):
    _name = 'res.users'
    _inherit = ['res.users']

    wx_ent_user_id = fields.Char(string='企业微信UserId', index=True)

    @api.model
    def auth_oauth_weixin_ent(self, provide_id, oauth_uid):
        _logger.info("oauth_uid: %s", oauth_uid)
        if provide_id == 'weixin_ent':
            user = self.sudo().search([('wx_ent_user_id', '=', oauth_uid)])
        else:
            user = self.sudo().search([('oauth_provider_id', '=', provide_id), ('oauth_uid', '=', oauth_uid)])
        _logger.info("user: %s", user.login)
        if not user or len(user) > 1:
            return AccessDenied
        return (self.env.cr.dbname, user[0].login, oauth_uid)

    @api.model
    def _check_credentials(self, password):
        try:
            return super(ResUsers, self)._check_credentials(password)
        except AccessDenied:
            res = self.sudo().search([('id', '=', self.env.uid), ('wx_ent_user_id', '=', password)])
            if not res:
                raise