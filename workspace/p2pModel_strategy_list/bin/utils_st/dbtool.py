#!/usr/bin/python
import ConfigParser
import MySQLdb

import redis

class db:
    def __init__(self, Host, Username, Password, DB, Port):
        self.conn = MySQLdb.connect(host=Host, user=Username, passwd=Password, db=DB, port=Port)
        self.cur = self.conn.cursor()
        self.cur.execute("SET NAMES 'UTF8'")
        self.cur.execute("SET CHARACTER SET UTF8")
        self.cur.execute("SET CHARACTER_SET_RESULTS=UTF8")

    def getsites(self):
        SQLstring = "SELECT DISTINCT site_id FROM project_info"
        ret = self.cur.execute(SQLstring)
        if ret > 0:
            return self.cur.fetchall()
        else:
            return []

    def query(self, site_ID, date=0):
        SQLstring = "SELECT annulized_rating,loan_period,investor FROM project_info where site_id = '%s' " % site_ID

        ret = self.cur.execute(SQLstring)
        if ret > 0:
            return self.cur.fetchall()
        else:
            return []

    def insert(self, m, siteid="_"):
        keys = ""
        values = ""
        for k, value in m.iteritems():
            keys = keys + "m%s," % k
            values = values + "%s," % value
        print keys + "site_id", values + repr(siteid)

    def getinfo(self, site_ID):
        SQLstring = "SELECT name FROM platform_id_name where dcq_id = '%s'" % site_ID
        ret = self.cur.execute(SQLstring)
        if ret > 0:
            d = self.cur.fetchone()
            return {'site_name': d[0], 'site_id': site_ID}

    def get(self, fields, tb, where=None, isDISTINCT=False):

        if where:
            sqlstr = "select " + ("DISTINCT " if isDISTINCT else "") + "  {fields} from {tb} where {where}".format(
                fields=fields, tb=tb, where=where)
        else:
            sqlstr = "select " + ("DISTINCT " if isDISTINCT else "") + "{fields} from {tb}".format(fields=fields, tb=tb)
        # print sqlstr
        ret = self.cur.execute(sqlstr)
        if ret > 0:
            return self.cur.fetchall()
        else:
            return []


from RedisInfo import *


class RedisManger:
    dbID = 0
    DB = {}
    k2name = {}
    name = {}

    config = ConfigParser.ConfigParser()
    config.read("conf_st/redis.ini")
    REDISHOST=config.get("DBINFO","REDISHOST")
    REDISPORT=config.getint("DBINFO","REDISPORT")
    USERNAME=config.get("DBINFO","USERNAME")
    REDISPWD=config.get("DBINFO","REDISPWD")

    for table in TABLES:
        if table:
            DB[table['key']] = redis.Redis(host=REDISHOST, port=REDISPORT, db=table['db'])
            k2name[table['key']] = table['name']
            name[table['name']] = table['key']
            if table.has_key("remark"):
                name[table['remark']] = table['key']
            dbID += 1

    @classmethod
    def get(self,fields,condition,tb_k):
        print "select",fields
        print "where",condition
        print "from",self.k2name[tb_k]
    @classmethod
    def gettb(self, tb):
        return self.DB[self.name[tb]]
    @classmethod
    def existtb(self,tb):
        if self.name.has_key(tb):
            return True
        else:
            return False

