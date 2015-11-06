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
    kv["site_id"] = "yiqihao";
    kv["borrower"] = extract(bstr, "div id=\"loaninfo-other\"", "借款用户", "：", "</p>");
    kv["credit_rating"] = extract(bstr, "id=\"loandetail\"", "<p>信用等级", "ico-star", "\">");
    kv["project_name"] = extract(bstr, "id=\"loandetail\"", "class=\"loaninfo-title\"", ">", "<");
    kv["project_id"] = idstr;
    kv["borrowing_amount"] =filternum( extract(bstr, "class=\"loaninfo-param\"", "流转总额", "￥", "</span>"));
    if (kv["borrowing_amount"].size() == 0) {
        kv["borrowing_amount"] =filternum( extract(bstr, "class=\"loaninfo-param\"", "贷款金额", "￥", "</span>"));
    }
    kv["annulized_rating"] =filternum( extract(bstr, "id=\"loandetail\"", "年利率", "class=\"darkred\">", "</span>"));
    kv["award"] = extract(bstr, "id=\"loandetail\"", "年利率", "icon-detail-reward\" title=\"", "\"");
    kv["payment_method"] = extract(bstr, "class=\"imain imain-star\"", "还款方式", "float:right\">", "</span>");
    string lperiod = extract(bstr, "id=\"loandetail\"", "期限", "class=\"darkred\">", "</span>");
    if (lperiod.find("月") != string::npos) {
        kv["loan_period"] = longtostring(s_atod(lperiod.c_str())*30);
    }
    else {
        kv["load_period"] = longtostring(s_atol(lperiod.c_str()));
    }

    kv["minimum_investment"] = filternum( extract(bstr, "id=\"loandetail\"", "流转总额", "<span class=\"bold\">￥", "</span>") );
    kv["invested_amount"] = extract(bstr, "id=\"loandetail\"", "完成度", "class=\"bold\">￥", "</span>");
    if (kv["invested_amount"].size() == 0 && kv["minimum_investment"].size() != 0)
    {
        kv["invested_amount"] = longtostring (s_atod(extract(bstr, "id=\"loandetail\"", "流转单位", "class=\"bold\">", "份</span>").c_str()) * s_atod(kv["minimum_investment"].c_str()) );
    }
    kv["project_details"] = extract(bstr, "贷款描述", "留言 <span", "font-size:14px;\">", "</div><div id=\"bidrecord\">");

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

        if (has_object_member(json, "data") && has_array_member(json["data"], "list"))
        {
            for (int i = 0; i < json["data"]["list"].size(); i++) {
                string uname;
                string addtime;
                string account;

                if (!get_string_member(json["data"]["list"][i], "uname", uname)
                        || !get_string_member(json["data"]["list"][i], "addtime", addtime)
                        || !get_string_member(json["data"]["list"][i], "money", account))
                {
                    continue;
                }

                invstr += addtime + "|" + uname + "|" + account + "|";
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

