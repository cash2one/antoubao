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
    kv["site_id"] = "";
    kv["borrower"] = "";
    kv["credit_rating"] = "";
    kv["project_name"] = extract(bstr, "class=\"investContainer\"", "</a>", "<h3>", "</h3>");
    kv["project_id"] = idstr;
    kv["borrowing_amount"] = filternum(extract(bstr, "class=\"investContainer\"", "借款金额", "class=\"red\">", "</span>"));
    kv["annulized_rating"] = filternum(extract(bstr, "class=\"investContainer\"", "年化收益", "class=\"red\">", "</span>"));
    kv["payment_method"] = extract(bstr, "class=\"investContainer\"", "还款方式", "lass=\"con\">", "</div>");
    kv["award"] = "";
    kv["loan_period"] = extract(bstr, "class=\"investContainer\"", "借款期限", "class=\"con\">", "</div>");
    if (kv["loan_period"].find("月") != string::npos) {
        kv["loan_period"] = longtostring(s_atod(filternum(kv["loan_period"]).c_str()) * 30);
    }
    else {
        kv["loan_period"] = filternum(kv["loan_period"]);
    }

    kv["invested_amount"] = filternum(extract(bstr, "class=\"tb_list\"", "目前投资总额", "<span>", "</span>"));
    kv["release_time"] = "";
    kv["end_time"] = "";
    kv["project_details"] = "";

    string invstr;
    int invnum = 0;

    string tmps = extracthtml(bstr, "class=\"tb_list\"", "<thead>", "<tbody>", "</tbody>");

    string flag("<tr>");
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

        string uname = extract(s, "<td", "class=\"it3\"", ">", "</td>");
        string account = filternum(extract(s, "<td", "class=\"it2\"", ">", "</td>"));
        string addtime = extract(s, "<td", "class=\"it1\"", ">", "</td>");

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

