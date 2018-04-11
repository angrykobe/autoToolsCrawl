#encoding:utf-8
import pymongo

class MongoDb_Tyc(object):
    def __init__(self,db_name,account=None,pwd=None,host='localhost',port=28019,socketKeepAlive=True):
        super(MongoDb_Tyc, self).__init__()
        self.con = pymongo.MongoClient(host=host,port=port,socketKeepAlive=socketKeepAlive)
        self.db = self.con[db_name]
        if all([account,pwd]):
            self.db.authenticate(account, pwd)
        self.compList = self.db.compList
        self.compList.ensure_index('id_tyc', unique=True)
        self.compInfoList = self.db.compInfoList
        self.compInfoList.ensure_index('id_tyc', unique=True)
    
    def insert_comp(self,comp):
        try:
            self.compList.insert_one(comp)
        except pymongo.errors.DuplicateKeyError:
            pass
    def insert_comps(self,comps):
        for comp in comps:
            self.insert_comp(comp)
    def insert_compInfo(self,compInfo):
        try:
            self.compInfoList.insert_one(compInfo)
        except pymongo.errors.DuplicateKeyError:
            pass

    

