#encoding:utf-8
import pymongo

class MongoDb_Qcc(object):
    def __init__(self,db_name,account=None,pwd=None,host='localhost',port=28019,socketKeepAlive=True):
        super(MongoDb_Qcc, self).__init__()
        self.con = pymongo.MongoClient(host=host,port=port,socketKeepAlive=socketKeepAlive)
        self.db = self.con[db_name]
        if all([account,pwd]):
            self.db.authenticate(account, pwd)
        self.compList = self.db.compList
    def get_comps(self,number=None):
        if number:
            return self.compList.find({'$or':[{'getTycInfo':0},{'getTycInfo':{'$exists':False}}]},{'KeyNo':1,'Name':1,'_id':0}).limit(number)
        else:
            return self.compList.find({'$or':[{'getTycInfo':0},{'getTycInfo':{'$exists':False}}]},{'KeyNo':1,'Name':1,'_id':0})
    def update_status(self,id_qcc,id_tyc):
        self.compList.update_one({'KeyNo':id_qcc},{'$set':{'getTycInfo':1,'id_tyc':id_tyc}})