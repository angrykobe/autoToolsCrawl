#!/usr/bin/python
#-*- coding: utf8 -*-
'''
Created on 2017-03-29 20:16:02
Updated on 2017-05-11 11:32:48

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


# 飞码(http://www.2009abc.com/)   
# 实际为: 千万卡平台(http://www.yika66.com/userManage/index.aspx)
# 账号/密码: kkk321(mj2.236kj)
# 登录后, token有效期为10分钟, 过期需要重新申请token
# 平台接口前缀: 'http://xapi.yika66.com'
'''
账户基本信息
account_info = {
    'user_info': {
        u'用户名': 'kkk321',
        u'余额': '1.000',
        u'佣金': '0.000',
        u'积分': '1.000',
        u'折扣': '100%',
        u'用户等级': '普通会员',
        u'可同时登陆': '10',
        u'可同时获取数': '30',
        u'单个获取数': '10',
    }
    'register_info': {
        u'用户ID': '100088424',
        u'用户名': 'kkk321',
        u'密码': 'kkk321',
        u'联系电话': '18926779674',
        u'联系QQ': '1747485592',
        u'联系邮箱': '1747485592@qq.com',
        u'支付宝姓名': '张三',
        u'支付宝账号': '18926779674',
    }
    
    # 开发者参数
    'Developer': 'bcXbqUkm1xE23qXSaiwY9Q%3d%3d ',
}
'''



class Feima(object):
    def __init__(self):
        self.api_prefix = r'http://xapi.yika66.com'
        self.developer = r'bcXbqUkm1xE23qXSaiwY9Q%3d%3d'
        self.user_name = 'kkk321'
        self.user_pwd = 'mj2.236kj'
        self.token = '0JAv4nU76RVN9PLpot0Jd4LOLUO25x4382'
        self.phone_list = ''
        self.headers = {
            'Host': 'www.yika66.com',
            'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1',
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/56.0.2924.87 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Referer': 'http://www.yika66.com/Web/Api.Aspx',
            'Accept-Encoding': 'gzip, deflate, sdch',
            'Accept-Language': 'zh-CN,zh;q=0.8,en-US;q=0.6,en;q=0.4',
        }
        # 保存网站项目信息的文件
        self.items_file = os.path.sep.join([sys.path[0] , 'items', 'feima_items.json'])

        # 保存最终获得的手机号码信息保存文件
        current_date = time.strftime('%Y-%m-%d', time.localtime(time.time()))
        self.phone_file = sys.path[0] + os.path.sep + 'data' + os.path.sep + 'feima_phone_%s.txt' % (current_date)

        # LOG
        month = time.strftime('%Y-%m', time.localtime(time.time()))
        self.log_file = os.path.sep.join([sys.path[0], 'log', 'feima_%s.log' % month])

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
                
                # 情况1, get_num出错: False:Session 过期
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
                time.sleep(60)
            except Exception, e:
                self.logger.info(e)
                return

    # 登录, 获得用户token
    def login(self):
        payload = {
            'uName': self.user_name,
            'pWord': self.user_pwd,
            'Developer': self.developer,
            'code': 'utf8',
        }
        url = self.api_prefix+'/User/login'
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
            'code': 'utf8',
        }
        url = self.api_prefix+'/User/getItems'
        item_text = self.request('get', url, payload=payload)
        if item_text:
            if u'False:' in item_text:
                self.login()
            else:            
                self.logger.info(item_text[:100].encode('gb18030'))
                item_list = item_text.split('\n')
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
        area_url = 'http://xapi.yika66.com/User/getArea?code=utf8'
        area_res_text = self.request('get', area_url)
        area_list = area_res_text.split('\n')
        return area_list

    # 获取号码
    def get_phone(self, item_id, count=1, phone=''):
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
            'code': 'utf8',         # 转UTF8编码(缺省UTF8) 
        }
        url = self.api_prefix + '/User/getPhone'
        num_text = self.request('get', url, payload)
        phones = []
        if num_text:
            if u'False:' in num_text:
                self.login()
            else:
                phones = num_text.split(';')[:-1]
                add_str = '-%s;' % (item_id)
                self.phone_list = add_str.join(phones) + add_str
        print phones
        return phones

    # 释放号码
    # 未知原因, 无法正常访问
    def release_phone(self):
        url = self.api_prefix + '/User/releasePhone'
        payload = {
            'token': self.token,
            'phoneList': self.phone_list,
        }
        text = self.request('get', url, payload)
        if text:
            self.logger.info(u'释放号码: %s' % (text))

    # 释放所有号码
    # 未知原因, 无法正常访问
    def release_all_phone(self):
        url = self.api_prefix + '/User/ReleaseAllPhone'
        payload = {'token': self.token}
        text = self.request('get', url, payload)
        if text:
            self.logger.info(u'释放号码: %s' % (text))

    # 退出
    def exit(self):
        url = self.api_prefix + '/User/exit'
        payload = {'token': self.token}
        text = self.request('get', url, payload)
        if text:
            self.logger.info(u'退出成功！%s' % (text))


def main():

    feima = Feima()
    feima.login()

    if os.path.exists(feima.items_file):
        items = get_items_from_file(feima.items_file)
        feima.logger.info(u'从文件中读取__%s__网站可接收验证码项目%d个。' % (
            str(feima.__class__).split('.')[1].strip("'>"), len(items)))
    else:
        items = feima.get_items()
        save_items(items, feima.items_file)
        feima.logger.info(u'一共获取__%s__网站可接收验证码项目%d个。' % (
            str(feima.__class__).split('.')[1].strip("'>"), len(items)))

    for item in items[:]:
        # 每个项目拿10次
        # 2017-04-05 发现目标网站采取反扒措施,每次拿到的号码都一样。
        # 只有被封了, 然后恢复的时候会改变号码。所以每个项目拿10次改成1次。
        # 2017-05-09, 可以拿到不同的号码, 但是重复率很高, 主动增加延时为3秒       
        for i in xrange(10):
            time.sleep(2)
            item_name = item.get('item_name')
            item_id = item.get('item_id')
            item_price = float(item.get('item_price'))
            item_type = item.get('item_type')
            feima.logger.info(u'项目: __%s__, ID: __%s__, 价格: __%s__' % (item_name, item_id, item_price))

            if item_id and item_price <= 10:
                if item_price <= 1:
                    count = 10
                else:
                    count = int(10.0/item_price)

                nums = feima.get_phone(item_id, count)
                feima.logger.info(nums)
                if len(nums) == 0:
                    feima.logger.info(u'没有获取到有效号码')
                    feima.exit()
                    feima.login()
                    continue

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
                        'portal': u'飞码',              # 来源门户(实际为千万卡平台)
                    }
                    new_item = add_item_fields(phone_item)
                    phone_items.append(new_item)
                save_items(phone_items, feima.phone_file)


                # 退出, 让token失效
                feima.release_phone()
                # 重新登录, 刷新token
                feima.login()
            else:
                feima.logger.info(u'项目价格超过10元, 放弃.')
    feima.exit()                
    feima.logger.info(u'采集结束' + '-'*30)
        

if __name__ == '__main__':
    main()
