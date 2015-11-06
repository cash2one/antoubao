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
    kv["site_id"] = "edai";
    kv["credit_rating"] = "0";
    kv["project_name"] = extract(bstr, "<span class=\"cur\">项目详情", "class=\"item-detail-head clearfix\"", "<div class=\"hd\">", "</div>");;
    kv["project_id"] = extract(bstr, "class=\"data\"", "class=\"c-888\"", "</span>", "</li>");
    kv["borrowing_amount"] = filternum(extract(bstr, "class=\"data\"", "借款金额", "id=\"account\">", "元"));
    kv["annulized_rating"] = filternum(extract(bstr, "class=\"relative\"", "年利率", "class=\"f30 c-orange\">", "%"));
    kv["payment_method"] = extract(bstr, "class=\"data\"", "还款方式：", ">", "</li>");
    kv["award"] = "";
    kv["loan_period"] = longtostring(s_atod(extract(bstr, "class=\"data\"", "借款期限", ">", "个月").c_str()) * 30);
    kv["minimum_investment"] = extract(bstr, "class=\"data\"", "投资范围", ">","元");
    kv["maximum_investment"] = "";
    kv["release_time"] = longtostring(stringtotime(extract(bstr, "class=\"data\"", "发标日期：", "</span>", "</li>").c_str(), "%Y-%m-%d"));
    kv["project_details"] = extract(bstr, "class=\"bd bd_nav\"", "<div class=\"borrow-info\">", "借款人介绍", "<dl class=\"item\">");
    kv["end_time"] = "0";
    kv["invested_amount"] =  filternum(extract(bstr, "class=\"repayment-list\"", "目前投标总额：", "￥", "元"));
    kv["borrower"] = "0";
    vector <string> vstr;
    strtovstr(vstr, kv["project_details"].c_str(), "\n");
    for (size_t i = 0; i < vstr.size(); i++) {
        string tmp = dhtml(vstr[i]);
        if (tmp.find("借款人") != string::npos && tmp.find("介绍") == string::npos) {
            kv["borrower"] = tmp;
            break;
        }
    }

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
            if (!has_object_member(json, "list")) {
                continue;
            }
            for (int i = 1; i <= 100; i++) {
                string title = longtostring(i);
                string uname;
                string addtime;
                string account;
                if (!has_object_member(json["list"], title.c_str())
                        || !get_string_member(json["list"][title], "username", uname)
                        || !get_string_member(json["list"][title], "account", account)
                        || !get_string_member(json["list"][title], "addtime", addtime)) {
                    break;
                }
                addtime = longtostring(stringtotime(addtime.c_str(), "%Y-%m-%d %H:%M:%S"));
                invstr += addtime + "|" + uname + "|" + account + "|";
                invnum++;
            }
        }
        free(buf);
    }
    kv["investor"] = invstr;
    kv["investors_volume"] = longtostring(invnum);

    printstringmap(kv);

    if (s_atol(kv["borrowing_amount"].c_str()) <= 0) {
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
