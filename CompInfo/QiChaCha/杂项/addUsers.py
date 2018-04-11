# -*- coding: utf-8 -*-
# @Date    : 2018-03-19 10:27:48
# @Author  : jym
# @Description:
# @Version : v0.0
import pymongo
con = pymongo.MongoClient('localhost',28019)
db = con['QiChaCha']
coll = db['users']
coll.ensure_index('user', unique=True)
users = [{'user':'18680325804','pwd':'123456789qwe'},
         {'user':'18814118010','pwd':'hbbhbb'},
         {'user':'13823562294','pwd':'871124'},
         {'user':'13250222195','pwd':'lxj123'},
         {'user':'13250201823','pwd':'lxj123'},
         {'user':'13148942850','pwd':'lxj123'},
         {'user':'13242740941','pwd':'lxj123'},
         {'user':'13250502578','pwd':'lxj123'},
         {'user':'13250285066','pwd':'lxj123'},
         {'user':'13148935862','pwd':'lxj123'}]
coll.insert_many(users)