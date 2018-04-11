#encoding:utf-8
from celery import Celery
from util.util import distance
from db.QiChaChaDB_Mongo import QiChachaMongoDb

mydb = QiChachaMongoDb('QiChaCha')

app = Celery('db_tasks', broker='redis://127.0.0.1:6379/0',backend='redis://127.0.0.1:6379/1')

def init_params():
    if mydb.check_params_exists()==False:
        _init_params()

def _init_params():
    lower_left_lat = 16.032685
    lower_left_lng = 69.376754
    upper_right_lat = 55.711056
    upper_right_lng = 135.018309
    lat_num = 100
    lng_num = 100

    per_lat = (upper_right_lat - lower_left_lat)/lat_num
    per_lng = (upper_right_lng - lower_left_lng)/lng_num
    params_list =[]
    last_id = 0
    for lat_no in range(lat_num):
        for lng_no in range(lng_num):
            param ={
                'searchType':'multiple',
                'longitude':'',
                'latitude':'',
                'searchKey':'',   
                'pageSize':100,
                'pageIndex':1,
                'distance':0,
                'startDateBegin':'',
                'startDateEnd':'',
                'registCapiBegin':'',
                'registCapiEnd':'',
                'industryCode':'',
                'subIndustryCode':'0',
                'statusCode':'',
                'isSortAsc':'',
                'sortField':''}
            last_id = last_id + 1
            lower_left_lat_new = lower_left_lat + lat_no*per_lat
            lower_left_lng_new = lower_left_lng + lng_no*per_lng
            upper_right_lat_new = lower_left_lat + (lat_no+1)*per_lat
            upper_right_lng_new = lower_left_lng + (lng_no+1)*per_lng
            loc_data = [lower_left_lat_new,lower_left_lng_new,upper_right_lat_new,upper_right_lng_new]
            param['distance'] = distance(lower_left_lat_new,lower_left_lng_new,upper_right_lat_new,upper_right_lng_new)/2
            param['latitude'] = (lower_left_lat_new + upper_right_lat_new)/2
            param['longitude'] = (lower_left_lng_new + upper_right_lng_new)/2
            paramInfo = {'ParamId':last_id,'loc_data':loc_data,'status':0,'param':param}
            mydb.insert_param(paramInfo)

def get_param_list(number=5000):
    param_list = mydb.get_params(number)   
    return param_list
def last_id():
    return mydb.last_id()

@app.task
def update_status(paramid):
    mydb.update_status(paramid)

@app.task
def save_compInfos(compInfos):
    mydb.insert_comps(compInfos)

@app.task
def insert_param(params):
    mydb.insert_param(params)

@app.task
def get_userinfo_list():
    return mydb.get_userinfo_list()