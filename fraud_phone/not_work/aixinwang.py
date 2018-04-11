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

# 爱信码(http://www.ixinsms.com/index.html)
# 账号/密码: hbbhbb(rfM#!EzZU%!3s7*kxbTy)
# 平台接口前缀: 'http://api.ixinsms.com/api/do.php?action='
'''
账户基本信息
account_info = {
    'user_info': {
        u'当前账号': 'hbbhbb',
        u'余额': '0',
        u'充值总额': '0',
        u'分成总额': '0',
        u'可提现金额': '0',
        u'积分': '0',        
        u'等级': '普通会员',
        u'最大取号数': '50',
        u'QQ号码': '1634250628',
        u'E-mail': '1634250628@qq.com',
        u'支付宝账号': '',
        u'姓名': '',
    }
}
'''


class AiXinWang(object):
    def __init__(self):
        # 该参数用来存放该平台获取 项目列表 的地址
        self.item_url = "http://client.ixinsms.com"
        self.api_prefix = r'http://api.ixinsms.com/api/do.php?action='
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
            "Host": "api.ixinsms.com",
            "Upgrade-Insecure-Requests": "1",
            "User-Agent": "Mozilla/5.0 (Windows NT 6.1; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/63.0.3239.108 Safari/537.36"
        }
        # 保存网站项目信息的文件

        website_name = "aixinwang"

        items_file_name = '{website_name}_items.json'.format(website_name=website_name)
        self.items_file = os.path.join(sys.path[0], 'items', items_file_name)

        # 保存最终获得的手机号码信息保存文件
        current_date = time.strftime('%Y-%m-%d', time.localtime(time.time()))
        phone_file_name = "{website_name}_phone_{date}.txt".format(website_name=website_name, date=current_date)
        self.phone_file = os.path.join(sys.path[0], 'data', phone_file_name)

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
                        if "api" in url:
                            self.headers['Host'] = "api.ixinsms.com"
                        else:
                            self.headers['Host'] = "client.ixinsms.com"

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
        url = self.api_prefix + 'loginIn'
        payload = {
            "name": self.user_name,         # 用户名
            "password": self.user_pwd       # 密码
        }

        text = self.request(url=url, request_type="get", payload=payload)

        if text:
            try:
                status_code, token = text.split("|")

                if status_code == "0":
                    raise Exception

                self.token = token

                self.logger.info(u'登录成功！')
            except Exception:
                self.logger.info(u'登录失败！')

    # 获取项目
    def get_items(self):
        # 返回格式
        # [{"isFavorite":是否收藏,"projectId":项目ID,"projectName":项目名称,"projectPrice":项目价格,"projectStatus":项目状态,"projectType":项目类型,"remark":项目备注,"webSite":项目网站},...]
        # 项目类型:
        #   0.  无意义

        url = self.item_url + "cApi"
        payload = {
            'token': self.token,
            'action': "searchProject",
            'keyword': u"[a-z0-9贷金融理财网富服所投宝钱易线创汇信贷众资银]"
        }

        text = self.request(url=url, request_type="get", payload=payload)
        items = []

        if text:
            json_text = json.loads(text)

            if json_text["code"] != "111":
                self.logger.info(json_text["msg"])
            else:
                for item in json_text["data"]:

                    item_dict = dict(zip(
                        ['item_id', 'item_name', 'item_price', 'item_type'],
                        [item["projectId"], item["projectName"], item["projectPrice"], item["projectType"]]))

                    item_type = item_dict.get('item_type')
                    if item_type is not None:
                        items.append(item_dict)

                return items

    # 获取号码
    def get_phone(self, item_id, count=20):
        url = self.api_prefix + 'getPhone'
        payload = {
            'token': self.token,        # 登录时返回的令牌
            "sid": item_id,             # 项目ID
            "size": str(count),         # 可选, 要获取手机号数量
            "phone": "",                # 可选, 要指定获取的号码,传入号码不正确的情况下,获取新号码
            "phoneType": "",            # 可选, CMCC是指移动，UNICOM是指联通，TELECOM是指电信
            "vno": "",                  # 可选, 0是指排除所有虚拟运营商号码，1是只获取虚拟运营商号码，如果没有需求，则不用传入此参数
            "locationMatching": "",     # 可选, include为包含区域, exclude为排除区域
            "locationLevel": "",        # 可选, p或c, 指代省份或城市
            "location": "",             # 可选，与上一个参数对应的省份或城市，url编码后的中文字符，以上三个参数需搭配使用
        }

        text = self.request(url=url, request_type="get", payload=payload)
        phones = []

        if text:
            try:
                status_code, phones_str = text.split("|")

                if status_code == "0":
                    raise Exception

                phones = phones_str.split(",")

            except Exception:
                pass

        return phones

    # 添加号码到黑名单
    def add_black_list(self, item_id, phone):
        url = self.api_prefix + 'addBlacklist'
        payload = {
            'token': self.token,
            "sid": item_id,
            "phone": str(phone)
        }

        text = self.request(url=url, request_type="get", payload=payload)
        phones = []

        if text:
            try:
                status_code, msg = text.split("|")

                if status_code == "0":
                    raise Exception(msg)

                self.logger.info(u'加黑指定手机号码成功！')
            except Exception as e:
                self.logger.info(u'加黑指定手机号码失败！{msg}'.format(msg=e.message))

        return phones

    # 根据指定项目获取指定的手机号码
    def get_specific_phone(self, item_id, phone):
        url = self.api_prefix + 'getPhone'
        payload = {
            'token': self.token,        # 登录时返回的令牌
            "sid": item_id,             # 项目ID
            "size": "",                 # 可选, 要获取手机号数量
            "phone": str(phone),        # 可选, 要获取手机号数量
            "phoneType": "",            # 可选, CMCC是指移动，UNICOM是指联通，TELECOM是指电信
            "vno": "",                  # 可选, 0是指排除所有虚拟运营商号码，1是只获取虚拟运营商号码，如果没有需求，则不用传入此参数
            "locationMatching": "",     # 可选, include为包含区域, exclude为排除区域
            "locationLevel": "",        # 可选, p或c, 指代省份或城市
            "location": "",             # 可选，与上一个参数对应的省份或城市，url编码后的中文字符，以上三个参数需搭配使用
        }

        text = self.request(url=url, request_type="get", payload=payload)
        phones = []

        if text:
            try:
                status_code, phones_str = text.split("|")

                if status_code == "0":
                    raise Exception(phones_str)

                phones = phones_str.split(",")

            except Exception as e:
                self.logger.info(u'获取指定手机号码失败！{msg}'.format(msg=e.message))

        return phones

    # 释放全部号码
    def release_phone(self):
        url = self.api_prefix + 'cancelAllRecv'
        payload = {'token': self.token}

        text = self.request(url=url, request_type="", payload=payload)

        if text:
            try:
                status_code, msg = text.split("|")

                if status_code == "0":
                    raise Exception(msg)

                self.logger.info(u'释放所有手机号码成功！')

            except Exception as e:
                self.logger.info(u'释放所有手机号码失败！{msg}'.format(msg=e.message))

    # 退出
    def exit(self):
        self.logger.info(u'退出成功!')


