#encoding:utf-8
import tornado.ioloop
import tornado.web
import tornado.gen
from collections import deque
import json
import db_tasks_save
import tcelery
tcelery.setup_nonblocking_producer()


class MainHandler(tornado.web.RequestHandler):
    def post(self):
        compInfo = eval(self.get_body_argument('compInfo'))
        compInfo = json.loads(json.dumps(compInfo))
        db_tasks_save.insert_compInfo(compInfo)


class Application(tornado.web.Application):
     def __init__(self):
        handlers = [(r"/", MainHandler)]
        tornado.web.Application.__init__(self, handlers)
        print u"完成初始化操作"
if __name__ == "__main__":
    application = Application()
    application.listen(8001)
    tornado.ioloop.IOLoop.instance().start()
