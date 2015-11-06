
import ConfigParser
import json

import numpy
from utils_st import dbtool
from utils_st.dbtool import RedisManger

E2 = "platform_quantitative_data_E2"
TK = "platform_quantitative_data_ave_K"
E3 = "E3_quantitative_score"
transK = {
    "borrower_hhi":"borrower_HHI",
    "pr_transparency1":"PR_transparency1"
}
class ALevel:
    """
    db1:dev
    db2:db_w
    """

    def __init__(self,configlevel,config):
        A = []
        B = []
        AB = []
        C = []
        self.T = {}
        self.prement = {}
        self.data = {}

        for  item in configlevel.items("base"):
            if transK.has_key(item[0]):
                item = (transK[item[0]],item[1])
            # if item[0] != 'borrower_HHI':
            #     continue
            if item[1] == '0':
                a = configlevel.getint("ratio_a",item[0])
                A.append([item[0],a])
            elif item[1] == "1":
                b = configlevel.getint("ratio_b",item[0])
                B.append([item[0],b])
            elif item[1] == "2":
                a = configlevel.getint("ratio_a",item[0])
                b = configlevel.getint("ratio_b",item[0])
                AB.append([item[0],a,b])
            elif item[1] == "3":
                c = configlevel.getfloat("ratio_c",item[0])
                C.append([item[0],c])
            self.T[item[0]] = item[1]
            try:
                premethod = configlevel.getint("premethod",item[0])
            except:
                premethod = 0
            self.prement[item[0]] = premethod

        self.A = A
        self.B = B
        self.AB = AB
        self.C = C
        self.basetime = configlevel.getint("info","basetime")

        self.DB={}
        self.DB["db2"] = dbtool.newdb(config,"DB_W")



    def loaddata(self):
        "load "
        X ={}

        end = self.basetime + 86400*7*3
        self.start = end
        client = RedisManger.gettb(E2)
        data = {}
        i = 0
        l = []
        k = 0
        for platid in client.keys():
            tmp = []
            i += 1
            for date in client.hkeys(platid):
                t = int(date)
                if t < self.basetime or t > end:
                    continue
                jstr = client.hget(platid, date)
                jdata = json.loads(jstr)
                assert jdata
                jdata["date"] = date
                tmp.append(jdata)
            if len(tmp) < 4:
                continue
            data[platid] = sorted(tmp,key=lambda x:x["date"])
            k += 1

        R = {}
        for key in self.T:
            R[key] = [[],[],[],[]]
        for platid in data:
            for i in range(0,4):
                for key in self.T:
                    try:
                        if data[platid][i][key] > 0:
                            R[key][i].append(data[platid][i][key])
                    except:
                        pass
        for k,p in self.A:
            R0 = R[k]
            R3 = []
            for R1 in R0:
                R1.sort(reverse=True)
                d =getXp1(R1,p)
                R3.append(d)
            X[k] = numpy.mean(R3)

        for k,p in self.B:
            R0 = R[k]
            R3 = []
            for R1 in R0:
                R1.sort()
                d = getXp1(R1,p)
                R3.append(d)
            X[k] = numpy.mean(R3)

        for k,p1,p2 in self.AB:
            R0 = R[k]
            R3 = [[],[]]
            for R1 in R0:
                if not R1:
                    continue 
                R1.sort()
                d1 = getXp1(R1, p1)
                d2 = getXp1(R1, p2)
                R3[0].append(d1)
                R3[1].append(d2)
            X[k] = numpy.array([numpy.mean(R3[0]),numpy.mean(R3[1])])

        for k,p in self.C:
            X[k] = p

        self.X = X

    def level(self):
        fields = [x for x in self.X]

        client = RedisManger.gettb(TK)
        data = []
        for date in client.hkeys("AVE"):
            t = int(date)
            if t <= self.basetime - 7*86400:
                continue
            jstr = client.hget("AVE", date)
            jdata =  json.loads(jstr)
            jdata['date'] = t
            data.append(jdata)

        if len(data) < 4:
            return
        AVE = sorted(data,key=lambda x:x["date"])

        i = 3
        X =self.X
        client = RedisManger.gettb(TK)
        client1 = RedisManger.gettb(E2)

        for d in AVE[3:]:
            t = d["date"]
            # print t
            MAX = {}
            MIN = {}
            MEAN = {}
            D = {}

            for key in self.X:
                if i != 3:
                    d1 = 0.0
                    d2 = 0.0
                    for k in range(0,4):
                        # print AVE[i-k][key],
                        try:
                            d1 += AVE[i-k][key]*(4-k)
                            d2 += AVE[i-k-1][key]*(4-k)
                        except:
                            pass
                    D[key] = d1/d2
                    self.X[key] *= D[key]

            i += 1
            S = {}
            NUM = {}
            NN = 0
            for platid in client1.keys():
                jstr = client1.hget(platid,t)
                if not jstr:
                    continue
                jdata = json.loads(jstr)
                for key in self.T.keys():
                    if not jdata[key]:
                        continue
                    if not MAX.has_key(key):
                        MAX[key] = jdata[key]
                        MIN[key] = jdata[key]
                        S[key] = jdata[key]
                        NUM[key] = 1
                    else:
                        if MAX[key] < jdata[key]:
                            MAX[key] = jdata[key]
                        elif MIN[key] > jdata[key]:
                            MIN[key] = jdata[key]
                        S[key] += jdata[key]
                        NUM[key] += 1

            for key in self.T.keys():
                MIN[key] = pretrans(MIN[key],self.prement[key])
                MAX[key] = pretrans(MAX[key],self.prement[key])
                MEAN[key] = pretrans(S[key]/NUM[key],self.prement[key])

            for platid in client1.keys():
                jstr = client1.hget(platid,t)
                if not jstr:
                    continue
                jdata = json.loads(jstr)

                for key in self.T:
                    if not jdata.has_key(key) or not jdata[key]:
                        continue
                    dd = jdata[key]
                    data = {
                    "platform_id":platid,
                    "index_name":key,
                    "index_value":dd
                    }
                    dd = pretrans(dd,self.prement[key])
                    if self.T[key] == "0" or self.T[key] == "3":
                        data['index_type'] = 1
                        data['a_level_1'] = self.X[key]
                        lva = pretrans(self.X[key],self.prement[key])
                        if key == "cash_flow_in":
                            if dd > lva:
                                result = 1
                                index_value_new = 100*(numpy.log(dd - MIN[key]))/(numpy.log(MAX[key] - MIN[key]))
                            else:
                                result = 2
                                if MAX[key] < lva:
                                    lva = MAX[key]
                                index_value_m = (dd - MIN[key])/(lva - MIN[key])
                                level_max = (numpy.log(lva - MIN[key]))/(numpy.log(MAX[key] - MIN[key]))
                                index_value_new = 100*(numpy.exp(index_value_m) - 1)/(numpy.exp(1)-1)*level_max
                        else:
                            if dd > lva:
                                result = 1
                                index_value_new = 100*(numpy.log(dd) - numpy.log(MIN[key]))/(numpy.log(MAX[key]) - numpy.log(MIN[key]))
                            else:
                                result = 2
                                if MAX[key] < lva:
                                    lva = MAX[key]
                                index_value_m = (dd - MIN[key])/(lva - MIN[key])
                                level_max = (numpy.log(lva) - numpy.log(MIN[key]))/(numpy.log(MAX[key]) - numpy.log(MIN[key]))
                                index_value_new = 100*(numpy.exp(index_value_m) - 1)/(numpy.exp(1)-1)*level_max
                    elif self.T[key] == "1":
                        data['index_type'] = 2
                        data['a_level_1'] = self.X[key]
                        lvb = pretrans(self.X[key],self.prement[key])
                        if dd > lvb:
                            result = 2
                            if lvb < MIN[key]:
                                lvb = MIN[key]
                            index_value_m = (MAX[key] - dd)/(MAX[key] - lvb)
                            e = (numpy.exp(index_value_m) - 1)/(numpy.exp(1) - 1)
                            tt = (numpy.log(MAX[key]) - numpy.log(lvb))/(numpy.log(MAX[key]) - numpy.log(MIN[key]))
                            index_value_new = 100*e*tt
                        else:
                            result = 1
                            index_value_new = 100*(numpy.log(MAX[key]) - numpy.log(dd))/(numpy.log(MAX[key]) - numpy.log(MIN[key]))
                    else:
                        data['index_type'] = 3
                        data['a_level_1'] = self.X[key][0]
                        data['a_level_2'] = self.X[key][1]
                        lva = pretrans(self.X[key][0],self.prement[key])
                        lvb = pretrans(self.X[key][1],self.prement[key])
                        ave = (lva+lvb)/2
                        if dd > lva and dd < lvb:
                            result = 1
                            if dd < ave:
                                index_value_new = 100*(numpy.log(dd) - numpy.log(MIN[key]))/(numpy.log(ave) - numpy.log(MIN[key]))
                            else:
                                index_value_new = 100*( numpy.log(MAX[key]) - numpy.log(dd))/(numpy.log(MAX[key]) - numpy.log(ave))
                        else:
                            result = 2
                            if dd < lva:
                                if MAX[key] < lva:
                                    lva = MAX[key]
                                index_value_m = (dd - MIN[key])/(lva - MIN[key])
                                e = (numpy.exp(index_value_m) - 1)/(numpy.exp(1) - 1)
                                tt = (numpy.log(lva) - numpy.log(MIN[key]))/(numpy.log(ave) - numpy.log(MIN[key]))
                                index_value_new = 100 * e * tt
                                # index_value_new = 100*(dd - MIN[key])/(MEAN[key] - MIN[key])
                            else:
                                if MIN[key] > lvb:
                                    lvb = MIN[key]
                                index_value_m = (dd - MAX[key])/(lvb - MAX[key])
                                e = (numpy.exp(index_value_m) - 1)/(numpy.exp(1) - 1)
                                tt = (numpy.log(MAX[key]) - numpy.log(lvb))/(numpy.log(MAX[key]) - numpy.log(ave))
                                index_value_new = 100 * e * tt
                    try:
                        assert index_value_new>=0 and index_value_new <= 100+0.0001
                    except:
                        continue
                    data['result'] = result
                    data['index_value_new'] =index_value_new
                    data['date'] = t
                    try:
