# -*- coding: utf-8 -*-
# @Date    : 2018-02-12 11:27:10
# @Author  : jym
# @Description:将原SQLITE数据库中的数据导入mongodb中
# @Version : v0.0
from MySqLite import MySqLite,get_docIds_All,get_docIds_inRange,get_params_all
from WenShuCourtDB_Mongo import WenshucoutMongoDb
import time
import db_tasks
import tcelery
from config import master_ip
tcelery.setup_nonblocking_producer()

def exChangeDocId():
    sqlite_con = MySqLite(u"F:\\裁判文书网\\MySqlite\\MySqlite.db")
    table_name = "docIds"
    num = 1800000
    for i in range(12):
        records = get_docIds_inRange(sqlite_con,i*num,(i+1)*num)
        #records = get_docIds_All(sqlite_con)
        print u'查询完毕'
        for record in records:
            key_names = ('rowid',
                        u'案件名称',
                        u'裁判日期',
                        u'裁判要旨段原文',
                        u'案号',
                        u'文书ID',
                        u'审判程序',
                        u'法院名称',
                        u'不公开理由',
                        u'案件类型')
            record_dic = {}
            for i in range(1,len(key_names)):
                key_name = key_names[i]
                key_val = record[i]
                record_dic[key_name] = key_val
                if record[0]<18000000:
                    record_dic['Exported'] = True
            db_tasks.insertDocid.delay(record_dic)
        time.sleep(20*60)
def exChangeParams():
    sqlite_con = MySqLite(u"F:\\裁判文书网\\MySqlite\\MySqlite.db")
    table_name = "docIds"
    records = get_params_all(sqlite_con)
    #records = get_docIds_All(sqlite_con)
    print u'查询完毕'
    for record in records:
        key_names = ('param','count','beDownloaded')
        record_dic = {}
        for i in range(len(key_names)):
            key_name = key_names[i]
            key_val = record[i]
            record_dic[key_name] = key_val
        if record_dic['beDownloaded'] == 1:
            record_dic['beDownloaded'] = True
        else:
            del record_dic['beDownloaded']
        db_tasks.insertParam.delay(record_dic)
exChangeDocId()
