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
    kv["site_id"] = "xuridai";
    kv["borrower"] = extract(bstr,"昵称","<span class=","\"gary01\">","</span><br/>");
    kv["credit_rating"] = extract(bstr,"信用评级","信用等级","<span class=\"blue fb\">","</span>");
    kv["project_name"] = extract(bstr,"\"investment_left\">","investment_detailBox\">"," _height:33px;\">"," <b style=");
    kv["project_id"] = extract(bstr,"还款方式"," id=","\"bid\" value=\"","\" /></td>");
    kv["borrowing_amount"] = filternum(extract(bstr, "借款金额","<span class=", "¥","</span>"));
    kv["annulized_rating"] = filternum(extracthtml(bstr, "借款金额", "年利率", "\"percentage fw\">", "%</span>"));
    kv["payment_method"] = extract(bstr,"td width=","还款方式","</span>","<input name=");
    kv["award"] = "";
    kv["loan_period"] = extract(bstr, "月利息", "借款期限", "\"month fw\">", "</span>");
    if (kv["loan_period"].find("月") != string::npos) {
        kv["loan_period"] = longtostring(atof(kv["loan_period"].c_str())*30);
    }  else{
        kv["loan_period"] = longtostring(atof(kv["loan_period"].c_str()));
    }
    kv["investors_volume"] = extract(bstr,"<tr>","已投标数","class=\"fb\">","</span>");
    kv["invested_amount"] = longtostring(s_atol(kv["borrowing_amount"].c_str()) - s_atol(filternum(extract(bstr,"已投标数","还需额度","class=\"fb fw\">¥","</span>")).c_str()));
    kv["minimum_investment"] = "";
    kv["maximum_investment"] = "";
    kv["release_time"] = "0";
    kv["end_time"] = "0";
    kv["project_details"] = extract(bstr,"借款描述","投标奖励","资料审核","担保奖励及信息");

    {
        string tmp = bstr.substr(bstr.find("序号"));
        string ivname;
        string ivaccount;
        string ivtime;
        string retstr;
        while ((ivname = extract(tmp, "\"w135\">", "用户", "_blank\">", "</a>")) != "") {

            ivaccount = extract(tmp, "用户", "</span><span", "\"w160\">", "元 </span>");

            ivtime = extract(tmp, "元 </span", "\"w110\"", "\"w220 right\">", "</span></li>");
            ivtime = longtostring(stringtotime(ivtime.c_str(), "%Y年%m月%d日 %H时%M分")
                    );
            tmp = tmp.substr(tmp.find("用户") + 1);
            retstr += ivtime + "|" + ivname + "|" + ivaccount + "|";
        }
        kv["investor"] = retstr;
    }


    printstringmap(kv);
    if (kv["project_id"] == "") {
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

