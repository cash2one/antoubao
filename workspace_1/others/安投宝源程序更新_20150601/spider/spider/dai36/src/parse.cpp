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
    kv["site_id"] = "dai36";
    kv["borrower"] = "";
    kv["credit_rating"] = extract(bstr, "class=\"toninv_fkC\"", "信用等级", "<em>", "</em>");
    kv["project_name"] = extract(bstr, "class=\"contentbox\"", "class=\"tbttbg\"", "<em>", "</em>");
    kv["project_id"] = idstr;
    kv["borrowing_amount"] = filternum(extract(bstr, "class=\"toinv_wzbold\"", "class=\"toinv_wzbold\"", "<b>", "</b>"));
    kv["annulized_rating"] = filternum(extract(bstr, "class=\"toinvnsyz\"", ">", "<b>", "</b>"));
    kv["payment_method"] = extract(bstr, "class=\"toinv_qtzlC\"", "</div>", "<em>", "</em>");
    kv["award"] = "";
    kv["loan_period"] = loanperiod_util(extract(bstr, "span class=\"toinvnsyz\">", "class=\"toinv_wzbold\">", "<b>", "</span>"));

    kv["invested_amount"] = doubletostring(s_atod(kv["borrowing_amount"].c_str()) * 
        s_atod(filternum(extract(bstr, "class=\"toinv_qtzlC\"", "投标进度", "</span>", "</em>")).c_str()) / 100);
    kv["release_time"] = "";
    kv["end_time"] = "";
    kv["project_details"] = "";

    sprintf(filename, "html/%s.brec", idstr);
    buf = readfile(filename);

    string invstr;
    int invnum = 0;

    string tmps = "";
    if (buf) {
        vector<string> vs;
        strtovstr(vs, buf, "\n");

        string uname, account, addtime;
        for(int i = 0; i < vs.size(); i++)
        {
            switch(i%5)
            {
                case 0:
                    uname = extract(vs[i], "<", "td", ">", "</td>");
                    break;
                case 1:
                    account = filternum(extract(vs[i], "<td>", "<b>", "￥", "</b>"));
                    break;
                case 3:
                    addtime = extract(vs[i], "<", "td", ">", "</td>");
                    break;
                case 4:
                    invstr += longtostring(stringtotime(addtime.c_str(), "%Y-%m-%d %H:%M:%S")) + "|" + uname + "|" + account + "|";
                    invnum++;
                    break;
                default:
                    break;
            }
        }
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

