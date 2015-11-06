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

    int type = 0;  // 1:dpb 2:zj
    string bstr = string(buf);
    free(buf);
    map <string, string> kv;
    kv["site_id"] = "frbao";
    kv["project_id"] = idstr;
    kv["borrower"] = "";
    kv["project_name"] = extract(bstr, "class=\"dhb_mid\"", "class=\"bianhao_main\"", "class=\"right\">", "</td>");
    if ( kv["project_name"].size() != 0 )
    {
        type = 1;
    }
    else
    {
        kv["project_name"] = extract(bstr, "class=\"program\"", "style=\"padding-bottom:", "<h2>", "<span class=\"sp3\">");
        if ( kv["project_name"].size() != 0 )
        {
            type = 2;
        }
    }

    switch(type)
    {
        case 1:
            kv["borrowing_amount"] = num_util(extract(bstr, "class=\"dhb_mid\"", "融资总额", "class=\"right\">", "</td>"));
            kv["loan_period"] = loanperiod_util(extract(bstr, "class=\"dhb_mid\"", "投资期限", "class=\"right\">", "</td>"));
            kv["release_time"] = longtostring(stringtotime(extract(bstr, "class=\"dhb_mid\"", "class=\"bianhao_title\"", "发布时间：", "</em>").c_str(), "%Y-%m-%d"));
            kv["payment_method"] = extract(bstr, "class=\"dhb_mid\"", "收益方式", "class=\"right\"><p>", "</td>");
            break;
        case 2:
            kv["borrowing_amount"] = num_util(extract(bstr, "class=\"xiang3\"", "融资总额", "<td>", "</td>"));
            kv["loan_period"] = loanperiod_util(extract(bstr, "class=\"xiang3\"", "投资期限", "<span>", "</span>"));
            kv["release_time"] = longtostring(stringtotime(extract(bstr, "class=\"program\"", "class=\"sp2\">", "发布时间：", "</span>").c_str(), "%Y-%m-%d"));
            kv["payment_method"] = extract(bstr, "class=\"xiang3\"", "收益方式", "<td>", "</td>");
            break;
        default:
            return 1;
    }

    string invstr;
    int invnum = 0;

    string tmps = extracthtml(bstr, "class=\"hjmd_title\"", "<colgroup>", "</tr>", "</table>");

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

        string uname = "";
        switch(type)
        {
            case 1:
                uname = extract(s, "<td>", "cutstr", "('", "')");
                break;
            case 2:
                uname = extract(s, "<", "td", ">'", "'</td>");
        }
        string account = filternum(extract(s, "</td>", "</td>", "<td>", "</td>"));
        string addtime = extract(s, "</td>", "<td", ">", "</td>");

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

