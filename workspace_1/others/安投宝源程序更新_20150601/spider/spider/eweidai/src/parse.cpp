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
    
    kv["site_id"] = "eweidai";
    kv["borrower"] = extract(bstr, "class=\"items\">", "姓名", "class=\"val\">", "</span>");
    kv["project_name"] = extract(bstr, "class=\"model-box\">", "class=\"head\"", "<h2>", "</h2>");
    kv["project_id"] = idstr;
    kv["borrowing_amount"] = extract(bstr, "class=\"profit\">", "借款金额", "￥", "</dd>");
    kv["annulized_rating"] = extract(bstr, "class=\"dl_left\">", "年化利率", "<dd>", "%");
    kv["payment_method"] = extract(bstr, "class=\"marl20\">", "<span>", "", "：");
    kv["loan_period"] = loanperiod_util(extract(bstr, "class=\"dl_right\">", "还款期限", "id=\"lblPeriod\">", "</span>"));
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
            string jstr = (len>=6?string(p+5, len-6):"");
            p += len;
            Value json = stringtojson(jstr);
            if (!has_array_member(json, "desc")) {
                continue;
            }
            for (int i = 0; i < json["desc"].size(); i++) {
                double account;
                string addtime;
                string username;
                if (!get_double_member(json["desc"][i], "investMoney", account)
                        || !get_string_member(json["desc"][i], "investTime", addtime)
                        || !get_string_member(json["desc"][i], "investorShowName", username)) {
                    continue;
                }
                addtime = longtostring(stringtotime(addtime.c_str(), "%Y-%m-%d %H:%M:%S"));
                invstr += addtime + "|" + username + "|" + doubletostring(account) + "|";
                invnum++;
            }
        }
        free(buf);
    }
    kv["investor"] = invstr;
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

    
    
