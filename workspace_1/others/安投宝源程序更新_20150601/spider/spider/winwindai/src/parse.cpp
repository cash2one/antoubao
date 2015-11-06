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
    kv["site_id"] = "winwindai";
    kv["borrower"] = extract(bstr, "investDetial_bottom", "investBoxOne", "用户名：<strong>", "</strong>");
    kv["credit_rating"] = extract(bstr, "class=\"investBoxOne_l\"", "class=\"c_l_area_", ">", "</div>");
    kv["project_name"] = extract(bstr, "class=\"investDetial_tab\"", " <table width=\"100%\">", "font size=\"5\">", "</font>");
    kv["project_id"] = idstr;
    kv["borrowing_amount"] = filternum(extract(bstr, "class=\"investDetial_tab\"", "借款金额", "display:block\">￥", "</font>"));
    if( kv["borrowing_amount"].size() == 0 ) {
        kv["borrowing_amount"] = doubletostring(s_atod((extract(bstr, "investDetial_tab", "累计购买金额", "display:block\">￥", "</font>")).c_str()));
    }

    kv["annulized_rating"] = filternum(extract(bstr, "class=\"investDetial_tab\"", "年化利率", "display:block\">", "<font"));
    if ( kv["annulized_rating"].size() == 0) {
        kv["annulized_rating"] = filternum(extract(bstr, "class=\"investDetial_tab\"", "colspan=\"2\">年化收益率:", "color=\"#b40519\">", "<font"));
    }

    kv["loan_period"] = extract(bstr, "class=\"investDetial_tab\"", "借款期限", "display:block\">", "</font>");
    if ( kv["loan_period"].size() == 0 )
    {
        kv["loan_period"] = extract(bstr, "class=\"investDetial_tab\"", "赎回条件", "display:block\">", "</font>");
    }
    kv["loan_period"] = loanperiod_util(kv["loan_period"]);

    double ramt = s_atod(filternum(extract(bstr, "class=\"investDetial_tab\"", "剩余金额", "color=\"#b40519\">", "</font>")).c_str());
    kv["invested_amount"] = doubletostring(s_atod(kv["borrowing_amount"].c_str()) - ramt);
    long rtime = s_atol(extract(bstr, "<div id=\"remainSeconds\"", ">", "", "</div>").c_str());
    if (rtime > 0) {
        kv["end_time"] = longtostring(time(NULL) + rtime);
    }
    kv["project_details"] = extract(bstr, "class=\"investDetial_tab\"", "剩余金额", "/tr>", "</table>");
    if ( kv["project_details"].size() == 0 ) {
        kv["project_details"] = extract(bstr, "class=\"investDetial_tab\"", "产品描述</font", ">：", "</td>");
    }
    kv["minimum_investment"] = num_util(extract(bstr, "class=\"investDetial_rightTop\"", "投资现金", "</p>", "起投"));
    kv["maximum_investment"] = num_util(extract(bstr, "class=\"investDetial_rightTop\"", "投资现金", "起投，最高", "<"));

    sprintf(filename, "html/%s.brec", idstr);
    buf = readfile(filename);
    if (buf) {
        bstr = string(buf);
        free(buf);
    }
    else {
        bstr = "";
    }

    string invstr;

    string flag("<tr>\r\n<td align=\"center\">");
    size_t beg, end;
    beg = bstr.find(flag);

    while ( beg != string::npos )
    {  
        end = bstr.find(flag, beg+flag.size());

        string s;
        if (end != string::npos)
        {   
            s = bstr.substr(beg+flag.size(), end-beg);
        }   
        else
        {   
            s = bstr.substr(beg+flag.size());
        }   

        string uname = extract(s, "align=\"center\"", "class=\"name\"", ">\r\n", "<!");
        string account = extract(s, "align=\"center\"", "class=\"fred\">", "￥", "</td>");
        string addtime = extract(s, "￥", "align=\"center\"", ">", "</td>");

        invstr += longtostring(stringtotime(addtime.c_str(), "%Y-%m-%d %H:%M:%S")) + "|" + uname + "|" + account + "|";
        beg = end;
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

