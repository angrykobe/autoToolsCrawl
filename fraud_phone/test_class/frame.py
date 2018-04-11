# coding=utf-8
import os
import sys
import time
import logging
import requests
import gevent

from utils import save_items, get_items_from_file, add_item_fields, log_init, save_items_with_json

reload(sys)
sys.setdefaultencoding('utf8')

'''
账户基本信息
account_info = {
    'user_info': {
        u'用户名': '',
        u'用户类别': '',
        u'可同时登陆': '',
        u'可同时获取号码数': '',
        u'单个客户端获取号码数': '',
        u'折扣': '100%',        
        u'用户余额': '8.900',
        u'可提现金额': '0.000',
        u'真实姓名': '武松',
        u'支付宝': '1747485592',
        u'电子邮箱': '1747485591@qq.com',
        u'手机号码': '18926779674',
        u'QQ': '1747485592',
        u'注册日期': '',
    }

    u'author_uid': '8902',
}
'''


class BaseClass(object):
    def __init__(self):
        # 该参数用来存放该平台获取 项目列表 的地址
        self.item_url = ""
        self.api_prefix = r''
        self.author_uid = ''
        self.user_name = ''
        self.user_pwd = ''
        self.token = ''
        self.phone_list = ''
        self.headers = {

        }
        # 保存网站项目信息的文件

        website_name = "baseclass"

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

    def request(self, url, request_type, payload=None):
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
        url = self.api_prefix + ''
        payload = {}

        text = self.request(url=url, request_type="", payload=payload)

        self.token = ""

    def get_items(self):
        url = self.api_prefix + ''
        payload = {'token': self.token}
        # with api
        text = self.request(url=url, request_type="", payload=payload)

        # without api
        text = self.request(url=url, request_type="", payload=payload)

    def get_phone(self):
        url = self.api_prefix + ''
        payload = {'token': self.token}

        text = self.request(url=url, request_type="", payload=payload)

    def release_all_phone(self):
        url = self.api_prefix + ''
        payload = {'token': self.token}

        text = self.request(url=url, request_type="", payload=payload)

    def exit(self):
        url = self.api_prefix + ''
        payload = {'token': self.token}

        text = self.request(url=url, request_type="", payload=payload)


def main():
    pass


if __name__ == '__main__':
    main()
