# -*- coding: utf-8 -*-
###################################################################################
#    Copyright (C) 2019 SuXueFeng License GNU
###################################################################################
from odoo import api, fields, models


class ExternaLcontact(models.Model):
    _description = '联系人'
    _name = 'ent.external.contact'
    _order = 'id'
    _inherit = ['mail.thread', 'mail.activity.mixin']

    active = fields.Boolean('Active', default=True)
    name = fields.Char(string='名称', index=True)
    user_id = fields.Char(string='UserId', index=True)
    avatar = fields.Html('头像', compute='_compute_avatar')
    avatar_url = fields.Char('头像链接')
    user_type = fields.Selection(string=u'类型', selection=[(1, '微信用户'), (2, '企业微信用户')], default=2, index=True)
    gender = fields.Selection(string=u'性别', selection=[(1, '男性'), (2, '女性'), (0, '未知')], default=1)
    unionid = fields.Char(string='微信Unionid', index=True)
    position = fields.Char(string='职位')
    corp_name = fields.Char(string='企业简称')
    corp_full_name = fields.Char(string='企业主体名称')
    follow_ids = fields.One2many(comodel_name='external.contact.follow', inverse_name='external_id', string=u'企业成员')

    @api.multi
    @api.depends('avatar_url')
    def _compute_avatar(self):
        for res in self:
            if res.avatar_url:
                res.avatar = """
                <img src="{avatar_url}" style="width:100px; height=100px;">
                """.format(avatar_url=res.avatar_url)
            else:
                res.avatar = False


class ExternaLcontactFollowUser(models.Model):
    _description = '企业成员'
    _name = 'external.contact.follow'
    _rec_name = 'external_id'
    _order = 'id'

    external_id = fields.Many2one(comodel_name='ent.external.contact', string=u'联系人')
    ent_user_id = fields.Many2one(comodel_name='hr.employee', string=u'企业成员')
    user_remark = fields.Text(string='联系人备注')
    user_description = fields.Text(string='联系人描述')
    user_createtime = fields.Date(string=u'添加时间')
    tags_group_name = fields.Char(string='标签分组名称')
    tag_name = fields.Char(string='标签名称')
    tags_type = fields.Selection(string=u'标签类型', selection=[(1, '企业设置'), (2, '用户自定义'), ], default=1)
    remark_corp_name = fields.Char(string='备注企业名称')
    remark_mobiles = fields.Char(string='手机号码')
    externa_state = fields.Char(string='客户渠道')