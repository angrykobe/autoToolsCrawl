# coding=utf-8
import os
import sys
import time
import json
import gevent
import logging
import requests

from utils import save_items, get_items_from_file, add_item_fields, log_init, save_items_with_json

reload(sys)
sys.setdefaultencoding('utf8')

# 商码(http://ma.d4z.cn/index/index/index.html)
# 账号/密码: hbbhbb(rfM#!EzZU%!3s7*kxbTy)
# 平台接口前缀: 'http://ma.d4z.cn'
'''
账户基本信息
account_info = {
    'user_info': {
        u'用户名': 'hbbhbb',
        u'用户级别': 'VIP1',
        u'可同时获取号码数': '16',
        u'折扣': '100%',
        u'积分': '0',
        u'用户余额': '0',        
        u'可提现余额': '0',
        u'真实姓名': '0',
        u'支付宝': '0',
        u'电子邮箱': '1634250628@qq.com',
        u'手机号码': '18565748011',
        u'QQ': '1634250628',
    }

    u'Developer': 'hbbhbb',
}
'''


class Mad4z(object):
    def __init__(self):
        self.api_prefix = r'http://ma.d4z.cn'
        self.author_uid = ''
        self.user_name = 'hbbhbb'
        self.user_pwd = 'rfM#!EzZU%!3s7*kxbTy'
        self.token = ''
        self.phone_list = ''
        self.headers = {
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8",
            "Accept-Encoding": "gzip, deflate",
            "Accept-Language": "zh-CN,zh;q=0.9",
            "Cache-Control": "max-age=0",
            "Connection": "keep-alive",
            "Host": "ma.d4z.cn",
            "Upgrade-Insecure-Requests": "1",
            "User-Agent": "Mozilla/5.0 (Windows NT 6.1; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/63.0.3239.108 Safari/537.36"
        }
        # 保存网站项目信息的文件

        website_name = "mad4z"

        items_file_name = '{website_name}_items.json'.format(website_name=website_name)
        self.items_file = os.path.join(sys.path[0], 'items', items_file_name)

        # 保存最终获得的手机号码信息保存文件
        current_date = time.strftime('%Y-%m-%d', time.localtime(time.time()))
        phone_file_name = "{website_name}_phone_{date}.txt".format(website_name=website_name, date=current_date)
        self.phone_file = os.path.join(sys.path[0], "data", phone_file_name)
        # self.phone_file = sys.path[0] + os.path.sep + 'data' + os.path.sep + 'goodyzm_phone_%s.txt' % (current_date)

        # LOG
        month = time.strftime('%Y-%m', time.localtime(time.time()))
        log_file_name = '{website_name}_{month}.log'.format(website_name=website_name, month=month)
        self.log_file = os.path.join(sys.path[0], 'log', log_file_name)

        save_items([], self.phone_file)
        log_name = self.__class__.__name__
        log_init(log_name, self.log_file)
        self.logger = logging.getLogger(log_name)
        self.logger.info(u'开始采集' + '-' * 30)

    # 统一处理请求部分
    def request(self, url, request_type, payload=None):
        # url: 请求地址
        # request_type: 请求类型
        # payload: 请求参数

        retry_time = 0

        while 1:
            try:
                with gevent.Timeout(10, requests.Timeout):
                    try:
                        if request_type == "post" or request_type == "POST":
                            response = requests.post(url=url, headers=self.headers, data=payload, allow_redirects=False)
                        else:
                            response = requests.get(url=url, headers=self.headers, params=payload, allow_redirects=False)

                        if not response.text:
                            retry_time += 1

                            logging.info(u"返回内容为空，重试中。。。")

                            if retry_time > 3:
                                pass
                            else:
                                return ""

                        if response.status_code == 200:

                            return response.text
                        else:
                            logging.info(u"状态码是 {status_code}, 返回空内容。".format(status_code=response.status_code))

                            return ""

                    except requests.Timeout:
                        retry_time += 1
                        logging.info(u"连接超时，重试中。。。")

                        if retry_time > 3:
                            pass
                        else:
                            continue
            except requests.Timeout:
                retry_time += 1
                logging.info(u"连接超时，重试中。。。")

                if retry_time > 3:
                    pass
                else:
                    continue
            except Exception as e:
                print(e)

    # 登录, 获得用户token
    def login(self):
        url = self.api_prefix + '/Login'
        payload = {
            "User": self.user_name,         # 用户名
            "Password": self.user_pwd,      # 对应的密码
            "Logintype": "0"                # 登录类型，固定为0
        }

        text = self.request(url=url, request_type="get", payload=payload)

        if text:
            try:
                json_text = json.loads(text)

                if not (json_text["code"] == "0" or json_text["code"] == 0):
                    raise Exception(json_text["msg"])

                self.token = json_text["data"]["Token"]

                self.logger.info(u'登录成功！')
            except Exception as e:
                self.logger.info(u'登录失败！{msg}'.format(msg=e.message))

    # 获取项目
    def get_items(self):
        # 返回格式
        # [{"ItemId":项目ID,"ItemName":项目名称,"ItemPrice":项目价格,"ItemType":项目类型},...]
        # 项目类型:
        #   0  表示此项目用于接收验证码
        #   1  表示此项目用户发送短信
        #   2  表示此项目即可接收验证码，也可以发送短信

        url = self.api_prefix + "/GetAllItem"

        text = self.request(url=url, request_type="get")
        items = []

        if text:
            json_text = json.loads(text)

            if not (json_text["code"] == "0" or json_text["code"] == 0):
                self.logger.info(u'获取项目列表失败！{msg}'.format(msg=json_text["msg"]))

            for item in json_text["data"]:

                item_dict = dict(zip(
                    ['item_id', 'item_name', 'item_price', 'item_type'],
                    [item["ItemId"], item["ItemName"], item["ItemPrice"], item["ItemType"]]))

                item_type = item_dict.get('item_type')
                if item_type is not None:
                    items.append(item_dict)

            return items

    # 获取号码
    def get_phone(self, item_id, phone=None):
        # item_id: 项目ID

        url = self.api_prefix + '/GetPhoneNumber'
        payload = {
            'Token': self.token,
            "ItemId": item_id,
            'Phone': phone,
            'Operator': ""  # 运营商 [不填为 0] 0 [随机] 1 [移动] 2 [联通] 3 [电信] 4[虚拟运营商] 5[非虚拟运营商]
                            # 12 [越南12开头号码] 16 [越南16开头号码] 9 [越南9开头号码]
        }

        text = self.request(url=url, request_type="get", payload=payload)

        phones = []
        msgids = []

        if text:
            json_text = json.loads(text)

            try:
                if not (json_text["code"] == "0" or json_text["code"] == 0):
                    self.logger.info(u'获取手机号码失败！{msg}'.format(msg=json_text["msg"]))

                phones = [json_text["data"]["Phone"]]
                msgids = [json_text["data"]["MSGID"]]

            except Exception:
                self.logger.info(u'获取手机号码失败！')

        return phones, msgids

    # 添加号码到黑名单
    def add_black_list(self, msgid):
        url = self.api_prefix + '/AddBlackPhone'
        payload = {
            'Token': self.token,
            "MSGID": msgid
        }

        text = self.request(url=url, request_type="get", payload=payload)
        phones = []

        if text:
            try:
                json_text = json.loads(text)

                if not (json_text["code"] == "0" or json_text["code"] == 0):
                    raise Exception(json_text["msg"])

                self.logger.info(u'加黑指定手机号码成功！')
            except Exception as e:
                self.logger.info(u'加黑指定手机号码失败！{msg}'.format(msg=e.message))

        return phones

    # 获取指定号码
    def get_specific_phone(self, item_id, phone):
        return self.get_phone(item_id=item_id, phone=phone)

    # 释放全部号码
    def release_all_phone(self):
        url = self.api_prefix + '/AllRelease'
        payload = {'Token': self.token}

        text = self.request(url=url, request_type="", payload=payload)

        if text:
            json_text = json.loads(text)

            try:
                if not (json_text["code"] == "0" or json_text["code"] == 0):
                    raise Exception

                self.logger.info(u'释放所有手机号码成功！')

            except Exception as e:
                self.logger.info(u'释放所有手机号码失败！{msg}'.format(msg=e.message))

    # 退出
    def exit(self):
        self.logger.info(u'退出成功!')


