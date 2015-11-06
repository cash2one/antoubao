#include <stdio.h>
#include <stdlib.h>
#include <ctype.h>
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
    kv["site_id"] = "dddai";
    kv["borrower"] = "";
    kv["credit_rating"] = "";
    kv["project_name"] = extract(bstr,"</script>","<div class=\"box clearfix\">","<h3><b>","</b></h3>");
    kv["project_id"] = idstr;
    kv["borrowing_amount"] = filternum(extract(bstr, "<th width=", "计划金额：", "￥<b>", "</b></font> 元</td>"));
    kv["annulized_rating"] = filternum(extract(bstr, "<div class=\"b2", "预期收益", "</th><td>", "%"));
    kv["payment_method"] = "";
    kv["award"] = "";
    kv["loan_period"] = extract(bstr, "<div class=\"b2", "锁定期限", "</th><td>", "天 </td>");
    kv["invested_amount"] = longtostring(
            s_atol(kv["borrowing_amount"].c_str()) - s_atol(filternum(extract(bstr,"<div class=\"b2","剩余金额","￥<b>","</b></font> 元</td>")).c_str()));
    kv["minimum_investment"] = extract(bstr,"<div class=\"b2","最低加入金额","￥<b>","</b></font> 元</td>");
    string minimum;
    for (size_t i = 0; i < kv["minimum_investment"].size(); i++) {
        if (kv["minimum_investment"][i] != ',') {
            minimum += kv["minimum_investment"][i];
        }
    } 
    kv["minimum_investment"] = minimum;
    kv["maximum_investment"] = extract(bstr,"<div class=\"b2","最高加入金额","￥<b>","</b></font> 元</td>");
    string maximum;
    for (size_t i = 0; i < kv["maximum_investment"].size(); i++) {
        if (kv["maximum_investment"][i] != ',') {
            maximum += kv["maximum_investment"][i];
        }
    } 
    kv["maximum_investment"] = maximum;
    kv["release_time"] = longtostring(stringtotime(extract(bstr,"<div class=\"b2","加入开始时间","</th><td>","</td>").c_str(), "%Y-%m-%d %H:%M"));
    kv["end_time"] = longtostring(stringtotime(extract(bstr,"<div class=\"b2","加入结束时间","</th><td>","</td>").c_str(), "%Y-%m-%d %H:%M"));
    int investornum = 0;
    kv["project_details"] = extract(bstr,"计划介绍","<p style=","10px 0 20px;\">","</p>");
    {
        string tmp = bstr.substr(bstr.find("加入记录"));
        tmp = tmp.substr(tmp.find("编号"));
        tmp = tmp.substr(tmp.find(" <tr>") + 1);
        string ivname;
        string ivaccount;
        string ivtime;
        string retstr;
        while ((ivname = extract(tmp, "<td>", "</td>", "<td>", "</td>")) != "") {
            ivaccount = extract(tmp, "red", "￥", "<b>", "</b>");
            ivtime = extract(tmp, "<td>", "￥", "<td>", "</td>");
            ivtime = longtostring(stringtotime(ivtime.c_str(), "%Y-%m-%d %H:%M"));
            if (tmp.find("<tr>") == string::npos) {
                break;
            }

            tmp = tmp.substr(tmp.find("<tr>") + 1);
            retstr += ivtime + "|" + ivname + "|" + ivaccount + "|";
            investornum++;
        }
        kv["investor"] = retstr;
    }
    kv["investors_volume"] = longtostring(investornum);
    printstringmap(kv); 
    if (kv["project_id"] == "" || kv["release_time"] == "") {
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

