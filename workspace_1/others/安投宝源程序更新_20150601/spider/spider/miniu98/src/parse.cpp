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
    kv["site_id"] = "miniu98";
    kv["borrower"] = extract(bstr, "class=\"bd-7-r\"", "借款人信息", "姓名：", "</td>")
        + extract(bstr, "class=\"bd-7-r\"", "借款人信息", "手机号：", "</td>");
    kv["credit_rating"] = "";
    kv["project_name"] = extract(bstr, "<div class=\"bd-6 clearfix\">", "借款协议（范本）", "</a>", "</h3>");
    kv["project_id"] = idstr ;
    kv["borrowing_amount"] =filternum( extract(bstr, "<div class=\"bd-6-l\">", "借款总额", "<strong>", "元"));
    kv["annulized_rating"] =filternum( extract(bstr, "<div class=\"bd-6-l\">", "年化收益", "<strong>", "%"));
    kv["payment_method"] = extract(bstr, "<div class=\"bd-6-l\">", "付息方式：", "<span>", "</span>");
    kv["award"] = "";
    kv["loan_period"] = longtostring(s_atod(extract(bstr, "<div class=\"bd-6-l\">", "借款期限", "<strong>", "个月").c_str())*30);
    kv["minimum_investment"] = extract(bstr, "class=\"t-alert\"", "id=\"alertMessage\"", "投标金额必须是", "的整数倍");
    kv["maximum_investment"] = "";
    kv["end_time"] = "";
    kv["invested_amount"] = filternum(extract(bstr, "<div class=\"bd-7-l\">", "<div class=\"r\">", "出借总额：", "元"));
    kv["investors_volume"] = extract(bstr, "class=\"bd-7 clearfix\"","股票配资方案","出借人次：","人次");
    kv["project_details"] = extract(bstr, "class=\"bd-7 clearfix\"", "借款人信息", "<table>", "</table>");
    sprintf(filename, "html/%s.brec", idstr);
    buf = readfile(filename);

    string investor;
    int investornum = 0;
    {
        string::size_type pos = bstr.find("<table class=\"list\">");
        if (pos != string::npos) {
            pos = bstr.find("</tr>", pos + 1);
        }
        if (pos != string::npos) {
            string striv = bstr.substr(pos);
            string ivname;
            string ivamt;
            string ivtime;
            while ((ivname = extract(striv, "<tr>", "<td>", "", "</td>")) != "") {
                ivamt = filternum(extract(striv, "<tr>", "class=\"t-r\">", "", "元"));
                ivtime = longtostring(stringtotime(extract(striv, "元", "</td>", ">", "</td>").c_str(), "%Y-%m-%d %H:%M"));
                investor += ivtime + "|" + ivname + "|" + ivamt + "|";
                if (investornum == 0) {
                    kv["release_time"] = ivtime;
                }
                investornum++;
                pos = striv.find("</tr>", 1);
                if (pos == string::npos) {
                    break;
                }
                striv = striv.substr(pos);
            }
        }
    }

    kv["investor"] = investor;
    if (s_atol(kv["release_time"].c_str()) <= 0) {
        kv["release_time"] = longtostring(time(NULL));
    }
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

