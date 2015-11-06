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
    kv["site_id"] = "htctou";
    kv["borrower"] = extract(bstr, "<div class=\"state_project\">", "借款用户", ":", "<");
    kv["credit_rating"] = extract(bstr, "<div class=\"state_project\">", "<img src=", "title=\"", "\"");
    kv["project_name"] = extract(bstr, "<div class=\"state_project\">", "借款用户", ">", "<div");
    kv["project_id"] = idstr;
    kv["borrowing_amount"] = num_util(extract(bstr, "<div class=\"state_project\">", "借款金额", "￥", "元"));
    kv["annulized_rating"] = extract(bstr, "<div class=\"state_project\">", "借款金额", "元", "%/");
    kv["payment_method"] = extract(bstr, "<div class=\"state_project\">", "还款方式：", "", "</");
    kv["award"] = extract(bstr, "<div class=\"state_project\">", "投标奖励：", "", "</");
    kv["loan_period"] = loanperiod_util(extract(bstr, "<div class=\"state_project\">", "借款金额", "%/", "</li"));
    kv["release_time"] = longtostring(stringtotime(extract(bstr, "<div class=\"state_project\">", "发布时间", ":", "<").c_str(), "%Y-%m-%d %H:%M"));
    long rt = s_atol(extract(bstr, "input id=\"hid\"", "value=\"", "", "\"").c_str());
    if (rt != 0) {
        kv["end_time"] = longtostring(time(NULL) + rt);
    }

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
            string ivname;
            string ivtime;
            string ivacc;
            while ((ivname = extract(jstr, "<td", "txtC'>", "", "</td")) != "") {
                ivacc = num_util(extract(jstr, "<td", "￥", "", "元"));
                ivtime = longtostring(stringtotime(extract(jstr, "<td", "￥", "元</td>", "</td").c_str(), "%Y-%m-%d %H:%M"));
                invstr += ivtime + "|" + ivname + "|" + ivacc + "|";
                string::size_type spos = jstr.find("</tr");
                if (spos == string::npos) {
                    break;
                }
                jstr = jstr.substr(spos+1);
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

