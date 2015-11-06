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
    kv["site_id"] = "sunfobank";
    kv["borrower"] = extract(bstr,"借款人信息","<em>姓","名：</em>","年龄：");
    kv["credit_rating"] = "0";
    kv["project_name"] = extract(bstr, "class=\"content-left\">", "class=\"borrowTitle\">", "<b>", "</b>");
    kv["project_id"] = idstr ;
    kv["borrowing_amount"] = filternum(extract(bstr, "class=\"borrowAmount\"", "借款金额", "class=\"amountContent\">", "元"));
    kv["annulized_rating"] = filternum(extract(bstr, "class=\"awardAnnualRate\"", "年利率", "class=\"rateContent\">", "<span>"));
    kv["payment_method"] = extract(bstr, "class=\"paymentMode\"", "还款方式：", "<span>", "</span>");
    kv["award"] = "";
    kv["loan_period"] = longtostring(s_atod(extract(bstr, "class=\"deadline\"", "借款期限：", ">", "个月").c_str()) * 30);
    kv["minimum_investment"] = extract(bstr, "class=\"borrowLi2\"", "起投金额：", "<span>","元");
    kv["maximum_investment"] = "";
    kv["release_time"] = "0";
    kv["project_details"] = extract(bstr, "class=\"usertitle borrow-detail-nav\"", "项目详情", "<!-- 项目详情Tab页 -->", "资料展示");
    kv["end_time"] = "0"; 
    kv["invested_amount"] = longtostring(s_atol(kv["borrowing_amount"].c_str()) - s_atol(extract(bstr, "class=\"borrowLi3\"", "剩余额度：", "class=\"surplusSpan1\"", "元").c_str()));               

    sprintf(filename, "html/%s.brec", idstr);
    buf = readfile(filename);
    //bstr = string(buf);
    //free(buf);
    int investornum = 0;
    {
        string retstr;
        string::size_type tmp =  bstr.find("<li class=\"list_invest\">");
        if(tmp != string::npos){
            
            string striv = bstr.substr(tmp);
            string ivname;
            string ivaccount;
            string ivtime;
            while ((ivname = extract(striv, "<i>", "", "", "</i>")) != "") {
                ivaccount = filternum(extract(striv, "</i>", "</i>", "<i>", "</i>"));
                ivtime = extract(striv, "</i>", "</i>", "</i>", "</i>");
                ivtime = longtostring(stringtotime(ivtime.c_str(), "%Y-%m-%d %H:%M:%S"));
                if (striv.find("</li>") == string::npos) {
                    break;
                }
                striv = striv.substr(striv.find("</li>") + 1);

                retstr += ivtime + "|" + ivname + "|" + ivaccount + "|";
                investornum++;
            }
        }
        kv["investor"] = retstr;
    }
    kv["investors_volume"] = longtostring(investornum);
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
