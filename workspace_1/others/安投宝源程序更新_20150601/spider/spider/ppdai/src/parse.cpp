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
    kv["site_id"] = "ppdai";
    kv["borrower"] = extract(bstr, "class=\"lendDetailContent_infoDetail_userInfo", "</a>", "class=\"username\">", "</a>");
    kv["credit_rating"] = extract(bstr,"class=\"altQust\"","<span","class=\"creditRating ","\">");
    kv["project_name"] = extract(bstr, "class=\"lendDetailContent_infoDetail\"", "class=\"clearfix\"", ">", "</span>");
    kv["project_id"] = idstr ;
    kv["borrowing_amount"] =filternum( extract(bstr, "class=\"w528 clearfix\"", "借款总额", "</em>", "</dd>"));
    kv["annulized_rating"] =filternum( extract(bstr, "借款总额", "年利率", "<dd>", "%"));
    kv["payment_method"] = extract(bstr, " 剩余时间：", "class=\"item item1\"", ">", "</div>");
    kv["award"] = "";
    kv["loan_period"] = longtostring(s_atod(filternum(extract(bstr, "class=\"w528 clearfix\"","class=\"nodbr\"","期限","个月")).c_str())*30);
    kv["minimum_investment"] = extract(bstr,"class=\"input clearfix\"","class=\"inputSum\"","placeholder=\"","元");
    kv["maximum_investment"] = "";
    kv["release_time"] = "";
    string etimestr = extract(bstr, "class=\"otherInfo", "class=\"item\"", "剩余时间：", "</span>");
    if (etimestr.find("结束时间：") != string::npos) {
        kv["end_time"] = longtostring(stringtotime(etimestr.substr(etimestr.find("结束时间：") + strlen("结束时间：")).c_str(), "%Y/%m/%d"));
    }
    else {
        kv["end_time"] = longtostring(stringtotime(extract(bstr, "<script>", "deadline", "Date(\"", "\"").c_str(), "%Y/%m/%d %H:%M:%S"));
    }
    kv["invested_amount"] = longtostring(s_atol(kv["borrowing_amount"].c_str()) - s_atol(filternum(extract(bstr,"class=\"item item1\"","借款余额：","id=\"listRestMoney\"","</span>")).c_str()));
    kv["project_details"] = extract(bstr, "class=\"lendDetailTab w1000center\"","借款详情", "<p>", "</p>");

    sprintf(filename, "html/%s.brec", idstr);
    buf = readfile(filename);

    int investornum = 0;
    {
        string retstr;
        string::size_type tmp =  bstr.find("投标记录");
        if(tmp != string::npos){
            tmp = bstr.find("投标人", tmp+1);
        }
        if(tmp != string::npos){
            tmp =  bstr.find("</ul>",tmp+1);
        }
        if(tmp != string::npos){

            string striv = bstr.substr(tmp);
            string ivname;
            string ivaccount;
            string ivtime;
            while ((ivname = extract(striv, "<li", "<a", ">", "</a>")) != "") {
                ivaccount = filternum(extract(striv, "</li>", "</li>", ">", "</li>"));
                ivtime = extract(striv, "</li>", "</li>", "class=\"w327\">", "</li>");
                ivtime = longtostring(stringtotime(ivtime.c_str(), "%Y/%m/%d %H:%M:%S"));
                if (striv.find("</ol>") == string::npos) {
                    break;
                }
                striv = striv.substr(striv.find("</ol>") + 1);

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

