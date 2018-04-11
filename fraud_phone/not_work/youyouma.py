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
        u'用户类别' : 'vip0',
        u'可同时登录' : '10',
        u'可同时获取号码数' : '100',
        u'单个客户端获取号码数' : '20',
        u'折扣' : '100%',
        u'用户余额' : '0.000',
        u'可提现余额' : '0.000',
        u'积分' : '0.00',
        u'真实姓名' : '刘岩',
        u'支付宝' : '18914118010',
        u'电子邮箱' : '24481586@qq.com',
        u'手机号码' : '18914118010',
        u'QQ' : '24481586',
        u'注册日期' : '2017/9/19 15:38:41
    }

    u'Developer': 'VspVotbesY8%3d',
}
'''


class YouYouMa(object):
    def __init__(self):
        # 该参数用来存放该平台获取 项目列表 的地址
        self.api_prefix = r'http://api.youyouyzm.com'
        self.developer = r'VspVotbesY8%3d'
        self.user_name = 'hbbhbb'
        self.user_pwd = 'hbb123'
        self.token = ''
        self.phone_list = ''
        self.headers = {
            'Host': 'api.youyouyzm.com',
            'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1',
            'User-Agent': 'Mozilla/5.0 (Linux; Android 6.0; Nexus 5 Build/MRA58N) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/63.0.3239.108 Mobile Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8',
            'Accept-Encoding': 'gzip, deflate',
            'Accept-Language': 'zh-CN,zh;q=0.9',
        }
        # 保存网站项目信息的文件

        website_name = "youyouma"

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
                        if request_type in ["post", "POST"]:
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
                        elif response.status_code == 504:
                            self.logger.info(u'网关超时, 休眠5秒。')
                            time.sleep(5)
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
            "uName": self.user_name,
            "pWord": self.user_pwd,
            "Developer": self.developer
        }

        token_text = self.request(url=url, request_type="get", payload=payload)

        if token_text:
            self.token = token_text.strip().split('&')[0]
            if self.token != '':
                self.logger.info(u'登录成功！')
        else:
            self.logger.info(u'登录失败！')

    # 获取区域
    def get_area(self):
        url = 'http://api.youyouyzm.com/GetArea?'
        area_res_text = self.request(url=url, request_type="get")

        area_list = area_res_text.split('\n')
        return area_list

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

        url = self.api_prefix + '/GetItems'

        item_text = self.request(url=url, request_type="get", payload=payload)

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
        }
        url = self.api_prefix + '/getPhone'
        num_text = self.request(url=url, request_type="get", payload=payload)

        phones = []

        if num_text:
            if u'False:' in num_text:
                self.login()
            else:
                phones = num_text.split(';')[:-1]
                add_str = '-%s;' % (item_id, )
                self.phone_list = add_str.join(phones) + add_str

        return phones

    # 释放全部号码
    def release_phone(self):
        url = self.api_prefix + '/releasePhone'
        payload = {
            'token': self.token,
            'phoneList': self.phone_list,
        }

        text = self.request(url=url, request_type="get", payload=payload)

        if text:
            self.logger.info(u'释放号码: %s' % (text, ))

    # 退出
    def exit(self):
        url = self.api_prefix + '/Exit'
        payload = {'token': self.token}

        text = self.request(url=url, request_type="get", payload=payload)

        if text:
            self.logger.info(u'退出成功！%s' % (text, ))


def main():
    youyouma = YouYouMa()
    youyouma.login()

    if os.path.exists(youyouma.items_file):
        items = get_items_from_file(youyouma.items_file)
        youyouma.logger.info(u'从文件中读取__%s__网站可接收验证码项目%d个。' % (
            str(youyouma.__class__).split('.')[1].strip("'>"), len(items)))
    else:
        items = youyouma.get_items()
        save_items_with_json(items, youyouma.items_file)
        youyouma.logger.info(u'一共获取__%s__网站可接收验证码项目%d个。' % (
            str(youyouma.__class__).split('.')[1].strip("'>"), len(items)))

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
            youyouma.logger.info(u'项目: __%s__, ID: __%s__, 价格: __%s__' % (item_name, item_id, item_price))

            if item_id and item_price <= 1:
                count = int(1.0 / item_price)

                nums = youyouma.get_phone(item_id, count)
                youyouma.logger.info(nums)
                if len(nums) == 0:
                    youyouma.logger.info(u'没有获取到有效号码')

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
                        'portal': u'悠悠码',             # 来源门户
                    }
                    new_item = add_item_fields(phone_item)
                    phone_items.append(new_item)
                if len(phone_items) > 0:
                    save_items(phone_items, youyouma.phone_file)
                    youyouma.release_phone()

                # 退出, 让token失效
                # youyouma.exit()
                # 重新登录, 刷新token
                # youyouma.login()
            else:
                youyouma.logger.info(u'项目价格超过10元, 放弃.')
            retry_time_per_item += 1

            # 依据重复率判断是否需要结束当前item_id的重复尝试
            three_increase[2] = three_increase[1]
            three_increase[1] = three_increase[0]
            three_increase[0] = increase_length
            print three_increase
    youyouma.logger.info(u'采集结束' + '-'*30)


if __name__ == '__main__':
    main()
