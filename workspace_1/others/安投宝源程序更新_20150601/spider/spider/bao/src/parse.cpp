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
    kv["site_id"] = "bao";
    kv["borrower"] = extract(bstr, "<div class=\"personal-information\"", "用户名：", "", "</span>");
    kv["project_name"] = extract(bstr, "class=\"xiangqing\">", "class=\"title\">", "<p>", "</p>");
    kv["project_id"] = idstr ;
    kv["borrowing_amount"] = num_util(extract(bstr, "<div class=\"content\">", "预期年化收益率", "", "借款总额"));
    kv["annulized_rating"] = filternum(extract(bstr, "<div class=\"content\">", "", "", "预期年化收益率"));
    kv["payment_method"] = extract(bstr,  "<div class=\"content\">", "还款方式：", "", "</li>");
    kv["loan_period"] = loanperiod_util(extract(bstr, "<div class=\"content\">", "借款总额", "", "借款期限"));
    kv["invested_amount"] = doubletostring(s_atod(kv["borrowing_amount"].c_str()) - s_atod(filternum(extract(bstr,"class=\"right\">","融资余额：","","元")).c_str()));
    kv["project_details"] = extract(bstr, "class=\"p-i-content\"", "借款用途：", "<span>", "</div>");

    {   
        string retstr;
        string striv = extracthtml(bstr, "div class=\"huang_kuang content1\"", "投标人", "</tr>", "</table>");
        string ivname;
        string ivaccount;
        string ivtime;
        while ((ivname = extract(striv, "<td", "", ">", "</td>")) != "") {
            ivaccount = filternum(extract(striv, "</td", "</td", "￥", "</td>"));
            ivtime = extract(striv, "</td", "</td", "</td>", "</td>");
            ivtime = longtostring(stringtotime(ivtime.c_str(), "%Y-%m-%d %H:%M:%S"));
            retstr += ivtime + "|" + ivname + "|" + ivaccount + "|";
            if (striv.find("</tr>") == string::npos) {
                break;
            }
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

