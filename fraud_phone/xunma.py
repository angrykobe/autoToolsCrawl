#!/usr/bin/python
# -*- coding: utf-8 -*-
'''
Created on 2017-04-01 12:03:43
Updated on 2017-04-01 17:40:37

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


# 讯码(http://www.xunma.net/)
# 账号/密码: aaa111(08c4ab4b3be7bea180ccc6e86412208b8146ac9e)
# 登录后, token有效期为10分钟, 过期需要重新申请token
# 平台接口前缀: 'http://api.xunma.net'
'''
账户基本信息
account_info = {
    'user_info': {
        u'用户名': 'aaa111',
        u'用户类别': 'vip1',
        u'可同时登陆': '20',
        u'可同时获取号码数': '100',
        u'单个客户端获取号码数': '20',
        u'折扣': '98%',
        u'用户余额': '10.020',
        u'可提现余额': '0.000',
        u'积分': '11.00',
        u'真实姓名': '',
        u'支付宝': '',
        u'电子邮箱': '1747485592@qq.com',
        u'手机号码': '18926779674',
        u'QQ': '1747485592',
        u'注册日期': '2017/3/7 10:29:42',
    }

    # 开发者参数

    'Developer': 'CjLBFGjwJnHADikT40q%2b0w%3d%3d'
}
'''
# 注意：只要密码不变，token是可长期使用的，所以登录方法只需要
# 调用一次获取到token即可，程序运行中请不要重复调用
# (并非一个用户每次登录都是相同token)


class Xunma(object):
    def __init__(self):
        self.api_prefix = r'http://api.xunma.net'
        self.developer = r'CjLBFGjwJnHADikT40q%2b0w%3d%3d'
        self.user_name = 'aaa111'
        self.user_pwd = '08c4ab4b3be7bea180ccc6e86412208b8146ac9e'
        self.token = ''
        self.phone_list = ''
        self.headers = {
            'Host': 'api.xunma.net',
            'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1',
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537. (KHTML, like Gecko) Chrome/56.0.2924.87 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Referer': 'http://www.xunma.net/api.html',
            'Accept-Encoding': 'gzip, deflate, sdch',
            'Accept-Language': 'zh-CN,zh;q=0.8,en-US;q=0.6,en;q=0.4',
        }
        # 保存网站项目信息的文件
        self.items_file = os.path.sep.join([sys.path[0], 'items', 'xunma_items.json'])

        # 保存最终获得的手机号码信息保存文件
        current_date = time.strftime('%Y-%m-%d', time.localtime(time.time()))
        # self.phone_file = sys.path[0] + os.path.sep + 'data' + os.path.sep + 'xunma_phone_%s.txt' % (current_date)
        self.phone_file = sys.path[0] + os.path.sep + 'data' + os.path.sep + 'ema_phone_xunma_phone_%s.txt' % (current_date)

        # LOG
        month = time.strftime('%Y-%m', time.localtime(time.time()))
        self.log_file = os.path.sep.join([sys.path[0], 'log', 'xunma_%s.log' % month])

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
                        self.logger.info(r.text, u'重试中。。。')
                    else:
                        return r.text

                # set_cookies = r.headers.get('Set-Cookie')
                # if set_cookies:
                #     cfduid_str = re.search(r'__cfduid=[\S]{43}', set_cookies)
                #     if cfduid_str:
                #         self.cookies['cfduid'] = cfduid_str.group(0).split('=')[1]

                if r.status_code == 200 and 'False' not in r.text:
                    # 服务器返回的项目列表编码为 gb2312
                    # 若使用 encoding='utf8' 来读取，出了函数后
                    # 返回的文本似乎会变成不可逆编码的
                    if '&' in r.text:
                        r.encoding = "gb2312"
                    return r.text
                elif r.status_code == 504:
                    time.sleep(5)
                    self.logger.info(str(r.status_code) + u'\t网关超时, 休眠5秒。')
                elif 'False' in r.text:
                    continue
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
            'uName': self.user_name,
            'pWord': self.user_pwd,
            'Developer': self.developer,
        }
        url = self.api_prefix+'/Login'
        token_text = self.request('get', url, payload)
        if token_text:
            self.token = token_text.strip().split('&')[0]
            if self.token != '':
                self.logger.info(u'登录成功！')
        else:
            self.logger.info(u'登录失败！')

    # 获取项目
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
            'tp': 'ut',
        }
        url = self.api_prefix+'/GetItems'
        item_text = self.request('get', url, payload=payload)
        if item_text:
            item_list = item_text.split('\n')[1:]
            items = []
            for item in item_list:
                item_dict = dict(zip(
                    ['item_id', 'item_name', 'item_price', 'item_type'], item.split('&')))
                item_type = item_dict.get('item_type')
                if item_type and item_type in ['1', '3', '4']:
                    items.append(item_dict)
            return items

    # 获取区域
    def get_area(self):
        area_url = 'http://api.xunma.net/GetArea?'
        area_res_text = self.request('get', area_url)
        area_list = area_res_text.split('\n')
        return area_list

    # 获取号码
    def get_phone(self, item_id, count, phone=''):
        # token: 用户登录时获取的token
        # item_id: 项目ID
        # count: 获取手机号的数量

        payload = {
            'token': self.token,    # 登录token   必填
            'ItemId': item_id,      # 项目代码    必填
            'Phone': phone,         # 指定手机号
            'Count': str(count),    # 获取数量(不填默认1个)
            'Area': '',             # 区域(不填则随机)
            'PhoneType': '',        # 运营商(不填为0, [0-随机][1-移动][2-联通][3-电信])
        }
        url = self.api_prefix + '/getPhone'
        num_text = self.request('get', url, payload)
        phones = []
        if num_text:
            if u'False:' in num_text:
                self.login()
            else:
                phones = num_text.split(';')[:-1]
                add_str = '-%s;' % (item_id)
                self.phone_list = add_str.join(phones) + add_str
        return phones

    # 释放号码
    def release_phone(self):
        url = self.api_prefix + '/releasePhone'
        payload = {
            'token': self.token,
            'phoneList': self.phone_list,
        }
        text = self.request('get', url, payload)
        if text:
            self.logger.info(u'释放号码: %s' % (text))

    # 退出
    def exit(self):
        url = self.api_prefix + '/Exit'
        payload = {'token': self.token}
        text = self.request('get', url, payload)
        if text:
            self.logger.info(u'退出成功！%s' % (text))


def main():
    xunma = Xunma()
    xunma.login()

    if os.path.exists(xunma.items_file):
        items = get_items_from_file(xunma.items_file)
        xunma.logger.info(u'从文件中读取__%s__网站可接收验证码项目%d个。' % (
            str(xunma.__class__).split('.')[1].strip("'>"), len(items)))
    else:
        items = xunma.get_items()
        save_items_with_json(items, xunma.items_file)
        xunma.logger.info(u'一共获取__%s__网站可接收验证码项目%d个。' % (
            str(xunma.__class__).split('.')[1].strip("'>"), len(items)))

    for item in items[:]:
        max_time_per_item = 1000
        retry_time_per_item = 0
        phones_per_item_set = set()
        # 最近三次不重复号码总量增长
        three_increase = [20, 20, 20]
        increase_length = 0

        while 1:
            if sum(three_increase) < 10 or retry_time_per_item >= max_time_per_item:
                break
            # time.sleep(1.5)
            item_name = item.get('item_name')
            item_id = item.get('item_id')
            item_price = float(item.get('item_price'))
            item_type = item.get('item_type')
            xunma.logger.info(u'项目: __%s__, ID: __%s__, 价格: __%s__' % (item_name, item_id, item_price))

            if item_id and item_price <= 10:
                if item_price <= 0.5:
                    count = 20
                else:
                    count = int(10.0/item_price)

                nums = xunma.get_phone(item_id, count)
                xunma.logger.info(nums)
                if len(nums) == 0:
                    xunma.logger.info(u'没有获取到有效号码')

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
                        'portal': u'讯码',              # 来源门户
                    }
                    new_item = add_item_fields(phone_item)
                    phone_items.append(new_item)
                if len(phone_items) > 0:
                    save_items(phone_items, xunma.phone_file)

                # 退出, 让token失效
                xunma.exit()
                # 重新登录, 刷新token
                xunma.login()
            else:
                xunma.logger.info(u'项目价格超过10元, 放弃.')
            retry_time_per_item += 1

            # 依据重复率判断是否需要结束当前item_id的重复尝试
            three_increase[2] = three_increase[1]
            three_increase[1] = three_increase[0]
            three_increase[0] = increase_length
            print three_increase

    xunma.logger.info(u'采集结束' + '-'*30)


if __name__ == '__main__':
    main()
