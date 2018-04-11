#!/usr/bin/python
#-*- coding: utf-8 -*-

# 账号：nextnext （密码： mmjj4321）
# qq: 168103647  (密保邮箱: 168103647@qq.com)
# 密保手机 18924312528
# 野码    登录网站  http://yemapt.com

import requests
import time
import os
import sys
import math
import json
import codecs
import random
import logging

from requests.exceptions import ConnectionError
from utils import save_items, get_items_from_file, add_item_fields, log_init, save_items_with_json

reload(sys)
sys.setdefaultencoding('utf8')

'''
1.API 接口地址：http://www.yemapt.com/api
2.接口字符串地方，请进行 url 编码(UTF-8)。
3.接口统一采用 JSON 进行压缩。
4.接口调用方式：HTTP GET 方式（不支持 post）
5. 所有接口访问地址和参数，都需区分大小写，一定需注意。
6.状态 Return 返回,如果为 True 为成功,False 为失败,Info 为失败信息。
7.两个普通函数调用之间请保留至少 1S 的时间间隔,两个取码函数之间请保留至少
3S 的时间间隔。

'''


class Yema(object):
    def __init__(self):
        self.api_prefix = 'http://www.yemapt.com/api/'
        self.user_name = 'nextnext'
        self.user_pwd = 'mmjj4321'
        self.token = 'mmjj4321'
        self.session = requests.session()
        self.headers = {
            'accept': "*/*",
            'accept-encoding': "gzip, deflate, sdch",
            'accept-language': "zh-CN,zh;q=0.8",
            'cache-control': "no-cache",
            'connection': "keep-alive",
            'host': "yemapt.com",
            'pragma': "no-cache",
            'referer': "http://yemapt.com/web/project.html",
            'user-agent': "Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.96 Safari/537.36",
            'x-requested-with': "XMLHttpRequest",

        }

        # 保存网站项目信息的文件
        self.items_file = os.path.sep.join([sys.path[0], 'items', 'yema_items.json'])

        # 保存最终获得的手机号码信息保存文件
        current_date = time.strftime('%Y-%m-%d', time.localtime(time.time()))
        # self.phone_file = os.path.sep.join([sys.path[0], 'data', 'yema_phone_%s.txt' % (current_date)])
        self.phone_file = os.path.sep.join([sys.path[0], 'data', 'ema_phone_yema_phone_%s.txt' % (current_date)])

        # LOG
        month = time.strftime('%Y-%m', time.localtime(time.time()))
        self.log_file = os.path.sep.join([sys.path[0], 'log', 'yema_%s.log' % month])

        save_items([], self.phone_file)
        log_name = self.__class__.__name__
        log_init(log_name, self.log_file)
        self.logger = logging.getLogger(log_name)
        self.logger.info(u'开始采集' + '-' * 30)

    def request(self, request_type, url, payload):
        try:
            if request_type == 'get':
                r = requests.get(url=url, params=payload, headers=self.headers)
            else:
                r = requests.post(url=url, params=payload, headers=self.headers)
            r.encoding = 'utf-8'

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

    def user_info(self):
        url = self.api_prefix + 'GetMyinfo.php'
        params = {
            'Uid': self.user_name,
            'Pwd': self.user_pwd
        }
        r = self.request(url=url, request_type='get', payload=params)
        # 返回失败: {"Return":"False","Info":"失败信息"}
        # 普通用户返回成功: {"Return":"True"," type":"帐号类型(1 普通用户 2 开发者)"," Money
        # ":"余额"," SumMoney ":"帐号共充值"}
        if 'False' in r:
            return False
        else:
            return r

    def login(self):
        # 因为该网站的请求为每次均携带uN与uP获取,所以无须登录
        # 并且也没有登录接口可供使用
        # 2017-9-20
        return True

    def get_phone(self, item_id, count=1, phone=None):
        self.item_id = item_id
        url = self.api_prefix + 'GetMobilenum.php'
        params = {
            'Uid': self.user_name,
            'Pwd': self.user_pwd,
            'ID': item_id,
            'cr': '',  # 指定运营商  选填
            'size': count,  # 号码获取量， 1-10之间   选填
            'area': '',  # 归属地    选填
            'onks': '',  # 指定卡商     选填
            'mobile': phone,  # 指定手机号码  选填
        }
        # 两个 GetMobilenum 请保留至少 1S 的时间间隔。
        # 返回失败: {"Return":"False","Info":"失败信息"}
        # 返回成功: {"Return":"True"," mobile":"手机号(多号码-隔开)"}
        r = json.loads(self.request(url=url, request_type='get', payload=params))
        time.sleep(1)
        phones = []
        if r and r.get('Return') == 'True':
            try:
                _phones = r['mobile'].split('-')
                for _phone in _phones:
                    phones.append(_phone)
            except KeyError as e:
                print(str(e))
        return phones

    def release_all_phone(self):
        url = self.api_prefix + 'ReleaseMobile.php'
        params = {
            'Uid': self.user_name,
            'Pwd': self.user_pwd,
            'ID': self.item_id,  # 释放制定项目    选填
            'Mobile': ''  # 释放指定手机号   选填
        }

        # 返回失败: {"Return":"False","Info":"失败信息"}
        # 返回成功: {"Return":"True"}
        r = self.request(url=url, request_type='get', payload=params)
        if 'False' in r:
            return False
        else:
            print '释放成功'
            return r

    # 由于没有item的接口， 之后的方法用于获取网站中的项目名
    # 网站不需要登录， 可以直接拿json格式的数据
    def get_items(self, page=1):
        print("获取网站项目列表中")
        url = 'http://yemapt.com/api/SearchID.php?Uid=%s&Pwd=%s&Page=%s&' \
              % (self.user_name, self.user_pwd, page)
        r = self.session.get(url=url).text
        json_info = json.loads(r)
        all_length = json_info['Alllength']
        page_length = json_info['Pagelength']

        total_page = math.ceil(float(all_length) / float(page_length))
        items = []

        for i in range(int(total_page)):
            url = 'http://yemapt.com/api/SearchID.php?Uid=%s&Pwd=%s&Page=%s&' \
                  % (self.user_name, self.user_pwd, str(i + 1))
            r = self.session.get(url=url).text
            json_info = json.loads(r)
            item_info = json_info['Test']
            item_list = item_info.split('|')
            for each_item in item_list:
                item = dict(zip(['item_id', 'item_name', 'item_type', 'item_price'], each_item.split('-')[0:-1]))
                items.append(item)

            time.sleep(1)

        return items

    def exit(self):
        pass


