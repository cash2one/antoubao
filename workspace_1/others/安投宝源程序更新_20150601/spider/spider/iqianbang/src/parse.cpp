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
    kv["site_id"] = "iqianbang";
    kv["borrower"] = "";
    kv["credit_rating"] = "";
    kv["project_name"] = extract(bstr, "class=\"m2-tranHide\"", "所选项目", "</span>", "</div>");
    kv["project_id"] = idstr;
    kv["borrowing_amount"] = extract(bstr, "class=\"m2-detItemlef-con\"", "期限</span>", "class=\"m2-detItempsg-big\">", "</span>");
    if (kv["borrowing_amount"].find("万") != string::npos) {
        kv["borrowing_amount"] = doubletostring( s_atod(filternum(kv["borrowing_amount"]).c_str()) * 10000 );
    } else {
        kv["borrowing_amount"] = filternum(kv["borrowing_amount"]);
    }

    kv["annulized_rating"] = filternum(extract(bstr, "class=\"m2-detItemlef-con\"", "style=\"white-space: nowrap;\"", ">", "</span>"));
    kv["payment_method"] = "";
    kv["award"] = "";
    kv["loan_period"] = extract(bstr, "class=\"m2-detItemlef-con\"", "年化收益", "class=\"m2-detItempsg-big\">", "</span>");
    if (kv["loan_period"].find("月") != string::npos) {
        kv["loan_period"] = longtostring(s_atod(kv["loan_period"].c_str()) * 30);
    }
    else {
        kv["loan_period"] = longtostring(s_atod(kv["loan_period"].c_str()));
    }

    kv["invested_amount"] = doubletostring(s_atod(kv["borrowing_amount"].c_str()) - s_atod(filternum(extract(bstr, "class=\"m2-detItemrig\"", "可投金额", "id='left_money'>", "</span>")).c_str()));
    kv["release_time"] = "";
    kv["end_time"] = "";
    kv["project_details"] = extract(bstr, "class=\"m2-detSit m2-detSection\"", "项目情况", "26px;'>", "</p>");

    string invstr;
    int invnum = 0;

    sprintf(filename, "html/%s.brec", idstr);
    buf = readfile(filename);

    if (buf) {
        size_t buflen = strlen(buf);
        string jstr = string(buf, buflen);
        free(buf);

        Value json = stringtojson(jstr);
        int total = 0;

        string res;
        if (has_string_member(json, "count"))
        {   
            get_int_member(json, "count", total);

            for (int i = 0; i < total; i++) {
                string uname;
                string addtime;
                double account;

                if (!get_string_member(json["list"][i], "user_name", uname)
                    || !get_string_member(json["list"][i], "add_time", addtime)
                    || !get_double_member(json["list"][i], "investor_capital", account))
                {   
                    continue;
                }

                invstr += addtime + "|" + uname + "|" + doubletostring(account) + "|";
                invnum++;
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

