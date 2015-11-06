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
    kv["site_id"] = "ehjinrong";
    kv["borrower"] = extract(bstr, "class=\"detail_top_dkyt\"", "借", "人：", "<br/>");
    //kv["credit_rating"] = "";
    kv["project_name"] = extract(bstr, "class=\"detail_title\"", "class=\"detail_title_l p20\"", ">", "</div>");
    kv["project_id"] = idstr;
    kv["borrowing_amount"] = doubletostring(s_atod(filternum(extract(bstr, "class=\"detail_top_xx\"", "贷款总额", "<span>", "</span>")).c_str()) * 10000);
    kv["annulized_rating"] = filternum(extract(bstr, "class=\"detail_top_xx\"", "年化收益", "class=\"red\">", "</span>"));
    kv["payment_method"] = extract(bstr, "class=\"detail_top_dkyt\"", "还款方式", "：", "</div>");
   // kv["award"] = "";
    kv["loan_period"] = extract(bstr, "class=\"detail_top_xx\"", "投资期限", "<span>", "</li>");
    if (kv["loan_period"].find("月") != string::npos) {
        kv["loan_period"] = longtostring(s_atod(kv["loan_period"].c_str()) * 30);
    }
    else {
        kv["loan_period"] = longtostring(s_atod(kv["loan_period"].c_str()));
    }

    kv["invested_amount"] = doubletostring(s_atod(kv["borrowing_amount"].c_str()) - s_atod(extract(bstr, "class=\"detail_top_jd\"", "已投", "class=\"p20\">", "</span>").c_str()));
    //kv["release_time"] = "";
    //kv["end_time"] = "";
    //kv["project_details"] = extract(bstr, "基本情况描述", "</strong>", "<p align=\"left\">", "</p>");

    string invstr;
    int invnum = 0;

    string tmps = extracthtml(bstr, "id=\"yw0_c0\"", "id=\"yw0_c4\"", "</thead>", "</tbody>");

    string flag("<tr class=\"odd\">");
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

        string uname = extract(s, "<td", "class=\"tab_2\"", ">", "</td>");
        string account = filternum(extract(s, "class=\"tab_2\"", "</td>", "<td>", "</td>"));
        string addtime = extract(s, "class=\"tab_2\"", "</td><td>", "</td><td>", "</td>");

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

