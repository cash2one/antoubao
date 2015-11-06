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
    kv["site_id"] = "jinshangdai";
    kv["borrower"] = extract(bstr,"<span> ","<div class=\"msg\">","会员名：","</span>");
    kv["project_name"] = extract(bstr, "<div id=\"main\"", "<div class=\"title", "<a title=\"","\">");
    kv["project_id"] = extract(bstr," <input type=\"hidden\"","name=\"borrow_id\"","value=\"","\" />");
    kv["borrowing_amount"] = extract(bstr,"</div> ","借款金额","\"/>","元");
    string::size_type pos = kv["borrowing_amount"].find("万");
    if (pos != string::npos){
        kv["borrowing_amount"] = doubletostring(atof(filternum(kv["borrowing_amount"]).c_str())*10000);
    } else{
        kv["borrowing_amount"] = doubletostring(atof(filternum(kv["borrowing_amount"]).c_str()));
    }  

    kv["annulized_rating"] = filternum(extract(bstr,"<ul class","借款金额", "年利率：", "%"));
    kv["payment_method"] = extract(bstr,"借款金额","年利率","还款方式：","</li>");
    kv["loan_period"] = extract(bstr, "<li>", "剩余金额", "借款期限："," </li>");
    int pos1 = kv["loan_period"].find("月");
    if (pos1 != -1) {
        kv["loan_period"] = longtostring(atof(kv["loan_period"].c_str())*30);
    }
    else{

        kv["loan_period"] = longtostring(atof(kv["loan_period"].c_str()));
    }

     kv["invested_amount"] = doubletostring(s_atod(kv["borrowing_amount"].c_str()) - s_atod(filternum(extract(bstr,"<li>"," 剩余金额:","￥","元")).c_str()));
     kv["release_time"] = extract(bstr,"<div class=\"rate_tiao","<div class=\"smum\">","时间：","</li>");
    kv["project_details"] = extract(bstr,"借款详情","资料审核","投标记录","</p></td></tr></tbody></table>");
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

    
    