class newdb:
    """ANA"""
    client = ""
    # client.get()

    def __init__(self, config, db):
        Host = config.get(db, "HOST")
        Username = config.get(db, "USERNAME")
        Password = config.get(db, "PASSWORD")
        DB = config.get(db, "DB")
        Port = config.getint(db, "PORT")

        self.conn = MySQLdb.connect(host=Host, user=Username, passwd=Password, db=DB, port=Port)
        self.cur = self.conn.cursor()
        self.cur.execute("SET NAMES 'UTF8'")
        self.cur.execute("SET CHARACTER SET UTF8")
        self.cur.execute("SET CHARACTER_SET_RESULTS=UTF8")

    def insert1(self, m, siteinfo, tb):
        keys = ""
        values = ""
        for k, value in m.iteritems():
            keys = keys + "%s," % k
            values = values + "%s," % value
        keys = keys + "site_id,site_name,date"
        values = values + "'{0}','{1}','{2}'".format(siteinfo["site_id"], \
                                                     siteinfo["site_name"], \
                                                     siteinfo['date']
                                                     )
        sqlstring = "insert into {tb} ({0})VALUES({1})".format(keys, values, tb=tb)
        self.cur.execute(sqlstring)
        self.conn.commit()


    def insert2(self, fields, tb):
        keys = ""
        values = ""
        for k, value in fields.iteritems():
            keys = keys + "`%s`," % k
            if isinstance(value, str):
                values = values + "'%s'," % value
            else:
                values = values + "%s," % value
        keys = keys[:-1]
        values = values[:-1]
        sqlstring = "insert into {tb} ({0}) VALUES ({1})".format(keys, values, tb=tb)
        self.cur.execute(sqlstring)
        self.conn.commit()

    def insert(self, m, siteinfo):
        keys = ""
        values = ""
        for k, value in m.iteritems():
            keys = keys + "m%s," % k
            values = values + "%s," % value
        keys = keys + "site_id,site_name,date"
        values = values + "'{0}','{1}','{2}'".format(siteinfo["site_id"], \
                                                     siteinfo["site_name"], \
                                                     siteinfo['date']
                                                     )
        sqlstring = "insert into Portfolio_site_interest_distribution ({0})VALUES({1})".format(keys, values)
        # print sqlstring
        self.cur.execute(sqlstring)
        self.conn.commit()

    def get(self, fields, tb, where=None):
        if self.client.existtb(tb):
            print tb
            return None
        else:
            return None
            if where:
                sqlstr = "select  {fields} from {tb} where {where}".format(fields=fields, tb=tb, where=where)
            else:
                sqlstr = "select  {fields} from {tb}".format(fields=fields, tb=tb)
            self.cur.execute(sqlstr)

    def getparam(self, date):
        sqlstr = "select site_id,belief,credit_transfer,payment_method from Portfolio_site_confidence_ATBscore where date = %s" % date
        ret = self.cur.execute(sqlstr)
        if ret > 0:
            Data = {}
            for data in self.cur.fetchall():
                Data[data[0]] = data[1:]
            return Data
        else:
            return {}

    def get(self, fields, tb, where=None, isDISTINCT=False,condtion={}):
        # if self.client.existtb(tb):
        #     if isinstance(fields,str):
        #         fields = fields.split(",")
        #     client.get()
        # else:
        #     return []

        if where:
            sqlstr = "select " + ("DISTINCT " if isDISTINCT else "") + "  {fields} from {tb} where {where}".format(
                fields=fields, tb=tb, where=where)
        else:
            sqlstr = "select " + ("DISTINCT " if isDISTINCT else "") + "{fields} from {tb}".format(fields=fields, tb=tb)
        # print sqlstr
        ret = self.cur.execute(sqlstr)
        if ret > 0:
            return self.cur.fetchall()
        else:
            return []

    def getone(self, fields, tb, where=None, isDISTINCT=False):
        if where:
            sqlstr = "select " + ("DISTINCT " if isDISTINCT else "") + "  {fields} from {tb} where {where}".format(
                fields=fields, tb=tb, where=where)
        else:
            sqlstr = "select " + ("DISTINCT " if isDISTINCT else "") + "{fields} from {tb}".format(fields=fields, tb=tb)
        # print sqlstr
        ret = self.cur.execute(sqlstr)
        if ret > 0:
            return self.cur.fetchone()
        else:
            return []

    def get1(self, fields, tb, where=None, isDISTINCT=False):
        if where:
            sqlstr = "select " + ("DISTINCT " if isDISTINCT else "") + "  {fields} from {tb} where {where}".format(
                fields=fields, tb=tb, where=where)
        else:
            sqlstr = "select " + ("DISTINCT " if isDISTINCT else "") + "{fields} from {tb}".format(fields=fields, tb=tb)
        # print sqlstr
        ret = self.cur.execute(sqlstr)
        if ret > 0:
            return self.cur.fetchone()
        else:
            return []

    def update(self, fields, tb, where=None):
        ss = ""
        for k, value in fields.iteritems():
            if isinstance(value,float):
                ss = ss + "`%s`=%s," % (k, value)
            else:
                ss = ss + "`%s`='%s'," % (k, value)
        ss = ss[:-1]
        sqlstring = "update  {tb} set {0} where {where}".format(ss, where=where, tb=tb)
        self.cur.execute(sqlstring)
        self.conn.commit()
    RedisManger





if __name__ == "__main__":
    pass

    # dbID = 0
    # for table in TABLES:
    #     print table['name']
    #     print table['key']
    #     r = redis.Redis(host=REDISHOST, port=REDISPORT, db=dbID)
    #     for platid in r.keys():
    #         print platid
    #         for date in r.hkeys(platid):
    #             print date
    #             print r.hget(platid, date)

