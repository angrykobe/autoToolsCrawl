#!/usr/bin/python
#-*- coding: utf-8 -*-
'''
Created on 2017-04-07 15:17:55

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


# 基码(http://www.jima123.com/)   
# 账号/密码: kkk321(kkk321)
# 登录后, token有效期为10分钟, 过期需要重新申请token
# 平台接口前缀: 'http://api.ltxin.com:8888'
'''
账户基本信息
account_info = {
    'user_info': {
        u'用户名': 'kkk321',
        u'用户类别': '登堂入室',
        u'最大登陆数量': '5',
        u'最大取号数量': '10',
        u'用户余额': '0.00',
        u'暂冻余额': '0.00',
        u'积分': '10.00',
        u'真实姓名': '赵四',
        u'联系电话': '18926779674',
        u'开发者余额': '0.0000',
        u'QQ': '1747485592',
    }
    
    u'Developer': 'yTVCJOLThoMGGJaQSqFImyv86Jnsx2vv',
}
'''


# 开发者参数
DEVELOPER = r'yTVCJOLThoMGGJaQSqFImyv86Jnsx2vv'

# API前缀
API_PREFIX = r'http://api.jima123.com/api.php'

# 保存网站项目信息的文件
ITEMS_FILE = os.path.sep.join([sys.path[0] , 'items', 'jima_items.json'])

# 保存最终获得的手机号码信息保存文件
current_date = time.strftime('%Y-%m-%d', time.localtime(time.time()))
PHONE_FILE = sys.path[0] + os.path.sep + 'data' + os.path.sep + 'jima_phone_%s.txt' % (current_date)

# LOG
month = time.strftime('%Y-%m', time.localtime(time.time()))
LOG_FILE = os.path.sep.join([sys.path[0], 'log', 'jima_%s.log' % month])


class Jima(object):
    def __init__(self):
        self.api_prefix = API_PREFIX
        self.developer = DEVELOPER
        self.user_name = 'kkk321'
        self.user_pwd = 'kkk321'
        self.token = ''
        self.userid = '11744'
        self.phone_list = ''
        self.headers = {
            'Host': 'api.jima123.com',
            'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1',
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/56.0.2924.87 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Accept-Encoding': 'gzip, deflate, sdch',
            'Accept-Language': 'zh-CN,zh;q=0.8,en-US;q=0.6,en;q=0.4',
        }
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
                if r.status_code == 200 and r.json().get('errno') in ['0','3059']:
                    return r.json()
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
            'act': 'login',
            'username': self.user_name,
            'password': self.user_pwd,
            'developer': self.developer,
        }
        url = self.api_prefix
        # 登录失败需要重试
        while 1:
            login_res_json = self.request('get', url, payload)
            if login_res_json and login_res_json['errno'] == '0':
                self.token = login_res_json['data'][0]['token'].strip()
                self.userid = login_res_json['data'][0]['userid'].strip()
                if self.token != '':
                    self.logger.info(u'登录成功！')
                    return
            else:
                self.logger.info(u'登录失败！重试中。。。')
                time.sleep(1.5)

    # 获取项目
    def get_items(self):
        # 项目类型:
        #   0-收码
        #   1-发码
        #   4-多个收码
        #   5-多个发码

        payload = {
            'act': 'gettask',
            'userid': self.userid,
            'token': self.token,
        }
        url = self.api_prefix
        item_json = self.request('get', url, payload=payload)
        if item_json and item_json['errno'] == '0':         
            self.logger.info(u'获取项目列表OK')
            item_list = item_json['data']
            items = []
            for item in item_list:
                item_dict = {}
                item_dict['item_id'] = item['taskid']
                item_dict['item_name'] = item['taskname']
                item_dict['item_price'] = item['gold']
                item_dict['item_type'] = item['type']
                items.append(item_dict)
            return items

    # 获取区域
    def get_area(self):
        area_url = self.api_prefix
        payload = {
            'act': 'getarea',
            'userid': self.userid,
            'token': self.token,
        }
        area_res_json = self.request('get', area_url, payload)
        area_list = area_res_json['data']
        # 返回示例
        # {"errno":"0","errmsg":"OK","data":[
        #   {"provinceid":"11","province":"\u5317\u4eac\u5e02"},
        #   {"provinceid":"12","province":"\u5929\u6d25\u5e02"}
        #   ]
        #  }
        return area_list

    # 获取号码
    def get_num(self, item_id, count):
        # item_id: 项目ID
        # count: 获取手机号的数量
        
        payload = {
            'act': 'getmobile',     
            'userid': self.userid,  # 用户ID      必填
            'token': self.token,    # 登录token   必填
            'taskid': item_id,      # 项目代码     必填
            'mobile': '',           # 指定手机号
            'max': '',              # 最大单价[项目最高价]
            'min': '',              # 最小单价[项目最低价]
            'key': '',              # 专属对接，与卡商直接对接
            'count': str(count),    # 获取数量(默认为1，最大为10)
            'area': '',             # 区域(不填则随机)
            'operator': '',         # 运营商(不填为0, [0-随机][1-移动][2-联通][3-电信])
        }
        url = self.api_prefix
        num_json = self.request('get', url, payload)
        nums = []
        if num_json:
            self.logger.info('errno is : %s' % (num_json['errno']))
            if num_json['errno'] == '0':
                nums = [mobile_data['mobile'] for mobile_data in num_json['data']]
                add_str = '-%s;' % (item_id)
                self.phone_list = add_str.join(nums) + add_str.strip(';')
            elif num_json['errno'] == '3059':
                self.logger.info(num_json['errmsg'])
        return nums

    # 释放号码
    def release_phone(self):
        url = self.api_prefix
        payload = {
            'act': 'resmobile',
            'userid': self.userid,
            'token': self.token,
            'list': self.phone_list,
        }
        release_res_json = self.request('get', url, payload)
        if release_res_json['errno'] == '0':
            self.logger.info(u'释放号码成功!')

    # 释放号码
    def release_all_phone(self):
        url = self.api_prefix
        payload = {
            'act': 'resall',
            'userid': self.userid,
            'token': self.token,
        }
        resall_res_json = self.request('get', url, payload)
        if resall_res_json['errno'] == '0':
            self.logger.info(u'释放所有号码成功!')

    # 退出
    def exit(self):
        url = self.api_prefix
        payload = {
            'act': 'quit',
            'userid': self.userid,
            'token': self.token
        }
        exit_res_json = self.request('get', url, payload)
        if exit_res_json['errno'] == '0':
            self.logger.info(u'退出成功!')


def main():

    jima = Jima()
    jima.login()

    if os.path.exists(ITEMS_FILE):
        items = get_items_from_file(ITEMS_FILE)
        jima.logger.info(u'从文件中读取__%s__网站可接收验证码项目%d个。' % (
            str(jima.__class__).split('.')[1].strip("'>"), len(items)))
    else:
        items = jima.get_items()
        save_items(items, ITEMS_FILE)
        jima.logger.info(u'一共获取__%s__网站可接收验证码项目%d个。' % (
            str(jima.__class__).split('.')[1].strip("'>"), len(items)))

    for item in items:
        # 每个项目拿10次
        # 该网站会冻结账户
        for i in xrange(10):
            time.sleep(5.5)
            item_name = item.get('item_name')
            item_id = item.get('item_id')
            item_price = float(item.get('item_price'))
            item_type = item.get('item_type')
            jima.logger.info(u'项目: __%s__, ID: __%s__, 价格: __%s__' % (item_name, item_id, item_price))

            if item_id and item_price <= 10:
                nums = jima.get_num(item_id, 10)
                jima.logger.info(nums)
                if len(nums) == 0:
                    jima.logger.info(u'没有获取到有效号码')
                    jima.exit()
                    jima.login()
                    continue

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
                        'portal': u'基码',              # 来源门户
                    }
                    new_item = add_item_fields(phone_item)
                    phone_items.append(new_item)
                save_items(phone_items, PHONE_FILE)

                # 释放号码
                jima.release_all_phone()
            else:
                jima.logger.info(u'项目价格超过10元, 放弃.')
        
        # 释放号码
        jima.exit()
        # 重新登录, 刷新token
        jima.login()
    jima.logger.info(u'采集结束' + '-'*30)

if __name__ == '__main__':
    main()