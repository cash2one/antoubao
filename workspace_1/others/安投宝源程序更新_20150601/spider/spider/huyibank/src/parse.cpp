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
    kv["site_id"] = "huyibank";
    kv["borrower"] = extract(bstr, "div id=\"container\"", "用户名:", "", "<");
    kv["credit_rating"] = extract(bstr, "span class=\"pullleft\"", "img", "title=\"", "\"");
    kv["project_name"] = extract(bstr, "box-info-detail-title", ">", "", "<");
    kv["project_id"] = extract(bstr, "box-info-detail", "a", "借款编号#", "</span>");
    kv["borrowing_amount"] = num_util(extract(bstr, "box-info-detail", "id=\"borrowAccount\"", "value=\"", "\""));
    kv["annulized_rating"] = num_util(extract(bstr, "borrowAccount", "年利率：", "", "%"));
    kv["payment_method"] = extract(bstr, "borrowAccount", "v", "还款方式：", "<li");
    kv["award"] = extract(bstr, "borrowAccount", "还款方式", "投资奖励：", "</li>");
    kv["loan_period"] = loanperiod_util(extract(bstr, "borrowAccount", "还款方式", "借款期限：", "<"));
    long rt = s_atol(filternum(extract(bstr, "剩余时间", "span id=\"endtime\"", "data-time=\"", "\"")).c_str());
    if (rt != 0) {
        kv["end_time"] = longtostring(time(NULL) + rt);
    }
    kv["release_time"] = longtostring(stringtotime(extract(bstr, "borrowAccount", "审时间", "：", "</li>").c_str(), "%Y-%m-%d %H:%M:%S"));
    kv["invested_amount"] = doubletostring(s_atod(kv["borrowing_amount"].c_str()) - s_atod(num_util(extract(bstr, "box-info-detail", "剩余金额:￥", "", "元")).c_str()));

    sprintf(filename, "html/%s.brec", idstr);
    buf = readfile(filename);
    string invstr;
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
            }
        }
        free(buf);
    }
    kv["investor"] = invstr;

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

