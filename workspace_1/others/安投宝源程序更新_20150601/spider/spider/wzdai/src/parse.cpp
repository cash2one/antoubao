#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <string>
#include <map>
#include "../../common/utils/json_utils.h"
#include "../../common/utils/utils.h"
#include "../../common/spi_utils/spi_utils.h"

using namespace std;

int parsefile(const char *idstr)
{
    char filename[256];
    sprintf(filename, "html/%s", idstr);
    char *buf = readfile(filename);
    if (!buf) {
        return 1;
    }
    
    string bstr = string(buf);
    free(buf);
    if (bstr.size() > 5) {
        bstr = bstr.substr(5, bstr.size()-6);
    }
    
    map <string, string> kv;

    Value wzdai = stringtojson(bstr);
        
    kv["site_id"] = "wzdai";
    kv["borrower"] = wzdai["user"]["username"].asString();
    kv["project_name"] = wzdai["borrow"]["name"].asString();
    kv["project_id"] = idstr;
    kv["borrowing_amount"] = wzdai["borrow"]["account"].asString();
    kv["annulized_rating"] = doubletostring(wzdai["borrow"]["apr"].asDouble());
    kv["payment_method"] = "";
    kv["loan_period"] = doubletostring(wzdai["borrow"]["time_limit"].asDouble() * 30);
    kv["minimum_investment"] = "";
    kv["release_time"] = "";
    kv["end_time"] = "";
    kv["project_details"] = wzdai["borrow"]["content"].asString();  
    

    sprintf(filename, "html/%s.brec", idstr);
    buf = readfile(filename);
    string invstr;
    int invnum = 0;
    if (buf) {
        char *p = buf;
        size_t buflen = strlen(buf);
        while (p < buf + buflen - 8) {
            int len;
            if (sscanf(p, "%08X", &len) != 1) {
                break;
            }
            p += 8;
            string jstr = string(p, len);
            if (jstr.size() > 5) {
                jstr = jstr.substr(5, jstr.size()-6);
            }
            p += len;
            Value json = stringtojson(jstr);
//            printf("%s\n", jsontostring(json).c_str());
            if (!has_object_member(json, "data")
                    || !has_array_member(json["data"], "list")) {
                continue;
            }
            for (int i = 0; i < json["data"]["list"].size(); i++) {
                string account;
                string addtime;
                string username;
                if (!get_string_member(json["data"]["list"][i], "account", account)
                        || !get_string_member(json["data"]["list"][i], "addtime", addtime)
                        || !get_string_member(json["data"]["list"][i], "username", username)) {
                    continue;
                }
                invstr += addtime + "|" + username + "|" + account + "|";
                invnum++;
            }
        }
        free(buf);
    }
    kv["investor"] = invstr;
    kv["investors_volume"] = longtostring(invnum);
    printstringmap(kv);

    if (kv["project_id"] == "" || s_atol(kv["borrowing_amount"].c_str()) <= 0) {
        return 1;
    }

    sprintf(filename, "data/%s", idstr);
    return savestringmap(kv, filename);
}

int main(int argc, char *argv[])
{
    if (argc < 2) {
        return 0;
    }
    return parsefile(argv[1]);
}

