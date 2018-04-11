#!/lib/anaconda2/bin/python
#-*- coding: utf-8 -*-
'''
Created on 2017-05-11 16:28:57

@author: Maxing
'''

import gevent
from gevent import monkey
monkey.patch_all()
import time

# from dingdingkama import Dingdingkama  # 无法获取指定号码
# from ema import Ema
# from feima import Feima
from goodyzm import Goodyzm
# from jima import Jima             # 会封号
from 弃用.laotou import Laotou
# from shenhua import Shenhua       # 会封号
from 被封禁.tianma import Tianma
from not_work.xingchenma import Xingchenma
from xunma import Xunma
# from yima import Yima             # 会封号
from yunma import Yunma
from utils import get_items_from_file


# 根据项目名称查询项目ID(这个有改进空间)
def match_item(item_name, items):
    for item in items:
        # 简单判断, 输入的项目名完全被保存的项目信息中的项目名包含视为匹配。
        if item_name in item['item_name']:
            return item['item_id']            

def check_phone(phone, item_name, check_object):
    a_t = time.time()
    items = get_items_from_file(check_object.items_file)
    print 'item cost: %.3f' % (time.time()-a_t)
    object_name = str(check_object.__class__).split('.')[1].strip("'>")
    check_object.logger.info(u'从文件中读取__%s__网站可接收验证码项目%d个。' % (
        object_name, len(items)))
    print object_name
    item_id = match_item(item_name, items)
    if not item_id:
        return 0

    check_object.login()
    
    # 检测打码平台是否存在指定的号码
    b_t = time.time()
    if object_name == 'Xingchenma':
        phones = check_object.get_specific_phone(item_id, phone)
    else:
        phones = check_object.get_phone(item_id, 1, phone)
    # print phones
    print 'check cost: %.3f' %(time.time()-b_t)

    # 释放号码
    if object_name in ['Feima', 'Laotou', 'Xunma', 'Yunma']:
        check_object.exit()
    else:
        check_object.release_all_phone()

    # 返回是否命中
    return len(phones)


def main():
    # ema = Ema()
    # feima = Feima()
    goodyzm = Goodyzm()
    laotou = Laotou()
    tianma = Tianma()
    xingchenkama = Xingchenma()
    xunma = Xunma()
    yunma = Yunma()
    object_list = [goodyzm, laotou, tianma, xingchenkama, xunma, yunma]

    # 测试号码
    # phones = ['13104936324', '17198245979', '17075307315', '13020930234',
    #   '13631771593', '15368749243', '17183021676', '18316285871',]
    
    start_time = time.time()
    tasks = [gevent.spawn(check_phone, '13631771593', u'红岭创投', _object) for _object in object_list]
    gevent.joinall(tasks)

    data = {}
    for i,task in enumerate(tasks):
        print i, task.value
        data.update({object_list[i].__class__.__name__: task.value})

    print data
    print 'cost: %.3f' % (time.time()-start_time)


if __name__ == '__main__':
    main()
