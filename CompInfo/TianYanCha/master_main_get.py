#encoding:utf-8
import tornado.ioloop
import tornado.web
import tornado.gen
from collections import deque
import json
import db_tasks_get

class MainHandler(tornado.web.RequestHandler):
    def get(self):
        if len(self.application.comp_queue)==0:
            comp_list = db_tasks_get.get_comps()
            self.application.comp_queue = deque(comp_list)
        data = self.application.comp_queue.pop()
        self.write(data)
    def post(self):
        id_qcc = self.get_body_argument('KeyNo')
        id_tyc = self.get_body_argument('id_tyc')
        db_tasks_get.update_status.delay(id_qcc,id_tyc)

class Application(tornado.web.Application):
     def __init__(self):
        handlers = [(r"/", MainHandler)]
        tornado.web.Application.__init__(self, handlers)
        comp_list = db_tasks_get.get_comps()
        self.comp_queue = deque(comp_list)
        print u"完成初始化操作"
if __name__ == "__main__":
    application = Application()
    application.listen(8003)
    tornado.ioloop.IOLoop.instance().start()
