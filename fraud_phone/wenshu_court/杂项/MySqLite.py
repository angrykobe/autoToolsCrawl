#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Date    : 2017-11-14 10:50:32
# @作者  : "jym"
# @说明    : ""
# @Version : $Id$
import tablib
import ConfigParser
import time
import sqlite3
import os
class MySqLite(object):
    """
    SQLite数据库是一款非常小巧的嵌入式开源数据库软件，也就是说没有独立的维护进程，所有的维护都来自于程序本身。
    在python中，使用sqlite3创建数据库的连接，当我们指定的数据库文件不存在的时候连接对象会自动创建数据库文件；
    如果数据库文件已经存在，则连接对象不会再创建数据库文件，而是直接打开该数据库文件。

    对于数据库链接对象来说，具有以下操作：
        commit()            --事务提交
        rollback()          --事务回滚
        close()             --关闭一个数据库链接
        cursor()            --创建一个游标

    cu = conn.cursor()
    这样我们就创建了一个游标对象：cu
    在sqlite3中，所有sql语句的执行都要在游标对象的参与下完成
    对于游标对象cu，具有以下具体操作：
        execute()           --执行一条sql语句
        executemany()       --执行多条sql语句
        close()             --游标关闭
        fetchone()          --从结果中取出一条记录
        fetchmany()         --从结果中取出多条记录
        fetchall()          --从结果中取出所有记录
        scroll()            --游标滚动
        update()            --更新数据
        delete()             --删除数据

    """
    # 是否打印sql
    SHOW_SQL = True

    def __init__(self, path):
        self.path = path

    def get_conn(self):
        """
        获取数据库连接
        """
        try:
            conn = sqlite3.connect(self.path)

            """
            该参数是为了解决一下错误：
            ProgrammingError: You must not use 8-bit bytestrings unless you use a text_factory that can interpret 8-bit bytestrings (like text_factory = str).
            It is highly recommended that you instead just switch your application to Unicode strings.
            """
            # conn.text_factory = lambda x: unicode(x, 'utf-8', 'ignore')
            conn.text_factory = str
            if os.path.exists(self.path) and os.path.isfile(self.path):
                return conn
        except sqlite3.OperationalError, e:
            print "Error:%s" % e

    def get_cursor(self, conn):
        """
        该方法是获取数据库的游标对象，参数为数据库的连接对象
        """
        if conn is not None:
            return conn.cursor()
        else:
            return self.get_conn().cursor()


    def close_all(self, conn, cu):
        """
        关闭数据库游标对象和数据库连接对象
        """
        try:
            cu.close()
            conn.close()
        except sqlite3.OperationalError, e:
            print "Error:%s" % e


    def create_table(self, sql):
        """
        创建数据库表
        """
        if sql is not None and sql != '':
            conn = self.get_conn()
            cu = self.get_cursor(conn)
            cu.execute(sql)
            conn.commit()
            self.close_all(conn, cu)
        else:
            print('the [{}] is empty or equal None!'.format(sql))

    def drop_table(self, table):
        """
        如果表存在,则删除表
        """
        if table is not None and table != '':
            sql = 'DROP TABLE IF EXISTS ' + table
            if self.SHOW_SQL:
                print('执行sql:[{}]'.format(sql))
            conn = self.get_conn()
            cu = self.get_cursor(conn)
            cu.execute(sql)
            conn.commit()
            print('删除数据库表[{}]成功!'.format(table))
            cu.close()
            conn.close()
            # self.close_all(conn, cu)
        else:
            print('the [{}] is empty or equal None!'.format(sql))

    def insert(self, sql, data):
        """
        插入数据
        """
        if sql is not None and sql != '':
            if data is not None:
                conn = self.get_conn()
                cu = self.get_cursor(conn)
                for d in data:
                    try:
                        cu.execute(sql, d)
                    except sqlite3.IntegrityError:
                        continue
                    except Exception,e:
                        raise e

                    conn.commit()

                self.close_all(conn, cu)
        else:
            print('the [{}] is empty or equal None!'.format(sql))

    def fetchall(self, sql):
        """
        查询所有数据
        """
        if sql is not None and sql != '':
            conn = self.get_conn()
            cu = self.get_cursor(conn)
            if self.SHOW_SQL:
                print('执行sql:[{}]'.format(sql))
            cu.execute(sql)
            r = cu.fetchall()
            return r
            self.close_all(conn, cu)
        else:
            print('the [{}] is empty or equal None!'.format(sql))

    def fetchone(self, sql, data):
        """
        查询一条数据
        """
        if sql is not None and sql != '':
            if data is not None:
                #Do this instead
                d = (data,)
                conn = self.get_conn()
                cu = self.get_cursor(conn)
                if self.SHOW_SQL:
                    print('执行sql:[{}],参数:[{}]'.format(sql, data))
                cu.execute(sql, d)
                r = cu.fetchall()
                if len(r) > 0:
                    for e in range(len(r)):
                        print(r[e])
                self.close_all(conn, cu)
            else:
                print('the [{}] equal None!'.format(data))
        else:
            print('the [{}] is empty or equal None!'.format(sql))

    def update(self, sql, data):
        """
        更新数据
        """
        if sql is not None and sql != '':
            if data is not None:
                conn = self.get_conn()
                cu = self.get_cursor(conn)
                for d in data:
                    #if self.SHOW_SQL:
                        #print('执行sql:[{}],参数:[{}]'.format(sql, d))
                    cu.execute(sql, d)
                    conn.commit()
                self.close_all(conn, cu)
        else:
            print('the [{}] is empty or equal None!'.format(sql))

    def delete(self, sql, data):
        """
        删除数据
        """
        if sql is not None and sql != '':
            if data is not None:
                conn = self.get_conn()
                cu = self.get_cursor(conn)
                for d in data:
                    if self.SHOW_SQL:
                        print('执行sql:[{}],参数:[{}]'.format(sql, d))
                    cu.execute(sql, d)
                    conn.commit()
                self.close_all(conn, cu)
        else:
            print('the [{}] is empty or equal None!'.format(sql))

