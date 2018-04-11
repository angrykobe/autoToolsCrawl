#encoding:utf-8
import tornado.ioloop
import tornado.web
import tornado.gen
from collections import deque
import json
import db_tasks
import tcelery
tcelery.setup_nonblocking_producer()

class MouseStatusHandler(tornado.web.RequestHandler):
    def get(self):
        self.write({'status':self.application.mouseStatus})
        if self.application.mouseStatus == True:
            self.application.mouseStatus = False
    def post(self):
        if self.application.mouseStatus == False:
            self.application.mouseStatus = True
        
class UserInfoHandler(tornado.web.RequestHandler):
    def get(self):
        try:
            data = self.application.userinfo_queue.pop()
        except Exception,e:
            data = ''
        self.write(data)
    def post(self):
        data = self.request.body
        userInfo = json.loads(data)
        print userInfo
        self.application.userinfo_queue.append(userInfo)
class MainHandler(tornado.web.RequestHandler):
    def get(self):
        if len(self.application.param_queue)==0:
            param_list = db_tasks.get_param_list()
            self.application.param_queue = deque(param_list)
        data = self.application.param_queue.pop()
        self.write(data)
    def post(self):
        post_type = self.get_body_argument('type')
        if post_type == 'post_param':
            paramInfo = json.loads(self.get_body_argument('paramInfo'))
            self.application.last_id += 1
            paramInfo['ParamId'] = self.application.last_id
            paramInfo['status'] = 0
            db_tasks.insert_param.delay(paramInfo)
            
        else:
            paramid = self.get_body_argument('ParamId')
            db_tasks.update_status.delay(int(paramid))                     
            if post_type == 'post_compinfos':
                compInfos = list(eval(self.get_body_argument('compInfos')))
                compInfos =[json.loads(json.dumps(compInfo)) for compInfo in compInfos]
                db_tasks.save_compInfos.delay(compInfos)


class Application(tornado.web.Application):
     def __init__(self):
        handlers = [(r"/", MainHandler),
                    (r"/userInfo", UserInfoHandler),
                    (r"/mouseStatus",MouseStatusHandler)]
        tornado.web.Application.__init__(self, handlers)
        db_tasks.init_params()
        param_list = db_tasks.get_param_list()
        userinfo_list = db_tasks.get_userinfo_list()
        self.param_queue = deque(param_list)
        self.userinfo_queue = deque(userinfo_list)
        self.last_id = db_tasks.last_id()
        self.mouseStatus = True #True:可用状态，False:不可用状态
        print u"完成初始化操作"
if __name__ == "__main__":
    application = Application()
    application.listen(8001)
    tornado.ioloop.IOLoop.instance().start()
