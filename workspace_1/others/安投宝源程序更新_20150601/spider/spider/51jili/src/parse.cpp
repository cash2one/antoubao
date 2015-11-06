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
    kv["site_id"] = "51jili";
    kv["borrower"] = "";
    kv["credit_rating"] = "";
    kv["project_name"] = extract(bstr, "class=\"wrap mg_bt-10\"", "class=\"bb pd-15\"", ">", "</h4>");
    kv["project_id"] = idstr;
    kv["borrowing_amount"] = filternum(extract(bstr, "class=\"detailBase\"", "借款金额", "class=\"fs-30\">", "</em>"));
    kv["annulized_rating"] = filternum(extract(bstr, "class=\"detailBase\"", "年化利率", "class=\"fs-30\">", "</em>"));
    kv["payment_method"] = extract(bstr, "class=\"detailBase\"", "class=\"pd_20-0\"", "还款方式：", "</span>");
    kv["award"] = "";
    kv["loan_period"] = extract(bstr, "class=\"detailBase\"", "借款期限", "class=\"fs-30\">", "</dd>");
    if (kv["loan_period"].find("月") != string::npos) {
        kv["loan_period"] = longtostring(s_atod(kv["loan_period"].c_str()) * 30);
    }
    else {
        kv["loan_period"] = longtostring(s_atod(kv["loan_period"].c_str()));
    }

    int percent = s_atod(extract(bstr, "class=\"detailBase\"", "class=\"progress dp-ibl va-m\"", "<span>", "</span>").c_str());
    kv["invested_amount"] = longtostring(s_atod(kv["borrowing_amount"].c_str()) * percent / 100);
    kv["release_time"] = "";
    kv["end_time"] = "";
    kv["project_details"] = extract(bstr, "class=\"detailContent\"", "id=\"floatNav_1\"", "<p>", "</p>");
    if ( kv["project_details"].size() == 0 )
    {
        kv["project_details"] = extract(bstr, "项目描述</h4>", "</h5>", "<p>", "</p>");
    }

    string invstr;
    int invnum = 0;

    string tmps = extracthtml(bstr, "id=\"TvRecord\"", "class=\"investRecord\"", "<tbody>", "</tbody>");

    string flag("<tr style=\"height:60px; overflow: hidden\">");
    size_t beg, end;
    beg = tmps.find(flag);

    while ( beg != string::npos )
    {  
        end = tmps.find(flag, beg+flag.size());

        string s;
        if (end != string::npos)
        {   
            s = tmps.substr(beg+flag.size(), end-beg);
        }   
        else
        {   
            s = tmps.substr(beg+flag.size());
        }   

        string uname = extract(s, "<p>20", "<td", ">", "</td>");
        string account = filternum(extract(s, "</td>", "</td>", "<td>", "</td>"));
        string addtime = extract(s, "<td>", "<p", ">", "</p>");

        invstr += longtostring(stringtotime(addtime.c_str(), "%Y-%m-%d %H:%M:%S")) + "|" + uname + "|" + account + "|";
        invnum++;

        beg = end;
    }

    kv["investor"] = invstr;
    kv["investors_volume"] = longtostring(invnum);

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

