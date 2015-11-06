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
    kv["site_id"] = "tuandai";
    kv["borrower"] = "";
    kv["credit_rating"] = "";
    kv["project_name"] = extract(bstr, "class=\"bond_invest_inf\"", "class=\"bond_inf_title box_dw\"", "16px;\">", "</span>");
    kv["project_id"] = idstr;
    kv["borrowing_amount"] =filternum( extract(bstr, "class=\"bond_invest_inf\"", "借款总额", "<span><b>", "</b>元"));
    kv["annulized_rating"] =filternum( extract(bstr, "class=\"bond_invest_inf\"", "年化利率", "<span><b>", "</b>"));
    kv["payment_method"] = extract(bstr, "class=\"bond_invest_inf\"", "还款方式", "</span>，", "</div>");
    kv["award"] = "";
    kv["loan_period"] = extract(bstr, "class=\"bond_invest_inf\"", "还款期限", "<span><b>", "</b>");
    kv["minimum_investment"] = filternum( extract(bstr, "class=\"bond_invest_inf\"", "class=\"bond_inf_unit box_dw\"", "出借单位：", "元</div>") );
    kv["maximum_investment"] = "";
    kv["release_time"] = "";
    kv["end_time"] = "";

    if (kv["minimum_investment"].size() != 0) {
        kv["invested_amount"] = longtostring (s_atod(extract(bstr, "class=\"bond_invest_inf\"", "class=\"bond_inf_incopies box_dw\"", "借入份数：", "份</div>").c_str()) * s_atod(kv["minimum_investment"].c_str()) );
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
                string account;

                if (!get_string_member(json["list"][i], "NickName", uname)
                        || !get_string_member(json["list"][i], "AddDate", addtime)
                        || !get_string_member(json["list"][i], "Amount", account))
                {   
                    continue;
                }

                invstr += longtostring(stringtotime(addtime.c_str(), "%Y/%m/%d %H:%M:%S")) + "|" + uname + "|" + account + "|";
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

