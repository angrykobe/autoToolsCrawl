#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Date    : 2017-11-22 11:36:28
# @作者  : "jym"
# @说明    : 
# @Version : $Id$
import tornado.ioloop
import tornado.web
import tornado.autoreload
import Queue
from config import master_ip
from db.WenShuCourtDB_Mongo import WenshucoutMongoDb
import db_tasks
import tcelery
import json
tcelery.setup_nonblocking_producer()

court_list = db_tasks.getCourts_queue()
params_list = db_tasks.getParams_queue()
#docids_list = db_tasks.getDocids_queue()
docids_list = Queue.Queue()
print u'初始化已完成'

class CourtInfoHandler(tornado.web.RequestHandler):
    def post(self):
        post_type = self.get_body_argument('type')
        post_data = self.get_body_argument('data')
        if post_type == 'post_data':
            court = json.loads(post_data)
            db_tasks.insertCourt.delay(court)


#用法院信息获取参数
class ParamInfoHandler(tornado.web.RequestHandler):
    def get(self):
        if court_list.qsize() == 0:
            self.write('No Data')
        else:
            data = court_list.get()
            self.write(data)
    def post(self):
        post_type = self.get_body_argument('type')
        post_data = self.get_body_argument('data')
        if post_type == 'post_data':
            param = json.loads(post_data)
            db_tasks.insertParam.delay(param)
        else:
            court_name = json.loads(post_data)['court_name']
            db_tasks.updateCourtStatus.delay(court_name)

#用参数信息获取docid
class DocIdInfoHandler(tornado.web.RequestHandler):
    def get(self):
        if params_list.qsize() == 0 :
            self.write('No Data')
        else:
            data = params_list.get()
            self.write(data)
    def post(self):
        post_type = self.get_body_argument('type')
        post_data = self.get_body_argument('data')
        if post_type == 'post_data':
            docids  = list(eval(post_data))
            db_tasks.insertDocids.delay(docids)
        else:
            param = post_data
            db_tasks.updateParamStatus.delay(param)
        
#用docid获取正文内容
class ContentInfoHandler(tornado.web.RequestHandler):
    def get(self):
        if docids_list.qsize() == 0:
            self.write('No Data')
        else:
            data = docids_list.get()
            self.write(data)
    def post(self):
        post_type = self.get_body_argument('type')
        post_data = self.get_body_argument('data')
        if post_type == 'post_data':
            content = json.loads(post_data)
            db_tasks.insertContent.delay(content)
        else:
            docid = json.loads(post_data)
            db_tasks.updateDocidStatus.delay(docid)



application = tornado.web.Application([
    (r"/courtinfo", CourtInfoHandler),
    (r"/paraminfo", ParamInfoHandler),
    (r"/docIdinfo", DocIdInfoHandler),
    (r"/contentinfo",ContentInfoHandler),
])

if __name__ == "__main__":
    application.listen(8000)
    tornado.ioloop.IOLoop.instance().start()
    