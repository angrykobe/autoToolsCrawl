#!/usr/bin/python
#-*- coding: utf-8 -*-
'''
Created on 2017-04-07 16:58:09
Updated on 2017-05-11 11:32:58

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
from utils import save_items, get_items_from_file, add_item_fields, log_init
reload(sys)
sys.setdefaultencoding('utf8')

# 叮叮卡码(http://code.yayayama.com/index.html)
# 账号/密码: kkk777(kkk777)
# 登录后, token有效期为10分钟, 过期需要重新申请token
# 平台接口前缀: 'http://code.yayayama.com/apimanual.html'
'''
账户基本信息
account_info = {
    'user_info': {
        u'用户名': 'kkk777',
        u'用户类别': '普通类型',
        u'可同时登陆': '30',
        u'可同时获取号码数': '5000000',
        u'单个客户端获取号码数': '500',
        u'折扣': '100%',        
        u'用户余额': '10.000',
        u'积分': '10.00',
        u'真实姓名': '',
        u'支付宝': '',
        u'电子邮箱': '1747485592@qq.com',
        u'手机号码': '18926779674',
        u'QQ': '1747485591',
        u'注册日期': '2017/3/7 18:50:14',
    }

}
'''
# 注意：只要密码不变，token是可长期使用的，所以登录方法只需要
# 调用一次获取到token即可，程序运行中请不要重复调用
# (并非一个用户每次登录都是相同token)

# 开发者参数(登录之后未找到, 调用API时该参数为空都可以...)
# DEVELOPER = r'CjLBFGjwJnHADikT40q%2b0w%3d%3d'
DEVELOPER = ''

# API前缀
API_PREFIX = r'http://www.yayayama.com:19876'

# 保存网站项目信息的文件
ITEMS_FILE = os.path.sep.join([sys.path[0], 'items', 'dingdingkama_items.json'])

# 保存最终获得的手机号码信息保存文件
current_date = time.strftime('%Y-%m-%d', time.localtime(time.time()))
PHONE_FILE = sys.path[0] + os.path.sep + 'data' + os.path.sep + 'dingdingkama_phone_%s.txt' % (current_date)

# LOG
month = time.strftime('%Y-%m', time.localtime(time.time()))
LOG_FILE = os.path.sep.join([sys.path[0], 'log', 'dingdingkama_%s.log' % month])


class Dingdingkama(object):
    def __init__(self):
        self.api_prefix = API_PREFIX
        self.developer = DEVELOPER
        self.user_name = 'kkk777'
        self.user_pwd = 'kkk777'
        self.token = '1buBaArtW0J2m0JG0JRzAMCYKduReC3554'
        self.phone_list = ''
        self.headers = {
            'Host': 'www.yayayama.com:19876',
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
                r.encoding = 'gb2312'
                
                # 情况1, get_phone出错: False:Session 过期
                # # 情况2, getItem出错: False:余额不足，请先释放号码
                if r.text in [u'False:Session 过期', u'False:余额不足，请先释放号码']:
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
            'uName': self.user_name,
            'pWord': self.user_pwd,
            'Developer': self.developer,
        }
        url = self.api_prefix+'/Url/userLogin'
        token_text = self.request('get', url, payload)
        if token_text:
            self.token = token_text.strip().split('&')[0]
            if self.token != '':
                self.logger.info(u'登录成功！')
        else:
            self.logger.info(u'登录失败！')

    # 获取项目
    def get_items(self, token):
        # 返回格式
        # 项目ID&项目名称&项目价格&项目类型\n项目ID&项目名称&项目价格&项目类型\n...
        # 项目类型:
        #   1. 表示此项目用于接收验证码
        #   2. 表示此项目用户发送短信
        #   3. 表示此项目即可接收验证码，也可以发送短信
        #   4. 表示可以接受多个验证码
        payload = {
            'token': token,
            'tp': 'ut',
        }
        url = self.api_prefix+'/Api/GetItem'
        item_text = self.request('get', url, payload=payload)
        if item_text:
            self.logger.info(item_text[:100].encode('gb18030'))
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
        area_url = 'http://www.yayayama.com:19876/Api/GetArea?'
        area_res_text = self.request('get', area_url)
        area_list = area_res_text.split('\n')
        return area_list

    # 获取号码
    def get_phone(self, token, item_id, count):
        # token: 用户登录时获取的token
        # item_id: 项目ID
        # count: 获取手机号的数量
        
        payload = {
            'token': token,         # 登录token   必填
            'ItemId': item_id,      # 项目代码    必填
            'Count': str(count),    # 获取数量(不填默认1个)
            'Area': '',             # 区域(不填则随机)
            'PhoneType': '',        # 运营商(不填为0, [0-随机][1-移动][2-联通][3-电信])
        }
        url = self.api_prefix + '/Url/userGetPhone'
        phone_text = self.request('get', url, payload)
        phones = []
        if phone_text:
            if u'False:' in phone_text:
                self.login()
            else:
                phones = phone_text.split(';')[:-1]
                add_str = '-%s;' % (item_id)
                self.phone_list = add_str.join(phones) + add_str
        return phones

    # 释放号码(该平台只能通过该方法释放号码, 退出登录无法释放)
    def release_phone(self):
        url = self.api_prefix + '/Url/userResPhoneList'
        payload = {
            'token': self.token,
            'phoneList': self.phone_list,
        }
        text = self.request('get', url, payload)
        if text and 'RES' in text:
            self.logger.info(u'释放号码成功!')

    # 退出
    def exit(self, token):
        url = self.api_prefix + '/Url/userExit'
        payload = {'token': token}
        text = self.request('get', url, payload)
        if text:
            self.logger.info(u'退出成功！%s' % (text))

def main():

    dingdingkama = Dingdingkama()
    dingdingkama.login()

    if os.path.exists(ITEMS_FILE):
        items = get_items_from_file(ITEMS_FILE)
        dingdingkama.logger.info(u'从文件中读取__%s__网站可接收验证码项目%d个。' % (
            str(dingdingkama.__class__).split('.')[1].strip("'>"), len(items)))
    else:
        items = dingdingkama.get_items(dingdingkama.token)
        save_items(items, ITEMS_FILE)
        dingdingkama.logger.info(u'一共获取__%s__网站可接收验证码项目%d个。' % (
            str(dingdingkama.__class__).split('.')[1].strip("'>"), len(items)))

    for item in items[:]:
        # 每个项目拿10次
        for i in xrange(10):
            item_name = item.get('item_name')
            item_id = item.get('item_id')
            item_price = float(item.get('item_price'))
            item_type = item.get('item_type')
            dingdingkama.logger.info(u'项目: __%s__, ID: __%s__, 价格: __%s__' % (item_name, item_id, item_price))

            if item_id and item_price <= 10:
                count = 10
                phones = dingdingkama.get_phone(dingdingkama.token, item_id, count)
                dingdingkama.logger.info(phones)
                if len(phones) == 0:
                    dingdingkama.logger.info(u'没有获取到有效号码')
                    dingdingkama.release_phone()
                    dingdingkama.login()
                    continue

                phone_items = []
                for phone in phones:
                    current_time = time.strftime(
                        '%Y-%m-%d %H:%M:%S', time.localtime(time.time()))

                    phone_item = {
                        'item_name': item_name,             # 项目名称
                        'item_id': item_id,                 # 项目ID
                        'crawl_time': current_time,         # 采集时间
                        'item_price': item_price,           # 项目价格
                        'item_type': item_type,             # 项目类型
                        'phone': phone,                     # 手机号
                        'portal': u'叮叮卡码',              # 来源门户
                    }
                    new_item = add_item_fields(phone_item)
                    phone_items.append(new_item)
                save_items(phone_items, PHONE_FILE)

                # 退出, 让token失效
                dingdingkama.release_phone()
            else:
                dingdingkama.logger.info(u'项目价格超过10元, 放弃.')
    dingdingkama.logger.info(u'采集结束' + '-'*30)
        

if __name__ == '__main__':
    main()
    # 之后代码重构的时候可以把main()方法中的流程做成一个统一的方法。
    # 不同的类采用一个工厂方法生成。
