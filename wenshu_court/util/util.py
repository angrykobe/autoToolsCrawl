# -*- coding: utf-8 -*-
# @Date    : 2018-02-28 11:19:48
# @Author  : jym
# @Description:
# @Version : v0.0
import datetime
import functools
import itertools
import time
import tornado
from tornado import gen
from tornado import web


#显示当前时间
def showTime():
    dt = datetime.datetime.now()
    localtime = dt.strftime('%Y-%m-%d %H:%M:%S') #转化为date time  
    print localtime
def delayTime(interval):
    time.sleep(interval)

#阻塞式重试函数
def retry(exceptions=(Exception,), interval=0, max_retries=10, success=None, retry_func=None, **retry_func_kwargs):
    '''
    exceptions是异常定义
    success是一个用于判定结果是否正确的函数，通常可以定义为一个lambda函数。
    例如结果值ret必须为正数，则可以定义success=lambda x: x>0

    retry_func为函数运行失败后调用的重试函数
    
    '''
    if not exceptions and success is None:
        raise u"exceptions与success参数不能同时为空"
    def decorator(func):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            if max_retries < 0:
                iterator = itertools.count()
            else:
                iterator = range(max_retries)
            for num, _ in enumerate(iterator, 1):
                try:
                    if num!=1 and retry_func!=None:
                        getattr(args[0],retry_func)()
                    result = func(*args,**kwargs)
                    if success is None or success(result):
                        return result
                except exceptions,e:
                    print e
                    if num == max_retries:
                        raise
                time.sleep(interval)#此处是阻塞的
        return wrapper
    return decorator

#因为windows平台不能使用信号来做定时器，所以借用tornado的协程来实现定时器功能
def retry_unblock(exceptions=(Exception,), interval=0, max_retries=10, success=None, retry_func=None, **retry_func_kwargs):
    if not exceptions and success is None:
        raise u"exceptions与success参数不能同时为空"
    def decorator(func):
        @functools.wraps(func)
        @gen.coroutine
        def wrapper(*args, **kwargs):
            if max_retries < 0:
                iterator = itertools.count()
            else:
                iterator = range(max_retries)
            for num, _ in enumerate(iterator, 1):
                try:
                    if num!=1 and retry_func!=None:
                        yield retry_func(**retry_func_kwargs)
                    result = yield func(*args,**kwargs)
                    if success is None or success(result):
                        yield result
                        return
                except exceptions,e:
                    print e
                    if num == max_retries:
                        print u"已达到最大重试次数"
                        return
                yield gen.sleep(interval)#此处是非阻塞的
        return wrapper
    return decorator


def run_retry_unblock(func):
    def wrapper(*args,**kwargs):
        tornado.ioloop.IOLoop.current().run_sync(lambda:func(*args,**kwargs))
    return wrapper

#测试
def retry_func(a,b,c):
    print "a + b + c = ",sum([a,b,c])
@run_retry_unblock    
@retry_unblock(interval=3,max_retries=3,retry_func=retry_func,a=1,b=2,c=3)
def test(a,b):
    print a/b

if __name__ == '__main__':
    test(10,0)