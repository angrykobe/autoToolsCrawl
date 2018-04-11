#encoding:utf-8
from celery import Celery
from db.QccDB_Mongo import MongoDb_Qcc
mydb = MongoDb_Qcc('QiChaCha')

app = Celery('db_tasks_get', broker='redis://127.0.0.1:6379/2',backend='redis://127.0.0.1:6379/3')

def get_comps(number=5000):
    comps = mydb.get_comps(number)   
    return comps

@app.task
def update_status(objId,id_tyc):
    mydb.update_status(objId,id_tyc)

