#!/lib/anaconda2/bin/python
#-*- coding: utf-8 -*-
'''
Created on 2017-05-09 16:04:50
Updated on 2017-05-11 11:33:04

@author: Maxing
'''



import sys
import os
import json
import codecs
import logging
import requests
from lxml import etree
reload(sys)
sys.setdefaultencoding('utf8')


# 保存项目信息
def save_items(items, save_file):
    with codecs.open(save_file, 'a', encoding='utf8') as sf:
        for item in items:
            values = []
            for key in sorted(item):
                if item[key] is None:
                    item_value = ''
                if type(item[key]) is float:
                    item_value = str(item[key])
                else:
                    item_value = str(item[key]).replace('^', '').replace('\n', '')
                values.append(item_value)
            new_line = '^'.join(values) + '\n'
            sf.write(new_line)


# 保存Json格式的项目信息
def save_items_with_json(items, save_file):
    with codecs.open(save_file, 'a', encoding='utf8') as sf:
        for item in items:
            sf.write(json.dumps(item, ensure_ascii=False) + "\n")


# 获取项目列表
def get_items_from_file(save_file):
    if os.path.exists(save_file):
        print 'open item list...'
        lines = list(open(save_file))
        items = []
        for line in lines:
            item = json.loads(line)
            items.append(item)
        return items

# 查询归属地和运营商信息
def query_api(phone):
    city = ''
    corp = ''
    if len(phone) != 11:
        return phone, city, corp
    url = 'http://www.ip138.com:8080/search.asp'
    payload = {
        'mobile': phone,
        'action': 'mobile',
    }
    headers = {
        'Host': 'www.ip138.com:8080',
        'Connection': 'keep-alive',
        'Upgrade-Insecure-Requests': '1',
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/57.0.2987.133 Safari/537.36',
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
        # 'Referer': 'http://www.ip138.com:8080/search.asp?mobile=13430662390&action=mobile',
        'Accept-Encoding': 'gzip, deflate, sdch',
        'Accept-Language': 'zh-CN,zh;q=0.8,en-US;q=0.6,en;q=0.4',
    }

    try:
        r = requests.get(url=url, headers=headers, params=payload, allow_redirects=False)
        if r.status_code == 200:
            r.encoding = 'gb2312'
            text = r.text
            root = etree.HTML(text)
            td_elements = root.xpath('//table[2][@class="tdc2"]/text()')
            if td_elements:
                city = td_elements[1].replace(u'\xa0', '').strip()
                corp = td_elements[2].strip()

            if city=='' and corp=='':
                city_str = root.xpath('//table[2]/tr[3]/td[2]/text()')
                if city_str:
                    city = city_str[0].replace(u'\xa0', '').strip()

                corp_str = root.xpath('//table[2]/tr[4]/td[2]/text()')
                if corp_str:
                    corp = corp_str[0].strip()

        # print city, corp
        return phone, city, corp
    except:
        return phone, city, corp

# 加载本地的归属地和运营商字典
def get_city_and_corp_dict(source):
    lines = list(codecs.open(source, 'r', encoding='utf-8'))
    city_and_corp_dict = {}
    for line in lines:
        phone = line.split('^')[0]
        city = line.split('^')[1]
        corp = line.split('^')[2].strip('\n')
        city_and_corp_dict[phone] = (city, corp)
    return city_and_corp_dict 

# 2017-05-09 在之前的字段基础上增加三个字段: 归属地、运营商、来源平台
def add_item_fields(item):
    phone = item['phone']
    phone, city, corp = query_api(phone)
    # print city, corp
    item.update({'city': city, 'corp': corp})
    return item

# log初始化
def log_init(log_name, log_file_path):
    # 创建一个logger
    logger = logging.getLogger(log_name)
    logger.setLevel(logging.DEBUG)

    # 创建一个handler,用于写入日志文件
    fh = logging.FileHandler(log_file_path)
    fh.setLevel(logging.DEBUG)

    # 再创建一个handler，用于输出到控制台
    # ch = logging.StreamHandler()
    # ch.setLevel(logging.DEBUG)

    # 定义handler的输出格式
    formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    fh.setFormatter(formatter)
    # ch.setFormatter(formatter)

    # 给logger添加handler
    logger.addHandler(fh)
    # logger.addHandler(ch)