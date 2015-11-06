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
    kv["site_id"] = "gsdai";
    kv["borrower"] = "";
    kv["credit_rating"] = "";
    kv["project_name"] = extract(bstr, "class=\"gsdobj\"", "class=\"gsdobj_title\"", "</em>", "</h2>");
    kv["project_id"] = idstr;
    kv["borrowing_amount"] = filternum(extract(bstr, "class=\"gsdobj_wrap\"", "项目的总额", "</p><em>&yen;", "</em></li>"));
    kv["annulized_rating"] = filternum(extract(bstr, "class=\"gsdobj_wrap\"", "年化收益率", "<em>", "</em>"));

    kv["payment_method"] = extract(bstr, "class=\"gsdobj_wrap\"", "还款方式", "<dt>", "</dt>");
    kv["award"] = "";
    kv["loan_period"] = extract(bstr, "class=\"gsdobj_wrap\"", "还款期限", "<em>", "</li>");;
    if (kv["loan_period"].find("月") != string::npos) {
        kv["loan_period"] = longtostring(s_atod(kv["loan_period"].c_str()) * 30);
    }
    else
    {
        kv["loan_period"] = longtostring(s_atod(kv["loan_period"].c_str()));
    }

    double ramt = s_atod(filternum(extract(bstr, "class=\"gsdobj_wrap\"", "还需金额", "<dt>&yen;", "</dt>")).c_str());
    kv["invested_amount"] = doubletostring(s_atod(kv["borrowing_amount"].c_str()) - ramt);
    kv["release_time"] = "";
    kv["end_time"] = "";
    kv["project_details"] = extract(bstr, "class=\"gsdobj_wrap\"", "项目介绍", "<td>", "</td>");

    string invstr = "";
    int invnum = 0;

    string flag("class=\"font_lan\"><a href=\"/user/other/");
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

        //printf("%s\n", s.c_str());
        string uname = extract(s, "target=", "_blank", ">", "</a");
        string account = extract(s, "<div class=\"font_Orange\"", ">", "&yen;", "</div>");
        string addtime = extract(s, "class=\"font_Orange\"", "class=\"font_Orange\"", "<td>", "</td>");

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

