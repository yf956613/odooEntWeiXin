# -*- coding: utf-8 -*-
###################################################################################
#    Copyright (C) 2019 SuXueFeng License GNU
###################################################################################
from odoo import api, fields, models


class WeiXinEntParameter(models.Model):
    _description = '企业微信系统参数'
    _name = 'weixin.ent.parameter'

    name = fields.Char(string='名称')
    key = fields.Char(string='key值', index=True)
    value = fields.Char(string='参数值')

    _sql_constraints = [
        ('key_uniq', 'unique(key)', u'系统参数中key值不允许重复!'),
    ]

    @api.model
    def get_parameter_value(self, key):
        """
        根据key获取对应的value
        :param key: string
        :return:
        """
        parameter = self.search([('key', '=', key)])
        return parameter.value if parameter and parameter.value else False

    @api.model
    def get_token_and_value(self, key, token_type):
        token_type = self.search([('key', '=', token_type)]).value
        parameter = self.get_parameter_value(key)
        return parameter, token_type