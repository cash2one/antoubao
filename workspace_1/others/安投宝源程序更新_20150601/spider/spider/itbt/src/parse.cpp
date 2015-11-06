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
    map <string, string> kv;
    kv["site_id"] = "itbt";
    kv["borrower"] = extract(bstr,"<b  class=\"icon-img","/></a><br /><a","\">","</a><br />");
    kv["project_name"] = extract(bstr, "<head><meta http-equiv", "/><title>", "_","</title>");
    kv["project_id"] = extract(bstr,"type=\"text/css","/><input id=","type=\"hidden\" value=\"","\"><input");
    kv["borrowing_amount"] = extract(bstr,"<li class=\"w1\">","融资总额","￥","</b>");
    string::size_type pos = kv["borrowing_amount"].find("万");
    if (pos != string::npos){
        kv["borrowing_amount"] = doubletostring(atof(filternum(kv["borrowing_amount"]).c_str())*10000);
    } else{
        kv["borrowing_amount"] = doubletostring(atof(filternum(kv["borrowing_amount"]).c_str()));
    }  

    kv["annulized_rating"] = filternum(extract(bstr,"","年利率", "<br /><b>", "%</b></li>"));
    kv["payment_method"] = extract(bstr,"</p><p class=\"bao\">","<b class=\"icon-img","\"></b>","</p></div>");
    kv["loan_period"] = extract(bstr, "", "融资期限", "<br /><b><span>","</b><b class=");
    int pos1 = kv["loan_period"].find("月");
    if (pos1 != -1) {
        kv["loan_period"] = longtostring(atof(kv["loan_period"].c_str())*30);
    }
    else{

        kv["loan_period"] = longtostring(atof(kv["loan_period"].c_str()));
    }

//     kv["invested_amount"] = doubletostring(s_atod(kv["borrowing_amount"].c_str()) - s_atod(filternum(extract(bstr,"<li>"," 剩余金额:","￥","元")).c_str()));
     long long etime1 = stringtotime(extract(bstr,"<ul><li>","开始时间","<b>","</b></li><li>").c_str(), "%Y-%m-%d %H:%M:%S");
     if (etime1 > 1000000000) {
         kv["release_time"] = longtostring(etime1);
     }
//    kv["project_details"] = extract(bstr,"借款详情","资料审核","投标记录","</p></td></tr></tbody></table>");
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
            p += len;
            Value json = stringtojson(jstr);
            if (!has_object_member(json, "data")
                ||  !has_object_member(json["data"], "tb")  || !has_array_member(json["data"]["tb"], "Rows")) {
                continue;
            }
            for (int i = 0; i < json["data"]["tb"]["Rows"].size(); i++) {
                string account;
                string addtime;
                string username;
                if (!get_string_member(json["data"]["tb"]["Rows"][i], "account", account)
                        || !get_string_member(json["data"]["tb"]["Rows"][i], "addtime", addtime)
                        || !get_string_member(json["data"]["tb"]["Rows"][i], "username", username)) {
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

    if (kv["project_id"] == "" || s_atol(kv["borrowing_amount"].c_str()) <= 0) {
        return 1;
    }
    printstringmap(kv);
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

    
    
