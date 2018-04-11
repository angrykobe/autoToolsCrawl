# encoding: utf-8

# 土豆
# http://www.6tudou.com:9000/adminlogin.html
# 账号： next (密码： mmjj4321)
# api 文档  http://www.6tudou.com:9000/Download.html
# 编码 utf-8
import json
import os
import random
import sys
import time
import requests
import codecs
import logging
from requests.exceptions import ConnectionError
from utils import save_items, get_items_from_file, add_item_fields, log_init, save_items_with_json


reload(sys)
sys.setdefaultencoding('utf8')


class Tudou():
    def __init__(self):
        self.api_prefix = "http://www.6tudou.com:9000/devapi/"
        self.user_name = 'next'
        self.user_pwd = 'mmjj4321'
        self.uid = ''
        self.token = ''
        self.headers = {
            'content-type': "multipart/form-data; boundary=----WebKitFormBoundary7MA4YWxkTrZu0gW",
            'accept': "image/webp,image/*,*/*;q=0.8",
            'accept-encoding': "gzip, deflate, sdch",
            'accept-language': "zh-CN,zh;q=0.8",
            'cache-control': "no-cache",
            'host': "www.6tudou.com:9000",
            'pragma': "no-cache",
            'proxy-connection': "keep-alive",
            'referer': "http://www.6tudou.com:9000/adminlogin.html",
            'user-agent': "Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.96 Safari/537.36",
        }

        # 保存网站项目信息的文件
        self.items_file = os.path.sep.join([sys.path[0], 'items', 'tudou_items.json'])

        # 保存最终获得的手机号码信息保存文件
        current_date = time.strftime('%Y-%m-%d', time.localtime(time.time()))
        self.phone_file = os.path.sep.join([sys.path[0], 'data', 'tudou_phone_%s.txt' % (current_date)])

        # LOG
        month = time.strftime('%Y-%m', time.localtime(time.time()))
        self.log_file = os.path.sep.join([sys.path[0], 'log', 'tudou_%s.log' % month])

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

    def get_items(self):
        url = "http://www.6tudou.com:9000/DevApi/GetCategoryList"
        data = {
            'uid': self.uid,
            'token': self.token
        }
        r = self.request(request_type='post', url=url, payload=data)
        items = []

        item_list = json.loads(r)
        for item in item_list:
            item_dict = dict(zip(
                ['item_id', 'item_name', 'item_price', 'item_type'],
                [item.get("CategoryID"), item.get("Name"),
                 item.get("Price"), item.get("CategoryType")]))

            items.append(item_dict)

        return items

    def login(self):
        url = self.api_prefix + 'loginIn'
        params = {
            'uid': self.user_name,
            'pwd': self.user_pwd
        }
        r = self.request(request_type='get', url=url, payload=params)
        login_info = json.loads(r)
        try:
            self.uid = login_info['Uid']
            # 由于编码问题， 需要把 %2B 替换为 +
            self.token = login_info['Token'].replace('%2B', '+')
            self.logger.info(u'登录成功！')
            return True
        except KeyError, e:
            self.logger.info(u'登录失败！')
            return False

    # 获取一个手机号
    def get_phone(self, item_id, count=1, phone=None):
        url = self.api_prefix + 'getMobilenum'
        params = {
            'uid': self.uid,
            'pid': item_id,
            'Token': self.token,
            'assgin': phone,  # 指定手机号，选填
            'type': '',  # 运营商类型，选填
            'province': '',  # 地区, 使用url中文编码，选填
            'channelId': '',  # 通道秘钥， 选填
            'nonVirtual': ''  # 非虚拟17号段，选填
        }
        num_text = self.request(request_type='get', url=url, payload=params)  # 返回字符串
        '''
        No_Data表示暂无号码，或提示余额不足|获取指定号码
        （返回Yes_Can号码可用，No_Can不可用，No_Exist号码不存在）'''

        '''
        返回格式改变
        '''
        if num_text:
            if u'False:' in num_text:
                self.login()
            else:
                return num_text

        if num_text in ['No_Exist', 'No_Data', u'余额不足|获取指定号码']:
            return []
        print (num_text)
        return []

    def release_all_phone(self):
        pass

    def exit(self):
        pass

    # def main(self):
    #     self.login()
    #     f = codecs.open(self.items_file)
    #     lines = f.readlines()
    #     for line in lines:
    #         item_id = json.loads(line)['item_id']
    #         phones = self.get_phone(item_id)
    #         print phones
    #         time.sleep(1)


def main():
    tudou = Tudou()
    tudou.login()

    if os.path.exists(tudou.items_file):
        items = get_items_from_file(tudou.items_file)
        tudou.logger.info(u'从文件中读取__%s__网站可接收验证码项目%d个。' % (
            str(tudou.__class__).split('.')[1].strip("'>"), len(items)))
    else:
        items = tudou.get_items()
        save_items_with_json(items, tudou.items_file)
        tudou.logger.info(u'一共获取__%s__网站可接收验证码项目%d个。' % (
            str(tudou.__class__).split('.')[1].strip("'>"), len(items)))

    for item in items[:]:
        max_time_per_item = 1000
        retry_time_per_item = 0
        phones_per_item_set = set()

        increase_length = 0

        saved_count = 0
        replicate_count = 0

        empty_count = 0

        while 1:
            if replicate_count > 15 or retry_time_per_item >= max_time_per_item or empty_count >= 10:
                break
            item_name = item.get('item_name')
            item_id = item.get('item_id')
            item_price = float(item.get('item_price'))
            item_type = item.get('item_type')
            tudou.logger.info(u'项目: __%s__, ID: __%s__, 价格: __%s__' % (item_name, item_id, item_price))

            if item_id and item_price <= 10:
                # if item_price <= 0.5:
                #     count = 20
                # else:
                #     count = int(10.0/item_price)

                num = tudou.get_phone(item_id)
                tudou.logger.info(num)
                if len(num) == 0:
                    empty_count += 1
                    tudou.logger.info(u'没有获取到有效号码')
                    continue

                # 同一个item_id查询出的不重复的号码
                last_length = len(phones_per_item_set)
                phones_per_item_set.add(num)
                current_length = len(phones_per_item_set)
                increase_length = current_length - last_length

                phone_items = []
                current_time = time.strftime(
                    '%Y-%m-%d %H:%M:%S', time.localtime(time.time()))

                phone_item = {
                    'item_name': item_name,         # 项目名称
                    'item_id': item_id,             # 项目ID
                    'crawl_time': current_time,     # 采集时间
                    'item_price': item_price,       # 项目价格
                    'item_type': item_type,         # 项目类型
                    'phone': num,                   # 手机号
                    'portal': u'土豆',              # 来源门户
                }
                new_item = add_item_fields(phone_item)
                phone_items.append(new_item)

                if increase_length > 0:
                    save_items(phone_items, tudou.phone_file)
                    saved_count += 1

                retry_time_per_item += 1

                # 依据重复次数判断该项目的卡号已被大致取完
                replicate_count += (1 - increase_length)

                print replicate_count,

                # 退出, 让token失效
                tudou.exit()
                # 重新登录, 刷新token
                tudou.login()
            else:
                tudou.logger.info(u'项目价格超过10元, 放弃.')
        print "",

    tudou.logger.info(u'采集结束' + '-' * 30)


if __name__ == '__main__':
    main()
