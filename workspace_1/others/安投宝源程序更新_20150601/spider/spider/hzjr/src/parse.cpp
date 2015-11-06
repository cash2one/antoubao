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
    kv["site_id"] = "hzjr";
    string brr = extract(bstr, "<tbody>", "用户ID", "<td>","</td>");
    if (brr != "") {
        kv["borrower"] = brr;
    }
    kv["project_name"] = extract(bstr,"<div id=\"main\"","class=\"inv-head", "<li class=\"clearfix\">", "</span");
    kv["project_id"] = idstr;
    kv["borrowing_amount"] = num_util(extract(bstr, "<div id=\"main\"", "金额：","￥", "</span"));
    kv["annulized_rating"] = filternum(extract(bstr,"金额", "预期年化收益：", "", "%"));
    kv["payment_method"] = extract(bstr,"<div id=\"main\"","还款方式", "：","<span");
    kv["loan_period"] = loanperiod_util(extract(bstr, "<div id=\"main\"", "期限", "：","</span"));
    double rm = s_atod(num_util(extract(bstr, "<div id=\"main\"", "<div class=\"ketou\">", "", "</div")).c_str());
    kv["invested_amount"] = doubletostring(s_atod(kv["borrowing_amount"].c_str()) - rm);
    kv["release_time"] = longtostring(stringtotime(extract(bstr,"还款方式","发布时间","<em>","</em></span></li>").c_str(), "%Y-%m-%d"));
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

            string::size_type spos = tmp.find("投标时间");
            string::size_type epos = tmp.find("<div id=\"pages\">");
            if (spos == string::npos || epos == string::npos) {
                continue;
            }
            tmp = tmp.substr(spos + 1, epos - spos - 1);
            string ivname;
            string ivaccount;
            string ivtime;
            while ((ivname = extract(tmp, "<input type=", "value=\"", "<td>", "</td>")) != "") {
                ivaccount = num_util(extract(tmp, "value=", "￥", "￥","</td>"));
                ivtime = extract(tmp, "￥", "￥", "<td>", "</td>");
                ivtime = longtostring(stringtotime(ivtime.c_str(), "%Y-%m-%d %H:%M"));
                retstr += ivtime + "|" + ivname + "|" + ivaccount + "|";
                string::size_type pos = tmp.find("<input type=\"hidden\"");
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