def main():
    yema = Yema()
    yema.login()

    if os.path.exists(yema.items_file):
        items = get_items_from_file(yema.items_file)
        yema.logger.info(u'从文件中读取__%s__网站可接收验证码项目%d个。' % (
            str(yema.__class__).split('.')[1].strip("'>"), len(items)))
    else:
        items = yema.get_items()
        save_items_with_json(items, yema.items_file)
        yema.logger.info(u'一共获取__%s__网站可接收验证码项目%d个。' % (
            str(yema.__class__).split('.')[1].strip("'>"), len(items)))

    for item in items[:]:
        max_time_per_item = 2000
        retry_time_per_item = 0
        phones_per_item_set = set()
        # 最近三次不重复号码总量增长
        three_increase = [10, 10, 10]
        increase_length = 0

        while 1:
            if sum(three_increase) < 10 or retry_time_per_item >= max_time_per_item:
                break
            item_name = item.get('item_name')
            item_id = item.get('item_id')
            item_price = float(item.get('item_price'))
            item_type = item.get('item_type')
            yema.logger.info(u'项目: __%s__, ID: __%s__, 价格: __%s__' % (item_name, item_id, item_price))

            if item_id and item_price <= 10:
                # 因为该网站的批量取码一次是10个 所以检定规则的数值有变
                # 余额是10元 (2017-9-20)
                if item_price <= 1:
                    count = 10
                else:
                    count = int(10.0/item_price)

                nums = yema.get_phone(item_id, count)
                yema.logger.info(nums)
                if len(nums) == 0:
                    yema.logger.info(u'没有获取到有效号码')

                # 同一个item_id查询出的不重复的号码
                last_length = len(phones_per_item_set)
                phones_per_item_set.update(nums)
                current_length = len(phones_per_item_set)
                increase_length = current_length - last_length

                phone_items = []
                for num in nums[:]:
                    current_time = time.strftime(
                        '%Y-%m-%d %H:%M:%S', time.localtime(time.time()))

                    phone_item = {
                        'item_name': item_name,         # 项目名称
                        'item_id': item_id,             # 项目ID
                        'crawl_time': current_time,     # 采集时间
                        'item_price': item_price,       # 项目价格
                        'item_type': item_type,         # 项目类型
                        'phone': num,                   # 手机号
                        'portal': u'野码',              # 来源门户
                    }
                    new_item = add_item_fields(phone_item)
                    phone_items.append(new_item)
                if len(phone_items) > 0:
                    save_items(phone_items, yema.phone_file)

                # 退出, 让token失效
                yema.exit()
                # 重新登录, 刷新token
                yema.login()
            else:
                yema.logger.info(u'项目价格超过10元, 放弃.')
            retry_time_per_item += 1

            # 依据重复率判断是否需要结束当前item_id的重复尝试
            three_increase[2] = three_increase[1]
            three_increase[1] = three_increase[0]
            three_increase[0] = increase_length
            print three_increase

    yema.logger.info(u'采集结束' + '-'*30)


if __name__ == '__main__':
    main()
