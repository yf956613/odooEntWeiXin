# -*- coding: utf-8 -*-
###################################################################################
#    Copyright (C) 2019 SuXueFeng License GNU
###################################################################################
import logging
from werkzeug.exceptions import BadRequest
from odoo import SUPERUSER_ID, api, http, _
from odoo import registry as registry_get
from odoo.addons.auth_oauth.controllers.main import OAuthLogin as Home
from odoo.addons.web.controllers.main import (login_and_redirect, ensure_db, set_cookie_and_redirect)
from odoo.http import request
from odoo.addons.weixin_ent_base.weixin_ent_tool.wx_tool import request_get

_logger = logging.getLogger(__name__)


class WeiXinEntLogin(Home, http.Controller):

    @http.route('/web/xinwei/ent/login', type='http', auth='public', website=True, sitemap=False)
    def web_weixin_ent_login(self, *args, **kw):
        """
        主页点击扫码登录将重定向到微信扫码授权页
        :param args:
        :param kw:
        :return:
        """
        corp_id = request.env['ir.config_parameter'].sudo().get_param('weixin_ent_base.ent_wx_corp_id')
        agentid = request.env['ir.config_parameter'].sudo().get_param('weixin_ent_base.ent_wx_agent_id')
        redirct_url = "{}web/weixin/ent/login/action".format(request.httprequest.host_url)
        url = """https://open.work.weixin.qq.com/wwopen/sso/qrConnect?appid={corp_id}&agentid={agentid}&redirect_uri={redirct_url}&state={state}""".format(
            corp_id=corp_id, agentid=agentid, redirct_url=redirct_url, state='odooerp')
        return http.redirect_with_hash(url)

    @http.route('/web/weixin/ent/login/action', type='http', auth="none")
    def web_action_weixin_ent_login_action(self, redirect=None, **kw):
        """
        扫码回调处理
        :param redirect:
        :param kw:
        :return:
        """
        code = request.params['code']
        state = request.params['state']
        _logger.info(">>>code：{}".format(code))
        url = "https://qyapi.weixin.qq.com/cgi-bin/user/getuserinfo?access_token="
        token = request.env['weixin.ent.parameter'].sudo().get_parameter_value('token')
        result = request_get(url, token, {'code': code})
        # 扫码失败
        if result['errcode'] != 0:
            return http.redirect_with_hash('/web')
        # 非企业成员直接返回到主界面
        if not result.get('UserId'):
            return http.redirect_with_hash('/web')
        # 成员UserID
        employee = request.env['hr.employee'].sudo().search([('ent_wx_id', '=', result['UserId'])], limit=1)
        # 没有关联系统用户时返回到主界面
        if not employee.user_id:
            return http.redirect_with_hash('/web')
        # 校验成功进行登录
        return self._wxent_do_post_login(employee.ent_wx_id, redirect)

    def _wxent_do_post_login(self, user_id, redirect):
        """
        所有的验证都结束并正确后，需要界面跳转到主界面
        :param user_id:  user_id
        :param redirect:
        :return:
        """
        ensure_db()
        dbname = request.session.db
        if not http.db_filter([dbname]):
            return BadRequest()
        context = {}
        registry = registry_get(dbname)
        with registry.cursor() as cr:
            try:
                env = api.Environment(cr, SUPERUSER_ID, context)
                credentials = env['res.users'].sudo().auth_oauth_weixin_ent("weixin_ent", user_id)
                cr.commit()
                url = '/web' if not redirect else redirect
                uid = request.session.authenticate(*credentials)
                if uid:
                    return http.redirect_with_hash(url)
                else:
                    self._do_err_redirect("登录失败")
            except Exception as e:
                self._do_err_redirect("登录失败,原因为:{}".format(str(e)))

    def _do_err_redirect(self, errmsg):
        """
        :param errmsg: 需要返回展示的信息
        :return:
        """
        values = request.params.copy()
        values['error'] = _(errmsg)
        http.redirect_with_hash('/web/login')
        response = request.render('web.login', values)
        return response