#                         self.DB['db2'].insert2(data,"A_level_result")
#                         pass

                        if not self.data.has_key(platid):
                            self.data[platid] = {}
                        if not self.data[platid].has_key(t):
                            self.data[platid][t] = {}
                        self.data[platid][t][key] = index_value_new
                        # pass
                    except:
                        pass



def getXp(L,p):
    index = len(L)*p/100
    m = len(L)*p%100
    if m == 0:
        d =  L[index][0]
    else:
        d = (L[index][0]*m + L[index+1][0]*(100-m))/100
    return d
def pretrans(x,method):
    if method == 1:
        x += 1.0
    elif method == 2:
        x = x*100.0+1
    else:
        x = x*1.0
    return x
def getXp1(L,p):
    index = len(L)*p/100
    m = len(L)*p%100
    d = None
    if m == 0:
        try:
            d =  L[index]
        except:
            pass
    else:
        d = (L[index]*m + L[index+1]*(100-m))/100
    return d

def calcX(L,x0):
    x = x0
    X = [x]
    for i in range(0,len(L)-5):
        t0 = 0
        t1 = 0
        for j in range(1,5):
            t0 += L[i+j-1][1]*j
            t1 += L[i+j][1]*j
        if 0 == t0:
            break
        x =  t1/t0*x
        X.append(x)
    return X

def init(config):
    pass

if __name__ == "__main__":
    configlevel = ConfigParser.ConfigParser()
    config = ConfigParser.ConfigParser()
    configlevel.read("conf_st/alevel.ini")
    config.read("conf_st/redis.ini")

    aLevel = ALevel(configlevel,config)
    aLevel.loaddata()
    aLevel.level()
    client = RedisManger.gettb(E3)

    data = aLevel.data
    for platid in data:
        for date in data[platid]:
            jstr = client.hget(platid,date)
            if jstr:
                jdata = json.loads(jstr)
                for key in jdata:
                    if data[platid][date].has_key(key):
                        if jdata[key] != data[platid][date][key]:
                            jdata[key] = data[platid][date][key]
                s = json.dumps(jdata)
                client.hset(platid,date,s)