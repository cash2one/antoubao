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
    kv["site_id"] = "haolip2p";
    kv["borrower"] = extract(bstr,"td1\">","pic\">","\"name\">","</div>");
    kv["credit_rating"] = extract(bstr, "div class=\"table2\"", "还款方式", "<td class=\"", "\">");
    kv["project_name"] = extract(bstr,"<td colspan=\"4","class=\"td2","class=\"tbt\">","</div>");
    kv["project_id"] = extract(bstr,"if(vbidmin","act=invest","&aid=","&money=");
    kv["borrowing_amount"] = filternum(extract(bstr, "借款金额", "截止时间", "<strong>", "</strong>元"));
    kv["annulized_rating"] = filternum(extract(bstr, "截止时间", "元</td>", "<strong>", "%</strong>"));
    kv["payment_method"] = extract(bstr,"保障方式","还款方式","<span>","</span>");
    kv["award"] = "";
    kv["loan_period"] = extract(bstr, "还款期限", "%</strong>", "<strong>", "</strong>个月");
    kv["loan_period"] = doubletostring(atof(kv["loan_period"].c_str())*30); 
    kv["invested_amount"] = longtostring(s_atol(kv["borrowing_amount"].c_str()) - s_atol(filternum(extract(bstr,"<td class=\"td1","标的余额","<strong>","</strong>元")).c_str()));
    kv["minimum_investment"] = "0";
    kv["maximum_investment"] = "0";
    kv["release_time"] = "0";
    kv["end_time"]=longtostring(stringtotime(extract(bstr,"<div class=\"content\">","id=\"endtime\"", " v=\"","\">").c_str(),"%Y-%m-%d %H:%M:%S"));
    kv["project_details"] = extract(bstr,"bt1","借款信息","<div class=\"text1\">","<div class=");
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
            if (!has_array_member(json, "data")
               ) {
                continue;
            }
            for (int i = 0; i < json["data"].size(); i++) {
                string account;
                string addtime;
                string username;
                if (!get_string_member(json["data"][i], "N_amount", account)
                        || !get_string_member(json["data"][i], "Createtime", addtime)
                        || !get_string_member(json["data"][i], "uname", username)) {
                    continue;
                }
                addtime = longtostring(stringtotime(addtime.c_str(), "%Y-%m-%d %H:%M:%S"));
                invstr += addtime + "|" + username + "|" + account + "|";
                invnum++;
            }
        }
        free(buf);
    }
    kv["investor"] = invstr;
    kv["investors_volume"] = longtostring(invnum);

    printstringmap(kv);

    if (kv["project_id"] == "" || kv["release_time"] == "") {
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
