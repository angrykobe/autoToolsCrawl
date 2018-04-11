#encoding:utf-8
from celery import Celery
from db.TycDB_Mongo import MongoDb_Tyc
from config import db_account,db_pwd
mydb = MongoDb_Tyc('TianYanCha',account=db_account,pwd=db_pwd)

app = Celery('db_tasks_save', broker='redis://127.0.0.1:6379/0',backend='redis://127.0.0.1:6379/1')


@app.task
def insert_comps(comps):
    mydb.insert_comps(comps)

@app.task
def insert_comp(comp):
    mydb.insert_comp(comp)

@app.task
def insert_compInfo(compInfo):
    mydb.insert_compInfo(compInfo)
