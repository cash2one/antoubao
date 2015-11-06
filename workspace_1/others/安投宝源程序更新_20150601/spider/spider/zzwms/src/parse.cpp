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
    kv["site_id"] = "zzwms";
    kv["borrower"] = extract(bstr, "class=\"xmjs2\">", "<span>", "用户名：", "</span>");
    kv["project_name"] = extract(bstr, "class=\"ysd_tzxm\">", "class=\"ysd_tzxm_t\">", ">", "</span>");
    kv["project_id"] = idstr ;
    kv["borrowing_amount"] =num_util( extract(bstr, "class=\"tzxm_m1\">", "class=\"tzxm_5\">", "￥", "</span>"));
    kv["annulized_rating"] =filternum( extract(bstr, "class=\"tzxm_m1\">", "align=\"center\">", "class=\"tzxm_1\">", "%"));
    kv["payment_method"] = extract(bstr,  "class=\"tzxm_m1\">", "借款总额", "class=\"tzxm_5\">", "</span>");
    kv["loan_period"] = loanperiod_util(extract(bstr, "class=\"tzxm_m1\">", "%", "class=\"tzxm_1\">", "</td>"));
    kv["release_time"] ="";    
    {   
        string striv = extracthtml(bstr, "div id=\"tzxm4\"", "</tr>", "</tr>", "<div id=\"tzxm5\"");
        string retstr;
        string ivname;
        string ivaccount;
        string ivtime;
        while ((ivname = extract(striv, "</td>", "</td>", "", "</td>")) != "") {
            ivaccount = filternum(extract(striv, "&nbsp", "&nbsp", "￥", "元"));
            ivtime = extract(striv, "￥", "&nbsp", "</td>", "</td>");
            ivtime = longtostring(stringtotime(ivtime.c_str(), "%Y-%m-%d %H:%M:%S"));
            retstr += ivtime + "|" + ivname + "|" + ivaccount + "|";
            if (striv.find("</tr>") == string::npos) {
                break;
            }
            striv = striv.substr(striv.find("</tr>") + 1);
            striv = striv.substr(striv.find("</tr>") + 1);

        }
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

