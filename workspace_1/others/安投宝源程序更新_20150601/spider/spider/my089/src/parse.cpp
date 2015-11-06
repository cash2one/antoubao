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
    kv["site_id"] = "my089";
    kv["borrower"] = extract(bstr, "class=\"Bid_lf lf\"", "<span", "名：", "</dd>");
    kv["project_name"] = extract(bstr, "<div class=\"Bid_rt", "<span class=\"bt_txt\"", ">", "</span>");
    kv["project_id"] = idstr;
    kv["borrowing_amount"] = filternum(extract(bstr, "<div class=\"biao_info\">", "<li class=\"jine\">", "借款金额", "</li>"));
    kv["annulized_rating"] = extract(bstr, "<div class=\"biao_info\">", "利率", ">", "%");
    kv["payment_method"] = extract(bstr, "<div class=\"biao_info\">", "还款方式：", "", "</li>");
    kv["loan_period"] = extract(bstr, "<div class=\"biao_info\">", "借款期限：", "", "</li>");
    if (kv["loan_period"].find("月") != string::npos) {
        kv["loan_period"] = doubletostring(s_atod(filternum(kv["loan_period"]).c_str())*30);
    }
    else {
        kv["loan_period"] = doubletostring(s_atod(filternum(kv["loan_period"]).c_str()));
    }
    kv["invested_amount"] = doubletostring(s_atod(kv["borrowing_amount"].c_str())
            - s_atod(filternum(extract(bstr, "<div class=\"biao_info\">", "class=\"time\"", "还需", "元")).c_str()));
    kv["minimum_investment"] = filternum(extract(bstr, "<div class=\"biao_info\">", "可投范围", "￥", " "));
    kv["maximum_investment"] = filternum(extract(bstr, "<div class=\"biao_info\">", "可投范围", "~", "<"));
    string ettmp = extract(bstr, "<div class=\"biao_info\">", "class=\"time\"", "剩余时间：", "<");
    {
        int d, h, m, s;
        if (sscanf(ettmp.c_str(), "%d天%d时%d分%d秒", &d, &h, &m, &s) == 4) {
            kv["end_time"] = longtostring(time(NULL)+ d*86400+h*3600+m*60+s);
        }
    }
    kv["project_details"] = extract(bstr, "class=\"TabbedPanelsContentGroup\"", "<!--借款详情-->", "", "<!--投标记录-->");

    sprintf(filename, "html/%s.brec", idstr);
    buf = readfile(filename);
    string invstr = "";
    int invnum = 0;
    if (buf) {
        bstr = string(buf);
        free(buf);
        string::size_type tpos = bstr.find("<tr");
        if (tpos != string::npos) {
            tpos = bstr.find("<tr", tpos + 1);
        }
        while (tpos != string::npos) {
            bstr = bstr.substr(tpos + 1);
            string ivtime;
            string ivname;
            string ivaccount;
            ivtime = longtostring(stringtotime(extract(bstr, "￥", "￥", "<td>", "</td>").c_str(), "%Y-%m-%d %H:%M:%S"));
            ivname = extract(bstr, "<td>", "<td>", "", "</td>");
            ivaccount = filternum(extract(bstr, "￥", "￥", "", "<"));
            if (ivname == "") {
                break;
            }
            invstr += ivtime + "|" + ivname + "|" + ivaccount + "|";
            tpos = bstr.find("<tr");
        }
    }
    kv["investor"] = invstr;

    printstringmap(kv);

    if (s_atol(kv["borrowing_amount"].c_str()) <= 0) {
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

