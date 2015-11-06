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
    kv["site_id"] = "cnaidai";
  //  kv["borrower"] = "";
    kv["project_name"] = extract(bstr, "class=\"prodt-mid\" >", "class=\"mt\">", "","</p>");
    kv["project_id"] = idstr;
    kv["borrowing_amount"] = extract(bstr, "class=\"list\"","债权金额", "class=\"red list-num bold\">", "万");
    kv["borrowing_amount"] = doubletostring(atof(kv["borrowing_amount"].c_str())*10000.0);
    kv["annulized_rating"] = extract(bstr, "class=\"list\"", "预期年化收益", "class=\"red list-tlnum bold\">", "%");
    kv["payment_method"] = extract(bstr, "class=\"prodt-mid-foot\">", "<p>", "还款方式：", "</p>");
    kv["loan_period"] = loanperiod_util(extract(bstr, "class=\"list\">","期限","</p>","</p>"));
    kv["minimum_investment"] = extract(bstr, "class=\"right\">", "<p>", "投资起始资金：", "元");
    kv["release_time"] = longtostring(stringtotime(extract(bstr,"class=\"prodt-mid-foot\"","<p>","发标日期：","</p>").c_str(), "%Y-%m-%d"));
//    kv["project_details"] = extract(bstr, "<!--借款详情-->", "class=\"list-detail\">", "<p>", "<!--合作单位-->");

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

