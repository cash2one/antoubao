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
    kv["site_id"] = "rozo360";
    kv["borrower"] = extract(bstr, "invest_details_person", "用户名称：", "", "</dd>");
    kv["project_name"] = extract(bstr, "invest_details_content_wrap_border", "class=\"bid_number\">", "</span>", "剩余金额:");
    kv["project_id"] = idstr;
    kv["borrowing_amount"] = extract(bstr, "class=\"pop-tb-l\">", "借款金额：", "￥", "元");
    kv["annulized_rating"] = extract(bstr, "class=\"pop-tb-l\">", "借款年利率:", "", "%");
    kv["payment_method"] = extract(bstr, "class=\"pop-tb-l\">", "还款方式:", "-->", "-->");
    kv["loan_period"] = loanperiod_util(extract(bstr, "class=\"pop-tb-l\">", "<li>", "借款期限:", "</li>"));
    kv["release_time"] = longtostring(stringtotime(extract(bstr, "invest_details_content_intro", "时间：", "<span>", "</span>").c_str(), "%Y-%m-%d %H:%M:%S"));

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
                if (!has_string_member(json["data"]["list"][i], "account")
                        || !has_string_member(json["data"]["list"][i], "addtime")
                        || !has_string_member(json["data"]["list"][i], "username")) {
                    continue;
                }
                invstr += json["data"]["list"][i]["addtime"].asString() + "|"
                    + json["data"]["list"][i]["username"].asString() + "|"
                    + json["data"]["list"][i]["account"].asString() + "|";
            }
        }
        free(buf);
    }
    kv["investor"] = invstr;

    printstringmap(kv);
    if (kv["project_id"] == "" || kv["release_time"] == "" || kv["borrower"] == "") {
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

