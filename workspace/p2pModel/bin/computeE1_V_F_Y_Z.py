#!/use/bin/python
#coding=utf-8

from atbtools.mysqlTools import *
from atbtools.header import *
from atbtools.computeTools import *

def changeRegisteredCap(_dict, _cur, _ratio):
    table_F = "platform_qualitative_F"
    stringSQL = "SELECT `platform_name`, `registered_cap`, `contributed_capital` FROM " + table_F
    _cur.execute(stringSQL)
    F_dict = {}
    for platform_name, registered_cap, contributed_capital in _cur.fetchall():
        if contributed_capital == None:
            F_dict[platform_name] = _ratio * float(registered_cap)
        elif contributed_capital == 0:
            F_dict[platform_name] = 1
        else:
            F_dict[platform_name] = contributed_capital
    for platform_name in _dict:
        if platform_name in F_dict:
            for date in _dict[platform_name]:
                _dict[platform_name][date]["registered_cap"] = F_dict[platform_name]
            
if __name__ == "__main__":
    
    conn_db = getConn(DBHOST_OUT, USERNAME, PASSWORD, DB, PORT)
    cur_db = getCursors(conn_db)
    conn_dev = getConn(DEVHOST_OUT, USERNAME, PASSWORD, DB, PORT)
    cur_dev = getCursors(conn_dev)
    conn_ddpt_test = getConn(DDPT_TESTHOST_OUT, USERNAME, PASSWORD, DB, PORT)
    cur_ddpt_test = getCursors(conn_ddpt_test)
    conn_ddpt_data = getConn(DDPT_DATAHOST_OUT, USERNAME, PASSWORD, DB, PORT)
    cur_ddpt_data = getCursors(conn_ddpt_data)
    initializeCursors(cur_db, cur_dev, cur_ddpt_test, cur_ddpt_data)

    E1_old = "platform_quantitative_data_E1"
    E1_new = "0_E1_quantitative_data"
    V_view = "V_view"
    View_mobile = "98_view_mobile_fake"
    View_mobile_real_to = "97_view_mobile_real"
    View_mobile_real_from = "view_mobile"
    F_old = "platform_qualitative_F"
    F_new = "1_platform_qualitative_F"
    Y_old = "total_status"
    Y_new = "2_total_status"
    Z_old = "platform_problem_doubt_Z"
    Z_new = "01_platform_problem_doubt_Z"
    
    #在测试集中增加E1表
    cur_ddpt_test.execute("DELETE FROM " + E1_new)
    conn_ddpt_test.commit()    
     
    field_list_E1 = getAllColumnsFromTable(cur_db, E1_old, del_list = ["id", "date", "platform_name"])
    field_number_E1 = len(field_list_E1)
    stringSQL = "SELECT `date`, `platform_name`, `" + "`, `".join(field_list_E1) + "` FROM " + E1_old
    cur_db.execute(stringSQL)
    E1_dict = {}
    for rets in cur_db.fetchall():
        date = rets[0]
        platform_name = rets[1]
        value_list = rets[2:]
        if platform_name not in E1_dict:
            E1_dict[platform_name] = {}
        E1_dict[platform_name][date] = {}
        for i in range(field_number_E1):
            field = field_list_E1[i]
            E1_dict[platform_name][date][field] = value_list[i]
      
    #增加实缴资本代替注册资本的策略
    #changeRegisteredCap(E1_dict, cur_db, 1.0/3)
      
    #将新的E1写入
    for platform_name in E1_dict:
        for date in E1_dict[platform_name]:
            value_list = []
            for field in field_list_E1:
                value_list.append(str(E1_dict[platform_name][date][field]))
            stringSQL = "INSERT INTO " + E1_new + "(`" + "`,`".join(["platform_name", "date"] + field_list_E1) + "`) VALUES('" + "','".join([platform_name, str(date)] + value_list) + "')"
            stringSQL = stringSQL.replace("'None'", "NULL")
            cur_ddpt_test.execute(stringSQL)
        conn_ddpt_test.commit()
          
    print "E1准备完毕."
 
    #在测试集中增加view_mobile_fake表
    cur_ddpt_test.execute("DELETE FROM " + View_mobile)
    conn_ddpt_test.commit()  
     
    field_list_V = getAllColumnsFromTable(cur_ddpt_data, V_view, del_list = ["id", "date", "platform_name", "downgrading_info", "none_downgrading_info", "punishment", "punishment_info"])
    field_number_V = len(field_list_V)
    max_date = getDifferentFieldlist(V_view, cur_ddpt_data, "date")[-1]
    stringSQL = "SELECT `platform_name`, `" + "`, `".join(field_list_V) + "` FROM " + V_view + " WHERE `date` = '" + str(max_date) + "'"
    cur_ddpt_data.execute(stringSQL)
    V_dict = {}
    for rets in cur_ddpt_data.fetchall():
        platform_name = rets[0]
        value_list = rets[1:]
        V_dict[platform_name] = {}
        for i in range(field_number_V):
            field = field_list_V[i]
            V_dict[platform_name][field] = value_list[i]
     
    #将新的view_mobile写入
    for platform_name in V_dict:
        value_list = []
        for field in field_list_V:
            value_list.append(str(V_dict[platform_name][field]))
        stringSQL = "INSERT INTO " + View_mobile + "(`" + "`,`".join(["platform_name", "date"] + field_list_V) + "`) VALUES('" + "','".join([platform_name, str(max_date)] + value_list) + "')"
        stringSQL = stringSQL.replace("'None'", "NULL")
        cur_ddpt_test.execute(stringSQL)
        conn_ddpt_test.commit()
 
    print "view_mobile_fake准备完毕."
    
    #在测试集中增加view_mobile_real表
    cur_ddpt_test.execute("DELETE FROM " + View_mobile_real_to)
    conn_ddpt_test.commit()  
     
    field_list_view_mobile = getAllColumnsFromTable(cur_dev, View_mobile_real_from, del_list = ["id", "date", "platform_name"])
    field_number_view_mobile = len(field_list_view_mobile)
    max_date = getDifferentFieldlist(View_mobile_real_from, cur_dev, "date")[-1]
    stringSQL = "SELECT `platform_name`, `" + "`, `".join(field_list_view_mobile) + "` FROM " + View_mobile_real_from + " WHERE `date` = '" + str(max_date) + "'"
    cur_dev.execute(stringSQL)
    view_mobile_dict = {}
    for rets in cur_dev.fetchall():
        platform_name = rets[0]
        value_list = rets[1:]
        view_mobile_dict[platform_name] = {}
        for i in range(field_number_view_mobile):
            field = field_list_view_mobile[i]
            view_mobile_dict[platform_name][field] = value_list[i]
     
    #将新的view_mobile写入
    for platform_name in view_mobile_dict:
        value_list = []
        for field in field_list_view_mobile:
            value_list.append(str(view_mobile_dict[platform_name][field]))
        stringSQL = "INSERT INTO " + View_mobile_real_to + "(`" + "`,`".join(["platform_name", "date"] + field_list_view_mobile) + "`) VALUES('" + "','".join([platform_name, str(max_date)] + value_list) + "')"
        stringSQL = stringSQL.replace("'None'", "NULL")
        cur_ddpt_test.execute(stringSQL)
        conn_ddpt_test.commit()
 
    print "view_mobile_real准备完毕."
     
    #在测试集中增加F表
    cur_ddpt_test.execute("DELETE FROM " + F_new)
    conn_ddpt_test.commit()  
     
    field_list_F = getAllColumnsFromTable(cur_db, F_old, del_list = ["id", "platform_name"])
    field_number_F = len(field_list_F)
    stringSQL = "SELECT `platform_name`, `" + "`, `".join(field_list_F) + "` FROM " + F_old
    cur_db.execute(stringSQL)
    F_dict = {}
    for rets in cur_db.fetchall():
        platform_name = rets[0]
        value_list = rets[1:]
        F_dict[platform_name] = {}
        for i in range(field_number_F):
            field = field_list_F[i]
            F_dict[platform_name][field] = value_list[i]
     
    #将新的F写入
    for platform_name in F_dict:
        value_list = []
        for field in field_list_F:
            value_list.append(str(F_dict[platform_name][field]))
        stringSQL = "INSERT INTO " + F_new + "(`" + "`,`".join(["platform_name"] + field_list_F) + "`) VALUES('" + "','".join([platform_name] + value_list) + "')"
        stringSQL = stringSQL.replace("'None'", "NULL")
        cur_ddpt_test.execute(stringSQL)
        conn_ddpt_test.commit()
 
    print "F表准备完毕."
    
    #在测试集中增加Y表
    cur_ddpt_test.execute("DELETE FROM " + Y_new)
    conn_ddpt_test.commit()    
    
    field_list_Y = getAllColumnsFromTable(cur_db, Y_old, del_list = ["id", "date", "platform_name"])
    field_number_Y = len(field_list_Y)
    stringSQL = "SELECT `date`, `platform_name`, `" + "`, `".join(field_list_Y) + "` FROM " + Y_old
    cur_db.execute(stringSQL)
    Y_dict = {}
    for rets in cur_db.fetchall():
        date = rets[0]
        platform_name = rets[1]
        value_list = rets[2:]
        if platform_name not in Y_dict:
            Y_dict[platform_name] = {}
        Y_dict[platform_name][date] = {}
        for i in range(field_number_Y):
            field = field_list_Y[i]
            Y_dict[platform_name][date][field] = value_list[i]
     
    #将新的Z写入
    for platform_name in Y_dict:
        for date in Y_dict[platform_name]:
            value_list = []
            for field in field_list_Y:
                value_list.append(str(Y_dict[platform_name][date][field]))
            stringSQL = "INSERT INTO " + Y_new + "(`" + "`,`".join(["platform_name", "date"] + field_list_Y) + "`) VALUES('" + "','".join([platform_name, str(date)] + value_list) + "')"
            stringSQL = stringSQL.replace("'None'", "NULL")
            cur_ddpt_test.execute(stringSQL)
        conn_ddpt_test.commit()

    print "Y表准备完毕."
    
    #在测试集中增加Z表
    cur_ddpt_test.execute("DELETE FROM " + Z_new)
    conn_ddpt_test.commit()    
    
    field_list_Z = getAllColumnsFromTable(cur_db, Z_old, del_list = ["id", "date", "platform_name"])
    field_number_Z = len(field_list_Z)
    stringSQL = "SELECT `date`, `platform_name`, `" + "`, `".join(field_list_Z) + "` FROM " + Z_old
    cur_dev.execute(stringSQL)
    Z_dict = {}
    for rets in cur_dev.fetchall():
        date = rets[0]
        platform_name = rets[1]
        value_list = rets[2:]
        if platform_name not in Z_dict:
            Z_dict[platform_name] = {}
        Z_dict[platform_name][date] = {}
        for i in range(field_number_Z):
            field = field_list_Z[i]
            Z_dict[platform_name][date][field] = value_list[i]
     
    #将新的Z写入
    for platform_name in Z_dict:
        for date in Z_dict[platform_name]:
            value_list = []
            for field in field_list_Z:
                value_list.append(str(Z_dict[platform_name][date][field]))
            stringSQL = "INSERT INTO " + Z_new + "(`" + "`,`".join(["platform_name", "date"] + field_list_Z) + "`) VALUES('" + "','".join([platform_name, str(date)] + value_list) + "')"
            stringSQL = stringSQL.replace("'None'", "NULL")
            cur_ddpt_test.execute(stringSQL)
        conn_ddpt_test.commit()

    print "Z表准备完毕."    
    closeCursors(cur_db, cur_dev, cur_ddpt_test, cur_ddpt_data)
    closeConns(conn_db, conn_dev, conn_ddpt_test, conn_ddpt_data)
