# -*- coding: utf-8 -*-
###################################################################################
#    Copyright (C) 2019 SuXueFeng License（GNU）
###################################################################################
{
    'name': "企业微信集成应用",
    'summary': """管理员可以使用这些API，为企业接入更多个性化的办公应用""",
    'description': """管理员可以使用这些API，为企业接入更多个性化的办公应用""",
    'author': "SuXueFeng",
    'website': "https://www.sxfblog.com",
    'category': 'weixin',
    'version': '1.0',
    'depends': ['base', 'hr', 'contacts', 'auth_oauth', 'mail'],
    'installable': True,
    'application': True,
    'auto_install': False,
    'data': [
        'security/weixin_security.xml',
        'security/ir.model.access.csv',
        'data/system_parameter.xml',
        'data/default_num.xml',
        'data/auth_oauth.xml',

        'views/assets.xml',
        'wizard/synchronous.xml',
        'wizard/hr_employee_tags.xml',

        'views/res_config_settings_views.xml',
        'views/system_parameter.xml',
        'views/weixin_ent_hr.xml',
        'views/res_users_views.xml',
        'views/oauth_templates.xml',


    ],
    'qweb': [
        'static/xml/*.xml'
    ]
}
