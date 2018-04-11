#!/usr/bin/python
# -*- coding: utf-8 -*-
'''
Created on 2017-04-06 18:30:09

@author: Maxing
'''

import requests
from requests.exceptions import ConnectionError
import time
import os
import sys
import json
import codecs
import logging
import copy
from utils import save_items, get_items_from_file, add_item_fields, log_init, save_items_with_json

reload(sys)
sys.setdefaultencoding('utf8')

# 易码(www.51ym.me)
# 账号/密码: kkk123456(kkk123456)
# 登录后, token有效期为10分钟, 过期需要重新申请token
# 平台接口前缀: 'http://api.ltxin.com:8888'
'''
账户基本信息
account_info = {
    'user_info': {
        u'用户名': 'kkk123456',
        u'用户类别': '',
        u'可同时登陆': '',
        u'可同时获取号码数': '10',
        u'单个客户端获取号码数': '',
        u'折扣': '100%',        
        u'用户余额': '5.000',
        u'可提现余额': '0.000',
        u'积分': '5.00',
        u'真实姓名': '',
        u'支付宝': '',
        u'电子邮箱': '1747485592@qq.com',
        u'手机号码': '18926779675',
        u'QQ': '174748559',
        u'注册日期': '',
    }

}
'''

# API前缀
API_PREFIX = r'http://api.51ym.me/UserInterface.aspx'

# 保存网站项目信息的文件
ITEMS_FILE = os.path.sep.join([sys.path[0], 'items', 'yima_items.json'])

# 保存最终获得的手机号码信息保存文件
current_date = time.strftime('%Y-%m-%d', time.localtime(time.time()))
PHONE_FILE = os.path.sep.join([sys.path[0], 'data', 'yima_phone_%s.txt' % (current_date)])

# LOG
month = time.strftime('%Y-%m', time.localtime(time.time()))
LOG_FILE = os.path.sep.join([sys.path[0], 'log', 'yima_%s.log' % month])

# 从客户端提取的 项目列表url
# http://apii.51ym.me:8088/UserInterface.aspx?action=itemseach&itemname={itemname}&token={token}
ITEM_URL = r'http://apii.51ym.me:8088/UserInterface.aspx'


class Yima(object):
    def __init__(self):
        self.item_url = ITEM_URL
        self.api_prefix = API_PREFIX
        self.user_name = 'kkk123456'
        self.user_pwd = 'kkk123456'
        self.token = ''
        self.headers = {
            'Host': 'api.51ym.me',
            'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1',
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/56.0.2924.87 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Accept-Encoding': 'gzip, deflate, sdch',
            'Accept-Language': 'zh-CN,zh;q=0.8,en-US;q=0.6,en;q=0.4',
        }

        save_items([], PHONE_FILE)
        log_name = self.__class__.__name__
        log_init(log_name, LOG_FILE)
        self.logger = logging.getLogger(log_name)
        self.logger.info(u'开始采集' + '-' * 30)

    # 统一处理请求部分
    def request(self, request_type, url, payload=None, headers={}):
        # request_type: 请求类型
        # url: 请求地址
        # payload: 请求参数

        retry_time = 0
        while 1:
            try:
                if request_type == 'post':
                    r = requests.post(url=url, headers=headers, data=payload, allow_redirects=False)
                elif request_type == 'get':
                    r = requests.get(url=url, headers=headers, params=payload, allow_redirects=False)
                r.encoding = 'gb2312'

                # 情况1, get_phone出错: False:Session 过期
                # # 情况2, getItem出错: False:余额不足，请先释放号码
                if 'success' not in r.text:
                    if retry_time < 3:
                        retry_time += 1
                        self.logger.info(r.text + u'\t重试中。。。')
                    else:
                        return r.text

                # set_cookies = r.headers.get('Set-Cookie')
                # if set_cookies:
                #     cfduid_str = re.search(r'__cfduid=[\S]{43}', set_cookies)
                #     if cfduid_str:
                #         self.cookies['cfduid'] = cfduid_str.group(0).split('=')[1]

                if r.status_code == 200 and 'success' in r.text:
                    return r.text
                elif r.status_code == 504:
                    time.sleep(5)
                    self.logger.info(r.status_code + u'\t网关超时, 休眠5秒。')

                # 第三种情况，获取项目列表
                if r.status_code == 200 and 'ID' in r.text:
                    return r.content
                else:
                    return

            except ConnectionError:
                self.logger.info(u'被对方服务器主动拒绝, 暂停30S。')
                time.sleep(30)
            except Exception, e:
                self.logger.info(e)
                return

    # 登录, 获得用户token
    def login(self):
        payload = {
            'action': 'login',
            'username': self.user_name,
            'password': self.user_pwd,
        }

        url = self.api_prefix
        token_text = self.request('get', url, payload, headers=self.headers)
        if token_text and 'success' in token_text:
            self.token = token_text.strip().split('|')[1]
            if self.token != '':
                self.logger.info(u'登录成功！')
        else:
            self.logger.info(u'登录失败！')

    # 获取项目
    def get_items(self):
        # 返回格式
        # [{项目ID&项目名称&项目价格&项目类型\n...},+]
        # 项目类型:
        #   1. 表示此项目用于接收验证码
        #   2. 表示此项目用户发送短信
        #   3. 表示此项目即可接收验证码，也可以发送短信
        #   4. 表示可以接受多个验证码

        # 因为项目列表的地址跟该平台提供的 API 地址的服务器不一样，所以需要额外修改一下headers
        for_items_headers = copy.deepcopy(self.headers)
        for_items_headers['Host'] = "apii.51ym.me:8088"

        # 因为没有获取所有项目，所以需要自己添加关键字以搜索
        keywords = ['借', '贷', '融', '赚']
        items = []
        items_id = set()

        for keywords in keywords:
            payload = {
                'action': 'itemseach',
                'itemname': keywords,
                'token': self.token,
            }

            item_text = self.request('get', self.item_url, payload=payload, headers=for_items_headers)
            if item_text:
                items_json = json.loads(item_text)

                for item in items_json:
                    if item['ID'] not in items_id:

                        item_dict = dict(zip(
                            ['item_id', 'item_name', 'item_price', 'item_type'],
                            [item['ID'], item['ItemName'], item['Price'], item['ItemType']]))
                        item_type = item_dict.get('item_type')

                        if item_type and item_type in [1, 3, 4]:
                            items.append(item_dict)
                            items_id.add(item['ID'])
        return items

    # 获取号码
    def get_phone(self, item_id, count=1, phone=''):
        # token: 用户登录时获取的token
        # item_id: 项目ID
        # count: 获取手机号的数量

        payload = {
            'action': 'getmobile',
            'token': self.token,  # 登录token   必填
            'itemid': item_id,  # 项目代码    必填
            # 'country': '',        # 国家代码(中国-1, 美国-2)
            # 'province': '',       # 省代码
            # 'city': '',           # 市代码
            # 'isp': '',            # 运营商代码
            'mobile': phone,  # 指定手机号
            # 'excludeno': '',      # 排除号段(如:不获取170和188号段的号码，则设置为excludeno=170|180。)
        }
        url = self.api_prefix
        num_text = self.request('get', url, payload, headers=self.headers)
        nums = []
        if num_text:
            if 'success' not in num_text:
                self.login()
            else:
                nums = [num_text.strip().split('|')[1]]
        return nums

    # 释放号码
    def release_phone(self, phone, item_id):
        url = self.api_prefix
        payload = {
            'action': 'release',
            'token': self.token,
            'itemid': item_id,
            'mobile': phone,
        }
        text = self.request('get', url, payload, headers=self.headers)
        if 'success' in text:
            self.logger.info(u'释放号码成功！')

    # 退出
    def exit(self):
        url = self.api_prefix
        payload = {
            'action': 'logout',
            'token': self.token
        }
        text = self.request('get', url, payload, headers=self.headers)
        if text == 'success':
            self.logger.info(u'退出成功！')


