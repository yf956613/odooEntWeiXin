# -*- coding: utf-8 -*-
###################################################################################
#    Copyright (C) 2019 SuXueFeng  License GNU
###################################################################################
import json
import logging
import time

import requests
from requests import ReadTimeout
from odoo import api, models
from wechatpy.enterprise import WeChatClient
from wechatpy.session.memorystorage import MemoryStorage
from odoo.http import request

mem_storage = MemoryStorage()
_logger = logging.getLogger(__name__)


def app_client(secret_str):
    """
    根据应用的secret返回一个客户端实例，用于调取实例函数
    :param secret_str: 应用secret
    :return: 企业微信客户端实例
    """
    secret_str = 'weixin_ent_base.{}'.format(secret_str)
    corp_id = request.env['ir.config_parameter'].sudo().get_param('weixin_ent_base.ent_wx_corp_id')
    secret = request.env['ir.config_parameter'].sudo().get_param(secret_str)
    return WeChatClient(corp_id, secret, session=mem_storage)


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


def time_stamp(time_num):
    """
    将10位时间戳转换为时间(utc=0)
    :param time_num: 10位时间戳
    :return: "%Y-%m-%d"
    """
    time_array = time.gmtime(time_num)
    return time.strftime("%Y-%m-%d", time_array)


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

