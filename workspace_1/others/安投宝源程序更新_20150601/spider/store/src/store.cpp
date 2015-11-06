#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <iostream>
#include <string>
#include <map>
#include <mysql/mysql.h>
#include "../../common/spi_utils/spi_utils.h"

using namespace std;

string escape_string(MYSQL *mysql, const string &str)
{
    char *buf = (char *)malloc(str.size() * 2 + 1);
    if (!buf) {
        return "";
    }
    mysql_real_escape_string(mysql, buf, str.c_str(), str.size());
    string ret(buf);
    free(buf);
    return ret;
}

enum DB_FIELD_TYPE {
    DB_FIELD_TYPE_INT = 0,
    DB_FIELD_TYPE_FLOAT,
    DB_FIELD_TYPE_TEXT,
    DB_FIELD_TYPE_NUM,
};

typedef struct _dbdef_t {
    char field[32];
    enum DB_FIELD_TYPE type;
} dbdef_t;

dbdef_t dbdef[] = {
    {"annulized_rating", DB_FIELD_TYPE_TEXT},
    {"borrower", DB_FIELD_TYPE_TEXT},
    {"borrowing_amount", DB_FIELD_TYPE_FLOAT},
    {"credit_rating", DB_FIELD_TYPE_TEXT},
    {"end_time", DB_FIELD_TYPE_TEXT},
    {"guarantee", DB_FIELD_TYPE_TEXT},
    {"invested_amount", DB_FIELD_TYPE_FLOAT},
    {"investor", DB_FIELD_TYPE_TEXT},
    {"investor_volume", DB_FIELD_TYPE_INT},
    {"loan_period", DB_FIELD_TYPE_INT},
    {"maximum_investment", DB_FIELD_TYPE_FLOAT},
    {"minimum_investment", DB_FIELD_TYPE_FLOAT},
    {"payment_method", DB_FIELD_TYPE_TEXT},
    {"project_category", DB_FIELD_TYPE_TEXT},
    {"project_details", DB_FIELD_TYPE_TEXT},
    {"project_id", DB_FIELD_TYPE_TEXT},
    {"project_name", DB_FIELD_TYPE_TEXT},
    {"release_time", DB_FIELD_TYPE_TEXT},
    {"site_id", DB_FIELD_TYPE_TEXT},
};

long long findid(MYSQL *mysql, map <string, string> &kv)
{
    string query = "SELECT id FROM project_info WHERE site_id='" + kv["site_id"] + "' AND project_id='" + kv["project_id"] + "'";
    mysql_real_query(mysql, query.c_str(), query.size());

    MYSQL_RES *res = mysql_store_result(mysql);
    MYSQL_ROW r;
    unsigned int num_f = mysql_num_fields(res);
    long long id = -1;
    while ((r = mysql_fetch_row(res))) {
        unsigned long *len = mysql_fetch_lengths(res);
        if (num_f > 0 && len[0] > 0) {
            id = atoll(r[0]);
        }
    }
    mysql_free_result(res);

    return id;
}

int update_record(MYSQL *mysql, long long id, map <string, string> &kv)
{
    string query;
    for (int i = 0; i < sizeof(dbdef)/sizeof(dbdef[0]); i++) {
        string key = string(dbdef[i].field);
        map <string, string>::iterator iter = kv.find(key);
        if (iter == kv.end()) {
            continue;
        }
        if (query.size() > 0) {
            query += ", ";
        }
        switch (dbdef[i].type) {
            case DB_FIELD_TYPE_INT:
                query += key + "=" + longtostring(atol(iter->second.c_str()));
                break;
            case DB_FIELD_TYPE_FLOAT:
                query += key + "=" + doubletostring(atof(iter->second.c_str()));
                break;
            case DB_FIELD_TYPE_TEXT:
                query += key + "='" + escape_string(mysql, iter->second) + "'";
                break;
            default:
                break;
        }
    }
    if (query.size() == 0) {
        return 0;
    }
    if (id < 0) {
        query = "INSERT INTO project_info SET " + query + ", create_time='" + longtostring(time(NULL)) + "'";
    }
    else {
        query = "UPDATE project_info SET " + query + " WHERE id=" + longtostring(id);
    }
    return mysql_real_query(mysql, query.c_str(), query.size());
}

int storedata(const char *filename)
{
    map <string, string> kv;
    if (loadstringmap(kv, filename) != 0) {
        return 1;
    }

    MYSQL *mysql = mysql_init(NULL);
    if (!mysql_real_connect(mysql, "db-for-spider", "root", "4njMOzOjli", "antoubao", 0, NULL, 0)) {
        mysql_close(mysql);
        return 1;
    }
    mysql_set_character_set(mysql, "utf8");

    long long id = findid(mysql, kv);
    update_record(mysql, id, kv);

    mysql_close(mysql);
    
    return 0;
}

int main(int argc, char *argv[])
{
    if (argc < 2) {
        return 0;
    }
    return storedata(argv[1]);
}