def main():
    yima = Yima()
    yima.login()

    if os.path.exists(ITEMS_FILE):
        items = get_items_from_file(ITEMS_FILE)
        yima.logger.info(u'从文件中读取__%s__网站可接收验证码项目%d个。' % (
            str(yima.__class__).split('.')[1].strip("'>"), len(items)))
    else:
        items = yima.get_items()
        save_items_with_json(items, ITEMS_FILE)
        yima.logger.info(u'一共获取__%s__网站可接收验证码项目%d个。' % (
            str(yima.__class__).split('.')[1].strip("'>"), len(items)))

    for item in items:
        max_time_per_item = 1000
        retry_time_per_item = 0
        phones_per_item_set = set()

        increase_length = 0

        saved_count = 0         # 目前该 item 已保存的手机号码 的数量
        replicate_count = 0     # 该 item 取得的 手机号码 的重复次数
        empty_count = 0         # 该 item 无返回 手机号码 的次数

        while 1:
            if replicate_count > 15 or retry_time_per_item >= max_time_per_item or empty_count >= 10:
                break

            item_name = item.get('item_name')
            item_id = item.get('item_id')
            item_price = float(item.get('item_price'))
            item_type = item.get('item_type')
            yima.logger.info(u'项目: __%s__, ID: __%s__, 价格: __%s__' % (item_name, item_id, item_price))

            if item_id and item_price <= 10:
                # if item_price <= 1:
                #     count = 10
                # else:
                #     count = int(10 / item_price)
                num = yima.get_phone(item_id)
                yima.logger.info(num)
                if len(num) == 0:
                    yima.logger.info(u'没有获取到有效号码')
                    yima.exit()
                    yima.login()
                    print "没有获取到有效号码"
                    empty_count += 1
                    continue

                phone_items = []

                current_time = time.strftime(
                    '%Y-%m-%d %H:%M:%S', time.localtime(time.time()))

                phone_item = {
                    'item_name': item_name,  # 项目名称
                    'item_id': item_id,  # 项目ID
                    'crawl_time': current_time,  # 采集时间
                    'item_price': item_price,  # 项目价格
                    'item_type': item_type,  # 项目类型
                    'phone': num,  # 手机号
                    'portal': u'易码',  # 来源门户
                }

                new_item = add_item_fields(phone_item)
                phone_items.append(new_item)

                if increase_length > 0:
                    save_items(phone_items, PHONE_FILE)

                    saved_count += 1

                    print saved_count,

                retry_time_per_item += 1

                # 依据重复次数判断该项目的卡号已被大致取完
                replicate_count += (1 - increase_length)

                print replicate_count,

            else:
                yima.logger.info(u'项目价格超过10元, 放弃.')
        print "",

    yima.logger.info(u'采集结束' + '-' * 30)


if __name__ == '__main__':
    main()