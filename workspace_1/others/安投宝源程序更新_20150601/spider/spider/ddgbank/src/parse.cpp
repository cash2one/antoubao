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
    kv["site_id"] = "ddgbank";
    kv["project_id"] = idstr;
    kv["borrower"] = extract(bstr, "class=\"content\"", "借款人", "<td width=\"14%\">", "</td>");
    kv["project_name"] = extract(bstr, "class=\"main\"", "class=\"biao_name\">", ">", "</a>");

    kv["borrowing_amount"] = num_util(extract(bstr, "id=\"yitouzibishu\"", "id=\"yitouzijine\"", ">", "</li>"));
    kv["loan_period"] = longtostring( s_atol(filternum(extract(bstr, "class=\"none qixian\"", "期限", "<dd>共", "</dd>")).c_str()) 
        * s_atol(num_util(extract(bstr, "class=\"none qixian\"", "每期", "<dd>", "</dd>")).c_str()) );
    kv["release_time"] = "";
    kv["payment_method"] = extract(bstr, "class=\"hkfs\"", "</a>", "|", "</span>");

    string invstr;
    int invnum = 0;

    sprintf(filename, "html/%s.brec", idstr);
    buf = readfile(filename);
    if (!buf) {
        return 1;
    }
    string tmps = string(buf);
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

        string uname = extract(s, "<td>", "\\n", "\\t\\t\\t\\t\\t", "\\t");
        string account = filternum(extract(s, "<td>", "<td", ">", "<"));
        string addtime = extract(s, "<td>", "<td>", "<td>", "<");

        invstr += longtostring(stringtotime(addtime.c_str(), "%Y-%m-%d")) + "|" + uname + "|" + account + "|";
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

