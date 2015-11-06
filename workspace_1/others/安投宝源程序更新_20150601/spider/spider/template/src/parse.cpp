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
    kv["site_id"] = "zhaoshangdai";
    kv["borrower"] = extract(bstr, "div class=\"box-info-user ", "center;\">", "\">", "</a>");
    kv["credit_rating"] = extract(bstr, "span class=\"pullleft\"", "img", "title=\"", "\"");
    kv["project_name"] = extract(bstr, "box-info-detail", "h2", "color:#000;\">", "</span>");
    kv["project_id"] = extract(bstr, "box-info-detail", "a", "借款编号#", "</span>");
    kv["borrowing_amount"] = extract(bstr, "box-info-detail", "id=\"borrowAccount\"", "value=\"", "\"");
    kv["borrowing_amount"] = doubletostring(atof(kv["borrowing_amount"].c_str())/10000.0);
    kv["annulized_rating"] = extract(bstr, "borrowAccount", "年利率", "<strong>", "%");
    kv["payment_method"] = extract(bstr, "borrowAccount", "v", "还款方式：", "</li>");
    kv["award"] = extract(bstr, "borrowAccount", "还款方式", "投资奖励：", "</li>");
    kv["loan_period"] = extract(bstr, "borrowAccount", "还款方式", "借款期限：", "月");
    kv["rate_of_progress"] = extract(bstr, "borrowAccount", "完成", "inline;\">", "%");
    kv["remanent_amount"] = extract(bstr, "borrowAccount", "完成", "剩余金额:￥", "元");
    kv["minimum_investment"] = extract(bstr, "borrowAccount", "还款方式", "最小投标额：", "</li>");
    kv["maximum_investment"] = extract(bstr, "borrowAccount", "还款方式", "最大投标额：", "</li>");
    kv["remanent_time"] = extract(bstr, "borrowAccount", "剩余时间", "data-time=\"", "\"");
    kv["release_time"] = extract(bstr, "borrowAccount", "审时间", "：", "</li>");
    kv["project_details"] = extract(bstr, "id=\"jkxq\"", ";", "<div>", "还款保障：");

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

