#encoding:utf-8
import pymongo

class QiChachaMongoDb(object):
    """docstring for QiChachaMongoDb"""
    def __init__(self,db_name):
        super(QiChachaMongoDb, self).__init__()
        self.connection = pymongo.MongoClient('localhost', 28019)
        self.db = self.connection[db_name]
        self.compList = self.db.compList
        self.compList.ensure_index('KeyNo', unique=True)
        self.paramList = self.db.paramList
        self.paramList.ensure_index('ParamId', unique=True)
        self.usersList = self.db.users
        self.usersList.ensure_index('user', unique=True)
    def insert_comps(self,comp_infos):
        for comp_info in comp_infos:
            self.insert_comp(comp_info)
    def insert_comp(self,comp_info):
        try:
            self.compList.insert_one(comp_info)
        except pymongo.errors.DuplicateKeyError:
            pass
    def insert_param(self,param):
        try:
            self.paramList.insert_one(param)
        except pymongo.errors.DuplicateKeyError:
            pass
    def insert_params(self,params):
        for param in params:
            self.insert_param(param)  
    def update_status(self,paramId):
        self.paramList.update_one({'ParamId':paramId},{'$set':{'status':1}})
    
    def get_params(self,number=None):
        if number:
            return self.paramList.find({'status':0},{'_id':0}).limit(number)
        else:
            return self.paramList.find({'status':0},{'_id':0})

    def last_id(self):
        return self.paramList.count()
    def check_params_exists(self):
        last_id = self.last_id()
        if last_id==0:
            return False
        return True

    def get_userinfo_list(self):
        return self.usersList.find({},{'_id':0})