def create_table_docIds(mydb):
    create_table_sql = '''CREATE TABLE `docIds` (
                          `case_name` varchar(200) NOT NULL,
                          `judi_date` varchar(10) DEFAULT NULL,
                          `summary` varchar(2000) DEFAULT NULL,
                          `case_no` varchar(200) DEFAULT NULL,
                          `docid` varchar(50) PRIMARY KEY DEFAULT NULL,
                          'judi_process' varchar(50) DEFAULT NULL,
                          'court_name' varchar(50) DEFAULT NULL,
                          'private_reason' varchar(50) DEFAULT NULL,
                          'case_type' varchar(50) DEFAULT NULL,
                          'beDownloaded' INTEGER default 0
                        )'''
    try:
        mydb.create_table(create_table_sql)
    except Exception,e:
        print e
def insert_data_docIds(mydb,data):
    sql = '''INSERT INTO docIds values (?, ?, ?, ?, ?, ?, ?, ?, ?)'''
    mydb.insert(sql, data)      
def get_params_list(mydb):
    sql = '''SELECT param,count FROM Params where beDownloaded=0'''
    data = mydb.fetchall(sql)
    return data
def get_params_all(mydb):
    sql = '''SELECT param,count,beDownloaded FROM Params'''
    data = mydb.fetchall(sql)
    return data
def update_bedownloadedstatus(mydb,param):
    update_sql = 'UPDATE Params SET beDownloaded = 1 WHERE param = ? '
    mydb.update(update_sql,[(param,)])

def create_table_Params(mydb):
    create_table_sql = '''CREATE TABLE `Params` (
                          `param` varchar(500) PRIMARY KEY NOT NULL,
                          'count' int NOT NULL,
                          'refreshtime' int NOT NULL,
                          'beDownloaded' INTEGER default 0
                        )'''
    try:
        mydb.create_table(create_table_sql)
    except Exception,e:
        print e

def create_table_content(mydb):
    create_table_sql = '''CREATE TABLE `Content` (
                          `docId` varchar(500) PRIMARY KEY NOT NULL,
                          'title' varchar(500) NOT NULL,
                          'pubdate' varchar(500) NOT NULL,
                          'content' varchar(5000) NOT NULL
                        )'''
    try:
        mydb.create_table(create_table_sql)
    except Exception,e:
        print e

def insert_data_Params(mydb,data):
    sql = '''INSERT INTO Params values (?, ?, ?, ?)'''
    mydb.insert(sql, data) 

def create_table_court(mydb):

    create_table_sql = '''CREATE TABLE `court` (
                          `court_level` varchar(200) NOT NULL,
                          `court_parent` varchar(10) DEFAULT NULL,
                          `court_name` varchar(2000) PRIMARY KEY NOT NULL
                        )'''
    try:
        mydb.create_table(create_table_sql)
    except Exception,e:
        print e

def insert_data_court(mydb,data):
    sql = '''INSERT INTO court values (?, ?, ?)'''
    mydb.insert(sql, data) 

def get_court_list(mydb):
    sql = '''SELECT * FROM court where be_getParams=0'''
    data = mydb.fetchall(sql)
    return data

def update_begetparamsstatus(mydb,court_name):
    update_sql = 'UPDATE court SET be_getParams = 1 WHERE court_name = ? '
    mydb.update(update_sql,[(court_name,)])

def update_beDownloadedContent(mydb,docid):
    update_sql = 'UPDATE docIds SET beDownloaded = 1 WHERE docid = ? '
    mydb.update(update_sql,[(docid,)])

def insert_data_Content(mydb,data):
    sql = '''INSERT INTO content values(?,?,?,?)'''
    mydb.insert(sql,data)
def get_docIds(mydb):
    sql = '''SELECT * FROM docIds where beDownloaded=0'''
    data = mydb.fetchall(sql)
    return data
def get_docIds_inRange(mydb,start,last):
    sql = '''SELECT rowid,case_name,judi_date,summary,case_no,docid,judi_process,court_name,private_reason,case_type FROM docIds where rowid>=%d and rowid<=%d'''%(start,last)
    data = mydb.fetchall(sql)
    return data

def get_docIds_All(mydb):
    sql = '''SELECT rowid,case_name,judi_date,summary,case_no,docid,judi_process,court_name,private_reason,case_type FROM docIds'''
    data = mydb.fetchall(sql)
    return data
