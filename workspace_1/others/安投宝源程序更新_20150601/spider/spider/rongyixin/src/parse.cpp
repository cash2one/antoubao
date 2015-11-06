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
    kv["site_id"] = "rongyixin";
    kv["borrower"] = "";
    kv["project_name"] = extract(bstr, "class=\"w1100 wbor\">", "class=\"arl_title\">", "<h2>", "</h2>");
    kv["project_id"] = idstr;
    kv["borrowing_amount"] = num_util(extract(bstr, "class=\"w1100 wbor\">", "借款金额", "<span>", "元"));
    kv["annulized_rating"] = extract(bstr, "class=\"w1100 wbor\">", "年利率", "class=\"red\">", "</span>");
    kv["payment_method"] = extract(bstr, "class=\"arl_row\">", "还款方式：", "<em>", "</em>");
    kv["loan_period"] = loanperiod_util(extract(bstr, "class=\"w1100 wbor\">", "借款期限", "<span>", "</span>"));
    kv["release_time"] = longtostring(stringtotime(extract(bstr, "class=\"w1100 wbor\">", "借款时间：", "<em>", "</em>").c_str(),"%Y-%m-%d %H:%M"));

    string invstr;
    {
        sprintf(filename, "html/%s.brec", idstr);
        buf = readfile(filename);
        size_t buflen = strlen(buf);
        char *p = buf;
        string retstr;
        while (p < buf + buflen - 8) {
            int len;
            sscanf(p, "%08X", &len);
            p += 8;
            string tmp = string(p, len);
            p += len;

            string::size_type spos = tmp.find("<tr>");
            if (spos == string::npos) {
                continue;
            }
           // tmp = tmp.substr(spos + 1, epos - spos - 1);
            string ivname;
            string ivaccount;
            string ivtime;
            while ((ivname = extract(tmp, "<td>", "", "", "</td>")) != "") {
                ivaccount = extract(tmp, "<td>", "<td>", "￥","元");
                ivtime = extract(tmp, "<td>", "￥", "<td>", "</td>");
                ivtime = longtostring(stringtotime(ivtime.c_str(), "%Y-%m-%d %H:%M"));
                retstr += ivtime + "|" + ivname + "|" + ivaccount + "|";
                string::size_type pos = tmp.find("</tr>");
                if (pos != string::npos) {
                    tmp = tmp.substr(pos + 1);
                }
                else {
                   break;
            }
        }
        }
        free(buf);
        kv["investor"] = retstr;
    }
     
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

