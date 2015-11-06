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

    kv["site_id"] = "longdai";
//  kv["borrower"] = "";
    kv["project_name"] = extract(bstr, "class=\"main-detail-wrap\">", "main-detail-info-title-con clearfloat", "class=\"f-l main-detail-info-title\">", "<div");
    kv["project_id"] = idstr;
    kv["borrowing_amount"] = num_util(extract(bstr, "class=\"main-detail-wrap1\">", "发售金额（元）", "class=\"info-about-value\">", "</p>"));
    kv["annulized_rating"] = extract(bstr, "class=\"main-detail-wrap1\">", "预期年化", "class=\"info-about-value\">", "%");
    kv["payment_method"] = extract(bstr, "class=\"main-detail-wrap1\">", "保障方式", "class=\"info-about-value\">", "</");
    kv["loan_period"] = loanperiod_util(extract(bstr, "class=\"main-detail-wrap1\">", "期限（", "class=\"info-about-value\">", "<"));
//  kv["release_time"] = longtostring(stringtotime(extract(bstr,"class=\"progress-con-bottom clearfloat top_25\">","龙聚宝发售","<div>","</div>").c_str(), "%Y.%m.%d %H:%M:%S"));

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
                    || !has_object_member(json["data"], "pageBean")
                    || !has_array_member(json["data"]["pageBean"],"page")) {
                continue;
            }
            for (int i = 0; i < json["data"]["pageBean"]["page"].size(); i++) {
                double account;
                double addtime;
                string username;
                if (!get_double_member(json["data"]["pageBean"]["page"][i], "investAmount", account)
                        || !get_double_member(json["data"]["pageBean"]["page"][i], "joinTime", addtime)
                        || !get_string_member(json["data"]["pageBean"]["page"][i], "username", username)) {
                    continue;
                }
                invstr += longtostring(addtime/1000) + "|" + username + "|" + doubletostring(account) + "|";
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

