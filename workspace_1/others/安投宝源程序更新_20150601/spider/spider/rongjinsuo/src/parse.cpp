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
    kv["site_id"] = "rongjinsuo";
    kv["project_name"] = extract(bstr, "<div id=\"view_con_m\">", "<div id=\"vcm_tit\">", "<h1>", "</h1>");
    kv["project_id"] = extract(bstr,"<div id=\"vcm_tit\">","年利率：","借款编号：","</p>");
    kv["annulized_rating"] = extract(bstr, "<div class=\"jianj2s\">", "借款", "利率：", "%");
    kv["payment_method"] = extract(bstr, "借款编号", "借款期限", "还款方式：", "<a href=");
    kv["loan_period"] = loanperiod_util(extract(bstr, "年利率","借款编号","借款期限：","</p>"));
    kv["borrowing_amount"] = num_util(extract(bstr, "<li class=\"redTime\">", "借款金额","\">","</samp>"));
    kv["invested_amount"] = doubletostring(s_atod(kv["borrowing_amount"].c_str()) - s_atod(num_util(extract(bstr,"已投资","剩余:","￥","元)")).c_str()));
    //kv["minimum_investment"] = extract(bstr,"还款方式","借款用途","最小投标金额：","元");
    //kv["maximum_investment"] = extract(bstr,"借款用途","最小投标金额：","最大投标金额：","</p>");
    kv["release_time"] = longtostring(stringtotime(extract(bstr,"<p><span class=\"org_b\"","发标时间","<strong>","</strong>").c_str(), "%Y-%m-%d %H:%M"));
    kv["project_details"] = extract(bstr,"<div id=\"v_lowb2_tit\"","借款详情","<p><br>","</p>");
    kv["borrower"] = extract(bstr, "借款人信息", "/></a></p>", "html\">", "</a></p>");

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
            string tmp = stringtojson(string(p, len))["html"].asString();
            p += len;

            tmp = extracthtml(tmp, "投标时间", "<tr>", "", "</table>");

            string ivname;
            string ivaccount;
            string ivtime;
            while ((ivname = extract(tmp, "href=", "viewuser", "html\">", "<")) != "") {
                ivaccount = num_util(extract(tmp, "href=", "</td", "</td>","元"));
                ivtime = extract(tmp, "元<", "<td", ">", "</td>");
                ivtime = longtostring(stringtotime(ivtime.c_str(), "%Y-%m-%d %H:%M"));
                retstr += ivtime + "|" + ivname + "|" + ivaccount + "|";
                string::size_type pos = tmp.find("<tr");
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

    if (kv["project_id"] == "" || s_atod(kv["borrowing_amount"].c_str()) <= 0) {
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
