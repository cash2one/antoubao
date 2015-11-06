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
    kv["site_id"] = "qigehulu";
    kv["project_name"] = extract(bstr, "<div class=\"intro-l\">", "<h2", ">", "</h2");
    kv["project_id"] = idstr;
    kv["borrowing_amount"] = num_util(extract(bstr, "<div class=\"intro-l\">", "金额", "", "</li"));
    double invamt = s_atod(num_util(extract(bstr, "<div class=\"process-list\">", "实际已投金额", "", "</li>")).c_str());
    double ramt = s_atod(num_util(extract(bstr, "<div class=\"process-list\">", "剩余可投金额", "</li>", "</li>")).c_str());
    if (invamt > 0) {
        kv["invested_amount"] = doubletostring(invamt);
    }
    else {
        kv["invested_amount"] = doubletostring(s_atod(kv["borrowing_amount"].c_str()) - ramt);
    }
    kv["annulized_rating"] = extract(bstr, "<div class=\"intro-l\">", "年化收益", "","%");
    kv["payment_method"] = extract(bstr, "<ul class=\"financ-detail\">", "还款方式：", "", "<");
    kv["loan_period"] = loanperiod_util(extract(bstr, "<div class=\"intro-l\">", "项目期限", "", "</li"));
    kv["release_time"] = longtostring(stringtotime(extract(bstr, "<ul class=\"financ-detail\">", "项目发布日期：", "", "<").c_str(), "%Y-%m-%d"));
    long rt = s_atol(filternum(extract(bstr, "<div class=\"intro-foot-time\">", "剩余时间：", "", "</div>")).c_str());
    if (rt > 0) {
        kv["end_time"] = longtostring(time(NULL) + rt);
    }

    {
        string istr = extracthtml(bstr, "div class=\"invest-record", "投资记录", "</tr", "</table");
        string invstr;

        string invname;
        string invtime;
        string invacc;
        while ((invname = extract(istr, "<td", ">", "", "</td")) != "") {
            invacc = num_util(extract(istr, "<td", "<td", ">", "<td"));
            invtime = longtostring(stringtotime(extract(istr, "元", "<td", ">", "</td").c_str(), "%Y-%m-%d %H:%M:%S"));
            invstr += invtime + "|" +  invname + "|" + invacc + "|";

            string::size_type ep = istr.find("</tr");
            if (ep != string::npos) {
                istr = istr.substr(ep + 1);
            }
            else {
                break;
            }
        }
        kv["investor"] = invstr;
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

