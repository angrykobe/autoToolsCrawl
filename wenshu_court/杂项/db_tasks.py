#encoding:utf-8
from celery import Celery
from WenShuCourtDB_Mongo import WenshucoutMongoDb
from config import master_ip

mydb = WenshucoutMongoDb('WenShuCourt',host=master_ip)
app = Celery('db_tasks', broker='redis://127.0.0.1:6379/0',backend='redis://127.0.0.1:6379/1')

def getCourts():
    ret = mydb.getCourts()
    return ret

def getParams():
    ret = mydb.getParams()
    return ret

def getDocids():
    ret = mydb.getDocids()
    return ret

@app.task
def insertParams(params):
    mydb.insertParams(params)

@app.task
def insertParam(param):
    mydb.insertParam(param)

@app.task
def updateParamStatus(param):
    mydb.updateParamStatus(param)

@app.task
def updateCourtStatus(court_name):
    mydb.updateCourtStatus(court_name)

@app.task
def insertCourts(courts):
    mydb.insertCourts(courts)

@app.task
def insertCourt(court):
    mydb.insertCourt(court)

@app.task
def insertDocids(docids):
    mydb.insertDocids(docids)

@app.task
def insertDocid(docid):
    mydb.insertDocid(docid)

