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
    string tmps;
    free(buf);
    map <string, string> kv;
    kv["site_id"] = "esudai";
    kv["project_name"] = extract(bstr, "span class=\"content_div_item_tit", ">", "", "<span");
    kv["borrower"] = extract(bstr, "span class=\"content_div_item_tit", "<span", ">", "</span");
    kv["project_id"] = idstr;
    kv["borrowing_amount"] = num_util(extract(bstr, "span class=\"content_div_item_tit", "标总额", "￥", "<"));
    kv["annulized_rating"] = num_util(extract(bstr, "span class=\"content_div_item_tit", "年利率", "/div>", "</div"));
    kv["payment_method"] = extract(bstr, "span class=\"content_div_item_tit", "class=\"item_detail padbottom10\"", "还款方式：", "<");
    kv["loan_period"] = loanperiod_util(extract(bstr, "span class=\"content_div_item_tit", "还款期限", ">", "</div>"));

    kv["minimum_investment"] = extract(bstr, "class=\"item_detail padbottom", "最低可投：", "", "<");
    kv["maximum_investment"] = extract(bstr, "class=\"item_detail padbottom", "最高可投：", "", "<");
    kv["release_time"] = longtostring(stringtotime(extract(bstr, "class=\"item_detail padbottom", "发标时间：", "", "<").c_str(), "%Y-%m-%d %H:%M:%S"));
    long rtime = s_atol(filternum(extract(bstr, "class=\"rightnav_close\"", "var iTime =", "iTime = '", "'")).c_str());
    if (rtime > 0) {
        kv["end_time"] = longtostring(time(NULL) + rtime);
    }
    kv["invested_amount"] = doubletostring(s_atod(kv["borrowing_amount"].c_str()) -
        s_atod(filternum(extract(bstr, "<span class=\"item_restmoney", "剩余金额", "￥", "<")).c_str()));
    kv["project_details"] = "";


    string invstr;

    bstr = extracthtml(bstr, "<div class=\"list_item_table", "投标人", "</li>", "</ul>");
    string::size_type beg = bstr.find("<li");

    while (beg != string::npos)
    {
        bstr = bstr.substr(beg);

        string uname = extract(bstr, "</span>", "", "", "</span>");
        string account = extract(bstr, "</span>", "%</", "</span>", "</span>");
        string addtime = extract(bstr, "%</", "</span>", "</span>", "</span>");

        invstr += longtostring(stringtotime(addtime.c_str(), "%Y-%m-%d %H:%M:%S")) + "|" + uname + "|" + account + "|";

        beg = bstr.find("<li", 1);
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

