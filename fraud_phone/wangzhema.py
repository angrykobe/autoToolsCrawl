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

# 王者码(http://www.wangzhema.com/)
# 账号/密码: hbbhbb(rfM#!EzZU%!3s7*kxbTy)
# 平台接口前缀: 'http://47.52.119.171:9180/service.asmx'
'''
账户基本信息
account_info = {
    'user_info': {
        u'登陆名称': 'hbbhbb',
        u'帐户Id': '3194',
        u'联系人': u'刘岩',
        u'QQ号码': '24481586',
        u'VIP': '0',
        u'折扣': '无',        
        u'余额': '5.60',
    }

}
'''


class WangZheMa(object):
    def __init__(self):
        # 该参数用来存放该平台获取 项目列表 的地址
        self.api_prefix = r'http://47.52.119.171:9180/service.asmx'
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
            "Host": "47.52.119.171:9180",
            "Upgrade-Insecure-Requests": "1",
            "User-Agent": "Mozilla/5.0 (Windows NT 6.1; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/63.0.3239.108 Safari/537.36"
        }

        # 保存网站项目信息的文件

        website_name = "wangzhema"

        items_file_name = '{website_name}_items.json'.format(website_name=website_name)
        self.items_file = os.path.join(sys.path[0], 'items', items_file_name)

        # 保存最终获得的手机号码信息保存文件
        current_date = time.strftime('%Y-%m-%d', time.localtime(time.time()))
        # phone_file_name = "{website_name}_phone_{date}.txt".format(website_name=website_name, date=current_date)
        phone_file_name = "ema_phone_{website_name}_phone_{date}.txt".format(website_name=website_name, date=current_date)
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
                            response = requests.get(url=url, headers=self.headers, params=payload,
                                                    allow_redirects=False)

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
        error_mapping = {
            "": u"调用接口超时异常",
            "0": u"帐户处于禁止使用状态",
            "-1": u"调用接口失败",
            "-2": u"帐户信息错误",
            "-3": u"用户或密码错误",
            "-4": u"不是普通帐户",
            "-30": u"非绑定IP"
        }

        url = self.api_prefix + '/UserLoginStr '
        payload = {
            "name": self.user_name,
            "psw": self.user_pwd
        }

        text = self.request(url=url, request_type="get", payload=payload)

        if text:
            if text in error_mapping.keys():
                self.logger.error(u'登录失败！错误信息为 : {error_msg}'.format(error_msg=error_mapping[text]))
            else:
                self.token = text
                self.logger.info(u'登录成功！')
        else:
            self.logger.info(u'登录失败！')

    def get_phone_by_task_id(self, task_id):
        error_mapping = {
            "": u"调用接口超时异常。",
            "0": u"没登陆或失败。",
            "-1": u"任务已结束或被已被中止或当前没有合条件号码。",
            "-11": u"端口繁忙被占用，请稍后再试。",
        }

        url = self.api_prefix + '/GetTaskStr'
        payload = {
            'token': self.token,
            'id': task_id
        }

        text = self.request(url=url, request_type="get", payload=payload)

        if text:
            if text in error_mapping.keys():
                self.logger.error(u'获取号码失败！错误信息为 : {error_msg}'.format(error_msg=error_mapping[text]))
                return None
            else:
                return text

    # 获取项目
    def get_items(self):
        # 返回格式
        # 项目ID|,|项目名称|,|项目价格|,|项目类型|;|项目ID|,|项目名称|,|项目价格|,|项目类型|;|...
        # 项目类型:
        #   接收,多次接收.  表示此项目用于接收验证码
        #   语音接收.      表示此项目用于接收语音验证码
        #   发送.          表示此项目用户发送短信
        #   收发,多次收发.  表示此项目即可接收验证码，也可以发送短信

        item_type_mapper = {
            u"接收": "1",
            u"语音接收": "1",
            u"发送": "2",
            u"收发": "3",
            u"多次收发": "3",
            u"多次接收": "4",
        }

        url = self.api_prefix + '/GetXMmcStr'
        payload = {
            'token': self.token,
            'mc': u"[a-z0-9贷金融理财网富服所投宝钱易线创汇信贷众资银]"
        }

        items = []

        text = self.request(url=url, request_type="get", payload=payload)

        if text:
            if '0' == text:
                self.login()
            else:
                items_str = text.split("|;|")
                self.logger.info(items_str[:100])

                for item_str in items_str:
                    item_dict = dict(zip(
                        ['item_id', 'item_name', 'item_price', 'item_type'], item_str.split("|,|")))

                    item_type = item_dict.get('item_type')

                    item_dict['item_type'] = item_type_mapper.get(item_type, "1")

                    if item_type:
                        items.append(item_dict)

                return items

    # 获取号码
    def get_phone(self, item_id, count=20):
        # item_id: 项目ID
        # count: 获取手机号的数量

        error_mapping = {
            "": u"调用接口超时异常。",
            "0": u"没登陆或失败。",
            "-1": u"当前没有合条件号码。",
            "-2": u"提交取号任务超量，请稍后再试。",
            "-3": u"获取号码数量超量，请释放已经做完任务不使用的号码，以便获取新号码。",
            "-4": u"该项目已经被禁用，暂停取号做业务。",
            "-8": u"帐户余额不足。",
            "-11": u"端口繁忙被占用，请稍后再试。",
            "-15": u"查找不到该专属对应KEY。",

        }

        url = self.api_prefix + '/GetHMStr'
        payload = {
            'token': self.token,  # 登陆token
            'sl': str(count),  # 获取号码数量
            "xmid": item_id,  # 项目编码
            "lx": 0,  # 要获取号码类型，0是不限运营商，1是移动号码，2是联通号码，3是电信号码
            "a1": "",  # 省份
            "a2": "",  # 城市
            "pk": ""  # 专属卡商对应编号
        }

        text = self.request(url=url, request_type="get", payload=payload)

        if "id" in text:
            task_id = text.replace("id=", "")

            retry_time = 0

            while 1:
                text = self.get_phone_by_task_id(task_id=task_id)

                if text == "1" or text == 1:
                    retry_time += 1

                    if retry_time >= 10:
                        break

                    time.sleep(1)
                    continue
                else:
                    break

        phones = []

        if text:
            if text in error_mapping.keys():
                self.logger.error(u'获取号码失败！错误信息为 : {error_msg}'.format(error_msg=error_mapping[text]))
            else:
                phones_str = text.replace("hm=", "")

                phones = phones_str.split(",")

        return phones

    # 获取指定号码
    def get_specific_phone(self, item_id, phone):
        # item_id: 项目ID
        # phone: 指定号码

        payload = {
            'token': self.token,  # 登陆token
            'xmid': item_id,  # 项目编码
            'hm': phone,  # 指定号码
            'op': 1,  # 码库检测方式  0-检测云码库该号码是否已经做过该项目任务
            # 1-不检测码库是否已经做过该项目
        }
        url = self.api_prefix + '/mkHMStr'
        response_int = self.request(url=url, request_type="get", payload=payload)
        # 为了和其他平台统一, 命中返回一个长度为1的list, 否则返回一个空的list
        print response_int
        if response_int in ['1', '-2', '-3', '-5', '-10', '-13', '-16', '-20', '-30']:
            return ['1']
        else:
            return []

    # 释放全部号码
    def release_all_phone(self):
        url = self.api_prefix + '/sfAllStr'
        payload = {'token': self.token}

        text = self.request(url=url, request_type="get", payload=payload)

        if text == u'1':
            self.logger.info(u'释放号码成功!')
        else:
            self.logger.info(u'释放号码失败,重新登录刷新token。')

    # 加黑
    def add_black_list(self, item_id, phone):
        try:
            url = self.api_prefix + '/HmdStr'

            payload = {
                'token': self.token,  # 登陆token
                'xmid': item_id,  # 项目编码
                'hm': phone,  # 指定号码
            }

            text = self.request(url=url, request_type="get", payload=payload)

            if text in [u'1', u'-2']:
                self.logger.info(u'添加黑名单成功! {phone}'.format(phone=phone))
            else:
                raise Exception
        except Exception:
            self.logger.info(u'添加黑名单失败! {phone}'.format(phone=phone))

    # 退出
    def exit(self):
        url = self.api_prefix + '/UserExitStr'
        payload = {'token': self.token}

        text = self.request(url=url, request_type="get", payload=payload)

        if text == "1":
            self.logger.info(u'退出成功!')


