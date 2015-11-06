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
    kv["site_id"] = "0086cf";
    kv["project_id"] = idstr;
    kv["borrower"] = extract(bstr, "class=\"borrow_infor\"", "class=\"user_name\"", ">", "</p>");
    kv["project_name"] = extract(bstr, "class=\"tender_detai\"", "img src=", "/>", "<span");
    kv["borrowing_amount"] = num_util(filternum(extract(bstr, "class=\"tender_detai_cont\"", "借款金额", "class=\"yellow\">", "</em>")));
    kv["loan_period"] = loanperiod_util(extract(bstr, "class=\"tender_detai_cont\"", "借款期限", "<em>", "</em>"));
    kv["release_time"] = "";
    kv["payment_method"] = extract(bstr, "class=\"tender_detai_cont\"", "还款方式", "class=\"basic_value\">", "</span>");

    string invstr;
    int invnum = 0;

    string tmps = extracthtml(bstr, "class=\"trad_rec_lf\"", "<dl>", "</dt>", "</dl>");
    string flag("<dd>");
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

        string uname = extract(s, "<span>", "class=\"txt_lf\"", ">", "</span>");
        string account = filternum(extract(s, "<span>", "class=\"txt_lf\"", "<span>", "<em>"));
        string addtime = extract(s, "class=\"txt_lf\"", "<span>", "<span> ", "</span>");

        invstr += longtostring(stringtotime(addtime.c_str(), "%Y-%m-%d %H:%M")) + "|" + uname + "|" + account + "|";
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

