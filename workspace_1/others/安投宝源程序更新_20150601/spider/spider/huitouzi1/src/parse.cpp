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

    kv["site_id"] = "huitouzi";
//    kv["borrower"] = "";
    kv["project_name"] = extract(bstr, "class=\"breadcrumb\">", "首页", "class=\"active\">", "</li>");
    kv["project_id"] = idstr;
    kv["borrowing_amount"] = num_util(extract(bstr, "class=\"binfo-tab\">","项目规模","<td>","</td>"));
    kv["annulized_rating"] = extract(bstr, "class=\"binfo-tab\">", "</td>", "</td>", "%");
    kv["payment_method"] = extract(bstr, "class=\"info-tab\">", "收益方式：", "<td>", "</td>");
    kv["loan_period"] = loanperiod_util(extract(bstr, "class=\"binfo-tab\">","项目期限", "</td>", "</td>"));
//    kv["release_time"] = "";    


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
            if (!has_array_member(json, "data")){
                continue;
            }
            for (int i = 0; i < json["data"].size(); i++) {
                string account;
                string addtime;
                string username;
                if (!get_string_member(json["data"][i], "tender_money", account)
                        || !get_string_member(json["data"][i], "create_time", addtime)
                        || !get_string_member(json["data"][i], "showname", username)) {
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

