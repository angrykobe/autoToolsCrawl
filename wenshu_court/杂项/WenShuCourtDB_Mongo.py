#encoding:utf-8
import pymongo
import Queue
class WenshucoutMongoDb(object):
    def __init__(self,db_name,host ='localhost',port=27017):
        super(WenshucoutMongoDb, self).__init__()
        #self.connection = pymongo.MongoClient(host,port,socketKeepAlive=True)
        self.connection = pymongo.MongoClient(host,port)
        self.db = self.connection[db_name]
        self.courtsCol = self.db.courts
        self.courtsCol.ensure_index('court_name', unique=True)
        self.paramsCol = self.db.params
        self.paramsCol.ensure_index('param', unique=True)
        self.docidsCol = self.db.docids
        self.docidsCol.ensure_index(u'文书ID', unique=True)
        self.contentsCol = self.db.contents
        self.contentsCol.ensure_index(u'文书ID', unique=True)
    def _insert_one(self,coll,data):
        try:
            coll.insert(data)
        except pymongo.errors.DuplicateKeyError:
            pass
        except pymongo.errors.BulkWriteError as exc:
            print exc.details
            pass
    def _insert_many(self,coll,datas):
        '''
        try:
            coll.insert_many(datas)
        except pymongo.errors.DuplicateKeyError:
            pass
        except pymongo.errors.BulkWriteError as exc:
            print exc.details
            pass
        '''
        for data in datas:
            self._insert_one(coll,data)

    #保存法院信息
    def insertCourts(self,courts):
        self._insert_many(self.courtsCol,courts)

    def insertCourt(self,court):
        self._insert_one(self.courtsCol,court)

    #获取没有配置查询参数的法院列表
    def getCourts(self):
        courts = self.courtsCol.find({'be_getParams':{'$exists':False}},{'court_name':1,'court_level':1,'_id':0})
        return courts

    #更新法院状态:是否已经配置该法院查询参数
    def updateCourtStatus(self,name):
        self.courtsCol.update({'court_name':name},{'$set':{'be_getParams':True}})

    #保存参数信息
    def insertParams(self,params):
        self._insert_many(self.paramsCol,params)

    def insertParam(self,param):
        self._insert_one(self.paramsCol,param)

    #获取没有查询完的参数列表
    def getParams(self):
        ret = self.paramsCol.find({'beDownloaded':{'$exists':False}},{'param':1,'count':1,'_id':0})
        return ret

    #更新参数信息：已经完成了该参数下docId的获取
    def updateParamStatus(self,param):
        self.paramsCol.update({'param':param},{'$set':{'beDownloaded':True}})

    #保存docId信息
    def insertDocids(self,docids):
        self._insert_many(self.docidsCol,docids)

    def insertDocid(self,docId):
        self._insert_one(self.docidsCol,docId)

    #更新docId状态：该docId的详细内容是否已经下载
    def updateDocidStatus(self,docid):
        self.docidsCol.update({u'文书ID':docid},{'$set':{'beDownloaded':True}})
        
    #获取没有获取详细内容的docId列表
    def getDocids(self):
        ret = self.docidsCol.find({'$and':[{'$or':[{'beDownloaded':False},{'beDownloaded':{'$exists':False}}]},{'count':{'$lte':2000}}]},{u'文书ID':1,'_id':0})
        return ret

    #保存详细内容
    def insertContent(self,content):
        self._insert_one(self.contentsCol,content)


    def _cursor2queue(self,cursor):
        queue = Queue.Queue()
        for item in cursor:
            queue.put(item)
        return queue
    def getCourts_queue(self):
        queue = self._cursor2queue(self.getCourts())
        return queue

    def getParams_queue(self):
        queue = self._cursor2queue(self.getParams())
        return queue
    def getDocids_queue(self):
        queue = self._cursor2queue(self.getDocids())
        return queue

    def getParamsZero(self):
        ret = self.paramsCol.find({'count':0},{'param':1})
        return ret

from config import master_ip

mydb = WenshucoutMongoDb('WenShuCourt',host=master_ip)
ret = mydb.getParams()
count = sum([item['count'] for item in ret])
print count