def main():
    aixinwang = AiXinWang()
    aixinwang.login()
    aixinwang.release_phone()

    if os.path.exists(aixinwang.items_file):
        items = get_items_from_file(aixinwang.items_file)
        aixinwang.logger.info(u'从文件中读取__%s__网站可接收验证码项目%d个。' % (
            str(aixinwang.__class__).split('.')[1].strip("'>"), len(items)))
    else:
        items = aixinwang.get_items()
        save_items_with_json(items, aixinwang.items_file)
        aixinwang.logger.info(u'一共获取__%s__网站可接收验证码项目%d个。' % (
            str(aixinwang.__class__).split('.')[1].strip("'>"), len(items)))

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
            aixinwang.logger.info(u'项目: __%s__, ID: __%s__, 价格: __%s__' % (item_name, item_id, item_price))

            if item_id and item_price <= 1:
                count = int(1.0 / item_price)

                nums = aixinwang.get_phone(item_id, count)
                aixinwang.logger.info(nums)
                if len(nums) == 0:
                    aixinwang.logger.info(u'没有获取到有效号码')

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
                        'portal': u'爱信网',            # 来源门户
                    }
                    new_item = add_item_fields(phone_item)
                    phone_items.append(new_item)
                if len(phone_items) > 0:
                    save_items(phone_items, aixinwang.phone_file)
                    aixinwang.release_phone()

                # 退出, 让token失效
                aixinwang.exit()
                # 重新登录, 刷新token
                aixinwang.login()
            else:
                aixinwang.logger.info(u'项目价格超过10元, 放弃.')
            retry_time_per_item += 1

            # 依据重复率判断是否需要结束当前item_id的重复尝试
            three_increase[2] = three_increase[1]
            three_increase[1] = three_increase[0]
            three_increase[0] = increase_length
            print three_increase
    aixinwang.logger.info(u'采集结束' + '-' * 30)


if __name__ == '__main__':
    main()