def main():
    wangzhema = WangZheMa()
    wangzhema.login()
    wangzhema.release_all_phone()

    if os.path.exists(wangzhema.items_file):
        items = get_items_from_file(wangzhema.items_file)
        wangzhema.logger.info(u'从文件中读取__%s__网站可接收验证码项目%d个。' % (
            str(wangzhema.__class__).split('.')[1].strip("'>"), len(items)))
    else:
        items = wangzhema.get_items()
        save_items_with_json(items, wangzhema.items_file)
        wangzhema.logger.info(u'一共获取__%s__网站可接收验证码项目%d个。' % (
            str(wangzhema.__class__).split('.')[1].strip("'>"), len(items)))

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
            wangzhema.logger.info(u'项目: __%s__, ID: __%s__, 价格: __%s__' % (item_name, item_id, item_price))

            if item_price <= 10:
                if item_price > 1:
                    count = int(10 / item_price)
                else:
                    count = 10

                nums = wangzhema.get_phone(item_id, count)

                wangzhema.logger.info(nums)
                if len(nums) == 0:
                    wangzhema.logger.info(u'没有获取到有效号码！')

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
                        'portal': u'王者码',         # 来源门户
                    }

                    new_item = add_item_fields(phone_item)
                    wangzhema.add_black_list(item_id, num)

                    phone_items.append(new_item)
                if len(phone_items) > 0:
                    save_items(phone_items, wangzhema.phone_file)

                # 释放号码
                wangzhema.release_all_phone()

                # 重新登录, 刷新token
                wangzhema.exit()
                wangzhema.login()
            else:
                wangzhema.logger.info(u'项目价格超过10元, 放弃！')
            retry_time_per_item += 1

            # 依据重复率判断是否需要结束当前item_id的重复尝试
            three_increase[2] = three_increase[1]
            three_increase[1] = three_increase[0]
            three_increase[0] = increase_length
            print three_increase

    # 退出登录
    wangzhema.exit()

    wangzhema.logger.info(u'采集结束' + '-' * 30)


if __name__ == '__main__':
    main()
