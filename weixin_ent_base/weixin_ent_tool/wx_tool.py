# -*- coding: utf-8 -*-
###################################################################################
#    Copyright (C) 2019 SuXueFeng  License GNU
###################################################################################
import base64
import hashlib
import json
import logging
import time
import requests
from requests import ReadTimeout, ConnectTimeout
from odoo import api, models, fields
from wechatpy.enterprise import WeChatClient
_logger = logging.getLogger(__name__)


def get_client(corp_id, secret):
    """
    :param corp_id: 企业微信公司Id
    :param secret: 对应的秘钥（比如通讯录、自建应用...）
    :return: 企业微信客户端实例
    """
    return WeChatClient(corp_id, secret)


def request_get(url, token, data=None, timeout=None):
    """
    get请求
    :param url: url
    :param token:  token
    :param data:  dict
    :param timeout: time
    :return:
    """
    timeout = 5 if not timeout else timeout
    if not data:
        data = []
    try:
        result = requests.get(url="{}{}".format(url, token), params=data, timeout=timeout)
        return json.loads(result.text)
    except Exception as e:
        return {"errcode": 'Exception', 'errmsg': str(e)}


def request_post(url, token, data=None, timeout=None):
    """
    post请求
    :param url:
    :param token:
    :param data:
    :param timeout:
    :return:
    """
    headers = {'Content-Type': 'application/json'}
    timeout = 5 if not timeout else timeout
    if not data:
        data = {}
    try:
        result = requests.post(url="{}{}".format(url, token), headers=headers, data=json.dumps(data, 'utf8'), timeout=timeout)
        return json.loads(result.text)
    except ReadTimeout as e:
        logging.info(">>>Exception: 网络连接超时！")
        return {"errcode": 'ReadTimeout', 'errmsg': "网络连接超时!"}
    except Exception as e:
        return {"errcode": 'Exception', 'errmsg': str(e)}


class WeiXinEntTools(models.TransientModel):
    _description = '企业微信工具'
    _name = 'weixin.ent.tools'

    @api.model
    def get_weixin_ent_token(self):
        """
        获取token值
        :return:
        """
        _logger.info("执行获取Token任务")
        url = self.env['weixin.ent.parameter'].get_parameter_value('get_token')
        ent_wx_corp_id = self.env['ir.config_parameter'].sudo().get_param('weixin_ent_base.ent_wx_corp_id')
        # 获取自建应用token
        secret = self.env['ir.config_parameter'].sudo().get_param('weixin_ent_base.ent_wx_secret')
        data = {'corpid': ent_wx_corp_id, 'corpsecret': secret}
        access_token = self._get_request_token(url, data)
        token = self.env['weixin.ent.parameter'].search([('key', '=', 'token')], limit=1)
        if token:
            token.write({'value': access_token})
        # 通讯录Token
        secret = self.env['ir.config_parameter'].sudo().get_param('weixin_ent_base.ent_wx_ab_secret')
        data = {'corpid': ent_wx_corp_id, 'corpsecret': secret}
        access_token = self._get_request_token(url, data)
        token = self.env['weixin.ent.parameter'].search([('key', '=', 'ent_wx_ab_token')], limit=1)
        if token:
            token.write({'value': access_token})
        _logger.info("结束获取Token任务")

    @api.model
    def _get_request_token(self, url, data):
        # 发送数据
        result = requests.get(url=url, params=data, timeout=5)
        result = json.loads(result.text)
        _logger.info(">>>Token: {}".format(result))
        if result.get('errcode') == 0:
            return result['access_token']
        else:
            return '0000'

