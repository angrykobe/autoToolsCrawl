# coding=utf-8
import os
import re
import sys
import time
import json
import codecs
import random
import logging
import requests
import websocket

from scrapy.selector import Selector
from utils import save_items, get_items_from_file, add_item_fields, log_init, save_items_with_json

reload(sys)
sys.setdefaultencoding('utf8')

'''
账户基本信息
account_info = {
    'user_info': {
        u'用户名称': 'hbbhbb',
        u'用户等级': '普通用户',
        u'联系电话': '18914118010',
        u'邮箱': '24481586@qq.com',
        u'积分': '0',
        u'余额': '无',        
    }
}
'''


class Make02(object):
    def __init__(self):
        # 该参数用来存放该平台获取 项目列表 的地址
        self.api_prefix = r'ws://api.make02.com:7272'
        self.user_name = 'hbbhbb'
        self.user_pwd = 'hbb123'
        self.token = ''
        self.phone_list = ''
        self.headers = {
            "Host": "www.make02.com",
            "Connection": "keep-alive",
            "Upgrade-Insecure-Requests": "1",
            "User-Agent": "Mozilla/5.0 (Windows NT 6.1; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/63.0.3239.108 Safari/537.36",
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8",
            "Referer": "http://www.make02.com/index.php/Member/index/LeftPart",
            "Accept-Encoding": "gzip, deflate",
            "Accept-Language": "zh-CN,zh;q=0.9"
        }
        self._login_websocket()
        # 保存网站项目信息的文件

        website_name = "make02"

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

    def _login_websocket(self):
        self.ws = websocket.WebSocket()
        self.ws.connect(url=self.api_prefix)
        self._login()

    # 登录, 获得用户token
    def _login(self):
        msg = {
            'message_type': 'D_DP_DL_001',
            'user_name': self.user_name,
            'password': self.user_pwd
        }
        r = self.request(msg)
        self.token = json.loads(r)['token']

    # 统一处理请求部分
    def request(self, msg):
        # url: 请求地址
        # request_type: 请求类型
        # payload: 请求参数

        msg = json.dumps(msg)
        try:
            self.ws.send(payload=msg)
            result = self.ws.recv()
        except Exception as err:
            try:
                self._login_websocket()
            except Exception as e:
                return ''
            else:
                return self.request(msg)
        return result

    def login_website(self):
        session = requests.session()
        url = 'http://www.make02.com/index.php/Member/Member/login'
        data = {
            'user_type': '1',
            'username': self.user_name,
            'password': self.user_pwd,
            'submit': u'登录'
        }
        r = session.post(url=url, data=data, headers=self.headers).text
        regex = re.compile(u'手机验证码管理平台')
        if regex.findall(r):
            return session

    @staticmethod
    def login():
        return True

    def get_items(self, p=1):
        session = self.login_website()
        url_prefix = 'http://www.make02.com/index.php/Member/Item/index/p/%s.html'

        items = []
        max_page = 2
        is_max_page_change = False

        while p <= max_page:
            url = url_prefix % str(p)
            r = session.get(url=url, headers=self.headers)

            if max_page == 2 and is_max_page_change is False:
                total_num_of_page = re.findall(ur"共(\d+)页", r.text)
                if total_num_of_page:
                    max_page = int(total_num_of_page[0])
                    is_max_page_change = True

            items.extend(self.parse_item_info(r))

            p += 1

        return items

    @staticmethod
    def parse_item_info(response):
        selector = Selector(text=response.text)

        tr_selectors = selector.css("table tbody tr")

        items = []
        for tr_selector in tr_selectors:
            tds = tr_selector.css("td::text").extract()

            item = {
                'item_id': tds[0],
                'item_name': tds[1],
                'item_type': tds[2],
                'item_price': tds[3]
            }

            item['item_type'] = {u'接收': 1, u'发送': 2, u'发送和接收': 3}.get(item['item_type'], 0)
            item['item_price'] = item['item_price'].split("&")[0]

            items.append(item)

        return items

    def get_phone(self, item_id, count=10, phone=None):
        msg = {
            'message_type': 'M_GG_SF_009',
            'token': self.token,
            'item_id': item_id,
            'num': str(count),
            'op': '0',          # 1 新卡， 0 普通
            'provider': '',     # 运营商
            'provinceid': '',   # 省编码
            'cityid': '',       # 城市编码
            'telphone': phone   # 获取指定某个号码
        }
        phones = []
        r = json.loads(self.request(msg))

        if r.get('data'):
            try:
                phones.append(r.get('data')[0]['telphone'])
            except KeyError as err:
                print(str(err))
        return phones

    def release_all_phone(self):
        msg = {
            'message_type': 'D_SF_HM_001',
            'token': self.token
        }
        text = self.request(msg)

        try:
            if text:

                json_text = json.loads(text)

                if json_text["code"] == 0:
                    self.logger.info(u'释放全部号码成功')
                else:
                    raise Exception
            else:
                raise Exception
        except Exception:
            self.logger.info(u'释放全部号码失败')

    def exit(self):
        self.logger.info(u'退出成功。')


def main():
    make02 = Make02()
    make02.login()
    make02.release_all_phone()

    if os.path.exists(make02.items_file):
        items = get_items_from_file(make02.items_file)
        make02.logger.info(u'从文件中读取__%s__网站可接收验证码项目%d个。' % (
            str(make02.__class__).split('.')[1].strip("'>"), len(items)))
    else:
        items = make02.get_items()
        save_items_with_json(items, make02.items_file)
        make02.logger.info(u'一共获取__%s__网站可接收验证码项目%d个。' % (
            str(make02.__class__).split('.')[1].strip("'>"), len(items)))

    for item in items[:]:
        max_time_per_item = 1000
        retry_time_per_item = 0
        phones_per_item_set = set()
        # 最近三次不重复号码总量增长
        three_increase = [10, 10, 10]
        increase_length = 0

        while 1:
            if sum(three_increase) < 5 or retry_time_per_item >= max_time_per_item:
                break
            # time.sleep(1.5)
            item_name = item.get('item_name')
            item_id = item.get('item_id')
            item_price = float(item.get('item_price'))
            item_type = item.get('item_type')
            make02.logger.info(u'项目: __%s__, ID: __%s__, 价格: __%s__' % (item_name, item_id, item_price))

            if item_price <= 10:
                if item_price > 1:
                    count = int(10 / item_price)
                else:
                    count = 10
                nums = make02.get_phone(item_id, count)
                make02.logger.info(nums)
                if len(nums) == 0:
                    make02.logger.info(u'没有获取到有效号码！')

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
                        'item_name': item_name,      # 项目名称
                        'item_id': item_id,          # 项目ID
                        'crawl_time': current_time,  # 采集时间
                        'item_price': item_price,    # 项目价格
                        'item_type': item_type,      # 项目类型
                        'phone': num,                # 手机号
                        'portal': u'码客',           # 来源门户
                    }

                    new_item = add_item_fields(phone_item)
                    phone_items.append(new_item)
                if len(phone_items) > 0:
                    save_items(phone_items, make02.phone_file)

                # 释放号码
                make02.release_all_phone()
                # 重新登录, 刷新token
                make02.login()
            else:
                make02.logger.info(u'项目价格超过10元, 放弃！')
            retry_time_per_item += 1

            # 依据重复率判断是否需要结束当前item_id的重复尝试
            three_increase[2] = three_increase[1]
            three_increase[1] = three_increase[0]
            three_increase[0] = increase_length
            print three_increase

    # 退出登录
    make02.exit()

    make02.logger.info(u'采集结束' + '-' * 30)


if __name__ == '__main__':
    main()
