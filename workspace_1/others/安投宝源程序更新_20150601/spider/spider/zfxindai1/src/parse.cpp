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
    
    kv["site_id"] = "zfxindai";
    kv["project_name"] = extract(bstr,"class=\"grid_7\">","class=\"box\">","\">","<span");
    kv["project_id"] = idstr;
    kv["borrowing_amount"] = filternum(extract(bstr, "class=\"grid_7\">", "class=\"span4 f30 bold zhise\"", "￥", "<em"));
    kv["annulized_rating"] = extracthtml(bstr, "class=\"grid_7\">", "class=\"span4 f30 bold zhise ml20\">", "","<em");
    kv["loan_period"] = extract(bstr, "p20 pt5 pb5", "%", "class=\"span4 f30 bold zhise\">", "</em>");
    if (kv["loan_period"].find("天") != string::npos) {
       kv["annulized_rating"] = doubletostring(s_atod(filternum(kv["annulized_rating"]).c_str())*365);}   
    else{  
       kv["annulized_rating"] = doubletostring(s_atod(filternum(kv["annulized_rating"]).c_str()));}
    kv["loan_period"] = loanperiod_util(kv["loan_period"]);
    kv["payment_method"] = extract(bstr,"class=\"fl w80 gray\">","还款方式：", " cur\">","<img");
    kv["invested_amount"] = longtostring(s_atol(kv["borrowing_amount"].c_str()) - s_atol(filternum(extract(bstr,"class=\"m15 mt15 mb5\"","满标还差","<span class=\"f24 ml5\">","</span>")).c_str()));
    kv["minimum_investment"] = "";
    kv["maximum_investment"] = "";
    kv["release_time"] = longtostring(stringtotime(extract(bstr,"class=\"fl w80 gray\"","发布日期：","id=\"pubTime\">","</span>").c_str(), "%Y-%m-%d"));
    kv["end_time"] = longtostring(time(NULL) + s_atol(extract(bstr, "<span", "class=\"fl w80 gray\">", "有效时间：", "小时").c_str())*3600);;

    kv["borrorwer"] = extract(bstr,"class=\"invset-box-title p15\">","借款人信息","用户名：","性别");
    kv["project_details"] = extract(bstr,"class=\"invset-box-title p15\"","借款人信息","用户名：","</ul>");


    printf(filename, "html/%s.brec", idstr);
    buf = readfile(filename);

    int investornum = 0;
    {
        string retstr;
        string::size_type tmp =  bstr.find("投标记录");
        if(tmp != string::npos){
            tmp = bstr.find("投资用户",tmp+1);
        }
        if(tmp != string::npos){
            tmp =  bstr.find("table-list-item",tmp+1);
        }
        if(tmp != string::npos){

            string striv = bstr.substr(tmp);
            string ivname;
            string ivaccount;
            string ivtime;
            while ((ivname = extract(striv, "<div", "<span", ">", "</span>")) != "") {
                ivaccount = filternum(extract(striv, "<div", "<span", "<span", "元"));
                ivtime = extract(striv, "元", "<span",">", "</span>");
                ivtime = longtostring(stringtotime(ivtime.c_str(), "%Y-%m-%d %H:%M"));
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
