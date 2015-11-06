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
    kv["site_id"] = "iqianjin";
    kv["borrower"] = "";
    kv["credit_rating"] = "";
    kv["project_name"] = extract(bstr, "class=\"ui-box-lhead\"", "项目名称", "</em>", "</div>");
    kv["project_id"] = idstr;
    kv["borrowing_amount"] =filternum( extract(bstr, "class=\"ui-box-lhead\"", "计划金额", "id=\"amount\">", "<span>"));
    if (kv["borrowing_amount"].size() == 0)
    {
        kv["borrowing_amount"] =filternum( extract(bstr, "class=\"ui-box-lhead\"", "借款金额", "id=\"amount\">", "<span>"));
    }

    kv["annulized_rating"] =filternum( extract(bstr, "class=\"ui-box-lhead\"", "年化收益率", "id=\"insterest\">", "</div>"));
    kv["payment_method"] = "";
    kv["award"] = "";
    string lperiod = extract(bstr, "class=\"ui-box-lhead\"", "还款期限", "id=\"period\">", "</span></div>");
    if (lperiod.size() == 0)
    {
        lperiod = extract(bstr, "class=\"ui-box-lhead\"", "\">锁定期", "class=\"intro-text\">", "</span></div>");
    }
    if (lperiod.find("月") != string::npos) {
        kv["loan_period"] = longtostring(s_atod(lperiod.c_str())*30);
    }   
    else {
        kv["load_period"] = longtostring(s_atol(lperiod.c_str()));
    }

    kv["minimum_investment"] = filternum( extract(bstr, "class=\"ui-box-lhead\"", ">最小投资金额", "class=\"intro-text\">", "<span>元") );
    kv["maximum_investment"] = "";
    kv["release_time"] = "";
    kv["end_time"] = "";

    string remain = extract(bstr, "class=\"ui-box-lhead\"", ">剩余份数", "id=\"maxShare\">", "</em>") ;
    if (kv["borrowing_amount"].size() > 0 && remain.size() > 0 && kv["minimum_investment"].size() > 0 ) {
        kv["invested_amount"] = longtostring(s_atol(kv["borrowing_amount"].c_str()) - s_atol(kv["minimum_investment"].c_str()) * s_atol(remain.c_str()));
    } else {
        kv["invested_amount"] = "";
    }
    kv["project_details"] = "";

    kv["investor"] = "";
    kv["investors_volume"] = "";

    sprintf(filename, "html/%s.brec", idstr);
    buf = readfile(filename);
    string invstr;
    int invnum = 0;
    if (buf) {
        char *p = buf;
        size_t buflen = strlen(buf);
        string jstr = string(buf, buflen);
        free(buf);

        Value json = stringtojson(jstr);

        if (has_array_member(json, "list"))
        {   
            for (int i = 0; i < json["list"].size(); i++) {
                string uname;
                string addtime;
                double account;

                if (!get_string_member(json["list"][i], "createTime", addtime)
                        || !get_double_member(json["list"][i], "amount", account))
                {
                    continue;
                }

                if (!get_string_member(json["list"][i], "userName", uname)
                    && !get_string_member(json["list"][i], "lenderName", uname))
                {
                    continue;
                }

                invstr += longtostring(stringtotime(addtime.c_str(), "%Y-%m-%d %H:%M")) + "|" + uname + "|" + longtostring((long int)account) + "|";
                invnum++;
            }
        }
    }
    kv["investor"] = invstr;
    kv["investors_volume"] = longtostring(invnum);

    printstringmap(kv);

    if (s_atol(kv["borrowing_amount"].c_str()) <= 0) {
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

