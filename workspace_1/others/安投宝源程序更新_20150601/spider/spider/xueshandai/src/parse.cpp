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
    kv["site_id"] = "xueshandai";
    kv["borrower"] = extract(bstr,"借款人详情","<div id=\"jkmen\">","<span>","<img src=\"");
    kv["credit_rating"] = "";
    kv["project_name"] = extract(bstr,"<div class=\"","invesleft\">"," <h2 title=\"","\" class=");
    kv["project_id"] = extract(bstr,"&nbsp;","标号：","id\">","</span>");
    kv["borrowing_amount"] = filternum(extract(bstr, "<li><span>","</span>","标的总额：","元"));
    kv["invested_amount"] = filternum(extract(bstr, "html", "标的总额", "已投金额：", "元"));
    kv["annulized_rating"] = filternum(extracthtml(bstr, "<ul class=\"", "<span>", "预期年化收益率：", "%</span>"));
    kv["payment_method"] = extract(bstr,"还款方式:","<div","\">","</div>");
    kv["award"] = "";
    kv["loan_period"] = extract(bstr, "</font></li>","<li><span>", "还款期限：", "</span>");
    int pos = kv["loan_period"].find("月");
    if (pos != -1) {
        kv["loan_period"] = longtostring(atof(kv["loan_period"].c_str())*30);
    }  else{

        kv["loan_period"] = longtostring(atof(kv["loan_period"].c_str()));
    }
    kv["minimum_investment"] = "0";
    string miniv = extract(bstr,"/center-borrow/bid","","","</form>");
    for (size_t i = 0; i < miniv.size(); i++) {
        if (isdigit(miniv[i])) {
            kv["minimum_investment"] = longtostring(s_atol(miniv.c_str() + i));
            break;
        }
    }
    kv["maximum_investment"] = "";
    kv["release_time"] = longtostring(stringtotime(extract(bstr,"</span>","<span id=\"","发标时间：","</span>").c_str(), "%Y-%m-%d %H:%M"));
    kv["end_time"] = longtostring(time(NULL) + s_atol(extract(bstr, "<div id=\"contain\"", "span class=\"timer\"", "sum=\"", "\"").c_str())/1000);
    kv["project_details"] = extract(bstr, "class=\"navBox\"", "class=\"tabmenu\"", "class=\"jkr_r\">", "<div class=\"tzxq_z\"");

    {
        string ivstr;;
        int ivnum = 0;
        string::size_type pos = bstr.find("</html>");
        if (pos != string::npos) {
            string tstr = bstr.substr(pos);
            pos = tstr.find("</tr>");
            while (pos != string::npos) {
                tstr = tstr.substr(pos + 1);
                string uname = extract(tstr, "<td>", "<td>", "", "</td>");
                string account = filternum(extract(tstr, "<td>", "<td>", "<td>", "元"));
                string addtime = extract(tstr, "元", "元", "<td>", "</td>");
                if (uname == "" || account == "" || addtime == "") {
                    break;
                }
                addtime = longtostring(stringtotime(addtime.c_str(), "%Y-%m-%d"));
                ivstr += addtime + "|" + uname + "|" + account + "|";
                ivnum++;
                pos = tstr.find("</tr>");
            }
        }
        kv["investor"] = ivstr;
        kv["investors_volume"] = longtostring(ivnum);
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
