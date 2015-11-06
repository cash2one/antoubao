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
    kv["site_id"] = "shuangfudai";
    kv["borrower"] = extract(bstr, "div class=\"box-info-user ", "用户名", ">", "<");
    kv["credit_rating"] = extract(bstr, "span class=\"pullleft\"", "img", "title=\"", "\"");
    kv["project_name"] = extract(bstr, "box-detail-tl", ">", "", "<");
    kv["project_id"] = idstr;
    kv["borrowing_amount"] = filternum(extract(bstr, "box-detail-tl", "<dl>", "<dd>", "元"));
    kv["annulized_rating"] = filternum(extract(bstr, "box-detail-tl", "元", ">", "%"));
    kv["payment_method"] = extract(bstr, "box-detail-tl", "class=\"box-infodt-li\"", "还款方式：", "<");
    string binfotmp = extracthtml(bstr, "class=\"box-detail-tl\"", "<dl>", "元", "<dd>");
    kv["award"] = extract(binfotmp, "box-detail-font", "box-detail-font", "box-detail-font\">", "</dd>");
    kv["loan_period"] = extract(binfotmp, "box-detail-font", "box-detail-font\">", "", "<p");
    if (kv["loan_period"].find("月") != string::npos) {
        kv["loan_period"] = longtostring(s_atod(kv["loan_period"].c_str()) * 30);
    }
    else {
        kv["loan_period"] = longtostring(s_atod(kv["loan_period"].c_str()));
    }
    double ramt = s_atod(extract(bstr, "发标时间", "剩余金额", "￥", "</div>").c_str());
    kv["invested_amount"] = doubletostring(s_atod(kv["borrowing_amount"].c_str()) - ramt);
    kv["release_time"] = longtostring(stringtotime(extract(bstr, "box-detail-tl", "还款方式", "发标时间：", "<").c_str(), "%Y-%m-%d %H:%M:%S"));
    long rtime = s_atol(extract(bstr, "剩余时间", "id=\"endtime\"", "data-time=\"", "\"").c_str());
    if (rtime > 0) {
        kv["end_time"] = longtostring(time(NULL) + rtime);
    }
    kv["project_details"] = extract(bstr, "id=\"jkxq\">", "", "", "<div class=\"list-tab-con");

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

