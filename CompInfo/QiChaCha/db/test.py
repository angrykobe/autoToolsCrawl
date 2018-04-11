# -*- coding: utf-8 -*-
# @Date    : 2018-03-16 14:43:14
# @Author  : jym
# @Description:
# @Version : v0.0
import pymongo
import db_tasks


file_name = 'adjudicative_documents_code.txt'
file_obj = open(file_name,'r')
icount = 0
for line in file_obj.readlines():
    docid = line.replace('\n','')
    db_tasks.update_docid.delay(docid)
    icount += 1
    print icount
