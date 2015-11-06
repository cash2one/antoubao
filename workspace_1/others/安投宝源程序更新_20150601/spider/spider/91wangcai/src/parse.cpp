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
    kv["site_id"] = "91wangcai";
    kv["borrower"] = extract(bstr, "还款方式", "借&nbsp;款&nbsp;人", "<td>","</td>");
    kv["project_name"] = extract(bstr,"<div class=\"wrap\">","<div class=\"lbox\">","<div class=\"shd\">","</div>");
    kv["project_id"] = idstr;
    kv["borrowing_amount"] = num_util(extract(bstr, "投资期限", "<li class=\"end\">","<em>","</em>"));
    kv["annulized_rating"] = filternum(extract(bstr, "<div class=\"wrap\">", "<em class=\"c1\">","\">", "</b>%"));
    kv["payment_method"] = extract(bstr,"投资总额","<div class=\"","还款方式：","</span>");
    kv["loan_period"] = loanperiod_util(extract(bstr, "年化利率", "<li class=\"con\">", "\">","</em>"));
    kv["invested_amount"] = doubletostring(s_atod(kv["borrowing_amount"].c_str()) - s_atod(num_util(extract(bstr,"<div class=\"per\">","可投金额","<em>","</em><small>")).c_str()));
    kv["project_details"] = extract(bstr,"<div class=\"tabMain\">","<div class=\"tabBd\">","项目概况","</table>");
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

            string::size_type spos = tmp.find("</tr>");
            string::size_type epos = tmp.find("<div class=\"pageBox\">");
            if (spos == string::npos || epos == string::npos) {
                continue;
            }
            tmp = tmp.substr(spos + 1, epos - spos - 1);
            string ivname;
            string ivaccount;
            string ivtime;
            while ((ivname = extract(tmp, "<tr>", "<td>", "", "</td>")) != "") {
                ivaccount = extract(tmp, "<td>", "</td>", "<td>","&nbsp;元");
                ivtime = extract(tmp, "</td>", "&nbsp;元", "<td>", "</td>");
                ivtime = longtostring(stringtotime(ivtime.c_str(), "%Y-%m-%d %H:%M")
                        );
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

    if (kv["project_id"] == "" ) {
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
