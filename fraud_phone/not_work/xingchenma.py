#!/usr/bin/python
# -*- coding: utf-8 -*-
'''
Created on 2017-04-05 20:24:05
Updated on 2017-04-06 11:26:02

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
from utils import save_items, get_items_from_file, add_item_fields, log_init, save_items_with_json
reload(sys)
sys.setdefaultencoding('utf8')


# 星辰(http://xingchenma.com:9000/login.aspx)
# 账号/密码: aaa111(mj2.236kj)
# 登录后, token有效期为10分钟, 过期需要重新申请token
# 平台接口前缀: 'http://www.xingchenma.com:9180/service.asmx'
'''
账户基本信息
account_info = {
    'user_info': {
        u'用户名': 'aaa111',
        u'用户类别': '',
        u'可同时登陆': '',
        u'可同时获取号码数': '',
        u'单个客户端获取号码数': '',
        u'折扣': '',
        u'用户余额': '',
        u'可提现余额': '',
        u'积分': '',
        u'真实姓名': '',
        u'支付宝': '',
        u'电子邮箱': '',
        u'手机号码': '18926779674',
        u'QQ': '',
        u'注册日期': '',
    }
}
'''


class Xingchenma(object):
    def __init__(self):
        self.api_prefix = r'http://www.xingchenma.com:9180/service.asmx'
        self.user_name = 'aaa111'
        self.user_pwd = 'mj2.236kj'
        self.token = ''
        self.headers = {
            'Host': 'www.xingchenma.com:9180',
            'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1',
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/56.0.2924.87 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Accept-Encoding': 'gzip, deflate, sdch',
            'Accept-Language': 'zh-CN,zh;q=0.8,en-US;q=0.6,en;q=0.4',
        }
        # 保存网站项目信息的文件
        self.items_file = os.path.sep.join([sys.path[0] , 'items', 'xingchenma_items.json'])

        # 保存最终获得的手机号码信息保存文件
        current_date = time.strftime('%Y-%m-%d', time.localtime(time.time()))
        self.phone_file = sys.path[0] + os.path.sep + 'data' + os.path.sep + 'xingchenma_phone_%s.txt' % (current_date)

        # LOG
        month = time.strftime('%Y-%m', time.localtime(time.time()))
        self.log_file = os.path.sep.join([sys.path[0], 'log', 'xingchenma_%s.log' % month])

        save_items([], self.phone_file)
        log_name = self.__class__.__name__
        log_init(log_name, self.log_file)
        self.logger = logging.getLogger(log_name)
        self.logger.info(u'开始采集' + '-'*30)

    # 统一处理请求部分
    def request(self, request_type, url, payload=None):
        # request_type: 请求类型
        # url: 请求地址
        # payload: 请求参数

        retry_time = 0
        while 1:
            try:
                if request_type == 'post':
                    r = requests.post(url=url, headers=self.headers, data=payload, allow_redirects=False)
                elif request_type == 'get':
                    r = requests.get(url=url, headers=self.headers, params=payload, allow_redirects=False)
                r.encoding = 'utf8'

                # 情况1, get_phone出错: False:Session 过期
                # # 情况2, getItem出错: False:余额不足，请先释放号码
                if r.text in [u'False:Session 过期', u'False:余额不足，请先释放号码']:
                    if retry_time < 3:
                        retry_time += 1
                        self.logger.info(r.text + u'\t重试中。。。')
                    else:
                        return r.text

                if r.status_code == 200 and 'False' not in r.text:
                    return r.text
                elif r.status_code == 504:
                    time.sleep(5)
                    self.logger.info(str(r.status_code) + u'\t网关超时, 休眠5秒。')
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
            'name': self.user_name,
            'psw': self.user_pwd,
        }

        url = self.api_prefix+'/UserLoginStr?'
        token_text = self.request('get', url, payload)
        if token_text and len(token_text)==32:
            self.token = token_text.strip()
            if self.token != '':
                self.logger.info(u'登录成功！')
        else:
            self.logger.info(u'登录失败！')

    # 获取收藏项目
    def get_items(self):
        # 返回格式
        # 项目ID&项目名称&项目价格&项目类型\n项目ID&项目名称&项目价格&项目类型\n...
        # 项目类型:
        #   1. 表示此项目用于接收验证码
        #   2. 表示此项目用户发送短信
        #   3. 表示此项目即可接收验证码，也可以发送短信
        #   4. 表示可以接受多个验证码
        payload = {
            'token': self.token,
        }
        url = self.api_prefix+'/GetXMStr'
        item_text = self.request('get', url, payload=payload)
        if item_text:
            if len(item_text)<10:
                self.login()
            else:            
                self.logger.info(item_text[:100].encode('gb18030'))
                item_list = item_text.split('|;|')
                items = []
                for item in item_list:
                    item_dict = dict(zip(
                        ['item_id', 'item_name', 'item_price', 'item_type'], item.split('|,|')))
                    item_type = item_dict.get('item_type')
                    if item_type:
                        items.append(item_dict)
                return items

    # 获取号码
    def get_phone(self, item_id, count=1):
        # token: 用户登录时获取的token
        # item_id: 项目ID

        payload = {
            'token': self.token,    # 登录token   必填
            'xmid': item_id,        # 项目代码    必填
            'sl': count,            # 获取号码数量
            'lx': 0,                # 运营商(不填为0, [0-随机][1-移动][2-联通][3-电信])
            'a1': '',               # 省份(不填表示不限地区)
            'a2': '',               # 城市(参数值为空时表示不限城市)
            'pk': '',               # 专属卡商对应编号
        }
        url = self.api_prefix + '/GetHMStr'
        num_text = self.request('get', url, payload)
        phones = []
        if num_text:
            if 'hm=' not in num_text:
                self.logger.info(u'获取号码失败, 释放号码。')
                self.release_all_phone()
            else:
                phones = num_text.replace('hm=', '').split(',')
        return phones

    # 获取指定号码
    def get_specific_phone(self, item_id, phone):
        # item_id: 项目ID
        # phone: 指定号码

        payload = {
            'token': self.token,    # 登陆token 
            'xmid': item_id,        # 项目编码    
            'hm': phone,            # 指定号码    
            'op': 1,                # 码库检测方式  0-检测云码库该号码是否已经做过该项目任务
                                    # 1-不检测码库是否已经做过该项目
        }
        url = self.api_prefix + '/mkHMStr'
        response_int = self.request('get', url, payload)
        # 为了和其他平台统一, 命中返回一个长度为1的list, 否则返回一个空的list
        print response_int
        if response_int in ['1', '-2', '-3', '-5', '-10', '-13', '-16', '-20', '-30']:
            return ['1']
        else:
            return []

    # 释放所有号码
    def release_all_phone(self):
        url = self.api_prefix + '/sfAllStr'
        payload = {
            'token': self.token,
        }
        text = self.request('get', url, payload)
        if text == u'1':
            self.logger.info(u'释放号码成功!')
        else:
            self.logger.info(u'释放号码失败,重新登录刷新token。')

    # 退出
    def exit(self):
        url = self.api_prefix + 'UserExitStr'
        payload = {'token': self.token}
        text = self.request('get', url, payload)
        if text == 1:
            self.logger.info(u'退出成功!')


def main():
    xingchenma = Xingchenma()
    xingchenma.login()

    if os.path.exists(xingchenma.items_file):
        items = get_items_from_file(xingchenma.items_file)
        xingchenma.logger.info(u'从文件中读取__%s__网站可接收验证码项目%d个。' % (
            str(xingchenma.__class__).split('.')[1].strip("'>"), len(items)))
    else:
        items = xingchenma.get_items()
        save_items_with_json(items, xingchenma.items_file)
        xingchenma.logger.info(u'一共获取__%s__网站可接收验证码项目%d个。' % (
            str(xingchenma.__class__).split('.')[1].strip("'>"), len(items)))

    for item in items[:]:
        max_time_per_item = 1000
        retry_time_per_item = 0
        phones_per_item_set = set()
        # 最近三次不重复号码总量增长
        three_increase = [20, 20, 20]
        increase_length = 0

        while 1:
            if sum(three_increase) < 5 or retry_time_per_item >= max_time_per_item:
                break
            # time.sleep(1.5)
            item_name = item.get('item_name')
            item_id = item.get('item_id')
            item_price = float(item.get('item_price'))
            item_type = item.get('item_type')
            xingchenma.logger.info(u'项目: __%s__, ID: __%s__, 价格: __%s__' % (item_name, item_id, item_price))

            if item_price <= 10:
                if item_price > 1:
                    count = int(10/item_price)
                else:
                    count = 10
                nums = xingchenma.get_phone(item_id, count)
                xingchenma.logger.info(nums)
                if len(nums) == 0:
                    xingchenma.logger.info(u'没有获取到有效号码！')

                # 同一个item_id查询出的不重复的号码
                last_length = len(phones_per_item_set)
                phones_per_item_set.update(nums)
                current_length = len(phones_per_item_set)
                increase_length = current_length - last_length

                phone_items = []
                for num in nums:
                    current_time = time.strftime(
                        '%Y-%m-%d %H:%M:%S', time.localtime(time.time()))

                    phone_item = {
                        'item_name': item_name,         # 项目名称
                        'item_id': item_id,             # 项目ID
                        'crawl_time': current_time,     # 采集时间
                        'item_price': item_price,       # 项目价格
                        'item_type': item_type,         # 项目类型
                        'phone': num,                   # 手机号
                        'portal': u'星辰',              # 来源门户
                    }
                    new_item = add_item_fields(phone_item)
                    phone_items.append(new_item)
                if len(phone_items) > 0:
                    save_items(phone_items, xingchenma.phone_file)

                # 释放号码
                xingchenma.release_all_phone()
                # 重新登录, 刷新token
                xingchenma.login()
            else:
                xingchenma.logger.info(u'项目价格超过10元, 放弃！')
            retry_time_per_item += 1

            # 依据重复率判断是否需要结束当前item_id的重复尝试
            three_increase[2] = three_increase[1]
            three_increase[1] = three_increase[0]
            three_increase[0] = increase_length
            print three_increase

    # 退出登录
    xingchenma.exit()

    xingchenma.logger.info(u'采集结束' + '-'*30)

if __name__ == '__main__':
    main()