def main():
    mad4z = Mad4z()
    mad4z.login()
    mad4z.release_all_phone()

    if os.path.exists(mad4z.items_file):
        items = get_items_from_file(mad4z.items_file)
        mad4z.logger.info(u'从文件中读取__%s__网站可接收验证码项目%d个。' % (
            str(mad4z.__class__).split('.')[1].strip("'>"), len(items)))
    else:
        items = mad4z.get_items()
        save_items_with_json(items, mad4z.items_file)
        mad4z.logger.info(u'一共获取__%s__网站可接收验证码项目%d个。' % (
            str(mad4z.__class__).split('.')[1].strip("'>"), len(items)))

    for item in items[:]:
        max_time_per_item = 1000
        retry_time_per_item = 0
        phones_per_item_set = set()

        saved_count = 0
        replicate_count = 0

        three_increase = [1, 1, 1]
        increase_length = 0

        empty_count = 0

        while 1:
            if replicate_count > 15 or retry_time_per_item >= max_time_per_item or empty_count >= 10:
                break
            item_name = item.get('item_name')
            item_id = item.get('item_id')
            item_price = float(item.get('item_price'))
            item_type = item.get('item_type')
            mad4z.logger.info(u'项目: __%s__, ID: __%s__, 价格: __%s__' % (item_name, item_id, item_price))

            if item_id and item_price <= 1:
                # if item_price <= 0.5:
                #     count = 20
                # else:
                #     count = int(10.0/item_price)

                num, msgid = mad4z.get_phone(item_id)

                mad4z.logger.info(num)
                if len(num) == 0:
                    empty_count += 1
                    mad4z.logger.info(u'没有获取到有效号码')
                    continue

                # 同一个item_id查询出的不重复的号码
                last_length = len(phones_per_item_set)
                phones_per_item_set.add(num[0])
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
                    'phone': num[0],                # 手机号
                    'portal': u'商码',              # 来源门户
                }
                new_item = add_item_fields(phone_item)

                mad4z.add_black_list(msgid[0])

                phone_items.append(new_item)

                if increase_length > 0:
                    save_items(phone_items, mad4z.phone_file)
                    saved_count += 1

                mad4z.release_all_phone()
                retry_time_per_item += 1

                # 依据重复次数判断该项目的卡号已被大致取完
                replicate_count += (1 - increase_length)

                three_increase[2] = three_increase[1]
                three_increase[1] = three_increase[0]
                three_increase[0] = increase_length
                print three_increase

                # 退出, 让token失效
                mad4z.exit()
                # 重新登录, 刷新token
                mad4z.login()
            else:
                mad4z.logger.info(u'项目价格超过10元, 放弃.')
                break
        print "",

    mad4z.logger.info(u'采集结束' + '-' * 30)


if __name__ == '__main__':
    main()
