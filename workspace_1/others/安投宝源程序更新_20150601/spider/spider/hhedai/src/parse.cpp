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
    kv["site_id"] = "hhedai";
    kv["borrower"] = extract(bstr,"项目简介", "基本情况", "：", "<p");
    kv["credit_rating"] = extract(bstr,"我要投资", "信用等级", "：","</span></div>");
    kv["project_name"] = extract(bstr, "我要投资", "借款详情", "<font class=\"borrow_b fl\" >", "</font>");
    kv["project_id"] = idstr;
    kv["borrowing_amount"] = filternum(extract(bstr, "借款总额", "</p>", ">", "元"));
    kv["annulized_rating"] = filternum(extract(bstr, "净年化收益率","<p",">", "%"));
    kv["payment_method"] = extract(bstr, "<span", "<p", "还款方式", "</p>");
    kv["invested_amount"] = filternum(extract(bstr, "目前投标总额", "：", ">", "</span>"));
	kv["minimum_investment"] = num_util(extract(bstr,"发布日期","投资限额","：","起投"));
    kv["maximum_investment"] = num_util(extract(bstr, "发布日期", "投资限额", "最高限额", "<"));
    kv["release_time"] = longtostring(stringtotime((extract(bstr, "还款日期", "发布日期", "：", "</p>")).c_str(),"%Y-%m-%d"));
    long rtime = s_atol(extract(bstr, "class=\"borrow_r_t\"", "id=\"endtime\">", "", "<").c_str());
    if (rtime > 0) {
        kv["end_time"] = longtostring(time(NULL) + rtime);
    }
    kv["loan_period"] = extract(bstr, "借款期限", "<font class=\"borrow_f_y\">", "", "<");

    kv["project_details"] = extract(bstr, "项目简介", "</td>","<strong>", "</td");

    sprintf(filename, "html/%s.brec", idstr);
    buf = readfile(filename);

    {
        string retstr;
        string::size_type tmp =  bstr.find("投标人");
        if(tmp != string::npos){
            tmp = bstr.find("投标时间", tmp+1);
        }
        if(tmp != string::npos){
            tmp =  bstr.find("</tr>",tmp+1);
        }
        string::size_type etmp = string::npos;
        if (tmp != string::npos) {
            etmp = bstr.find("</tbody>", tmp);
        }
        if(tmp != string::npos && etmp != string::npos){
            string striv = bstr.substr(tmp + 1, etmp - tmp - 1);
            string ivname;
            string ivaccount;
            string ivtime;
            while ((ivname = extract(striv, "</td", "<td", "-->", "</td")) != "") {
                ivaccount = filternum(extract(striv, "</td", "</td", "￥", "</td>"));
                ivtime = extract(striv, "</td", "</td", "</td>", "</td>");
                ivtime = longtostring(stringtotime(ivtime.c_str(), "%Y-%m-%d %H:%M:%S"));
                retstr += ivtime + "|" + ivname + "|" + ivaccount + "|";

                if (striv.find("</tr>") == string::npos) {
                    break;
                }
                striv = striv.substr(striv.find("</tr>") + 1);
            }
        }
        kv["investor"] = retstr;
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

