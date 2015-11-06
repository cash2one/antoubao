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
    kv["site_id"] = "hao8dai";
    kv["borrower"] = extract(bstr,"class=\"detailedtopA1\">","用户名：","</small>","</span>");
    kv["credit_rating"] = "";
    kv["project_name"] = extract(bstr, "class=\"detailedtopB1b\"","<span",">","</span>");
    kv["project_id"] = idstr;
    kv["borrowing_amount"] = filternum(extract(bstr, "lass=\"detailedtopB3\">", "<ul>", "￥", "</span>"));
    kv["annulized_rating"] = filternum(extracthtml(bstr, "class=\"detailedtopB3\">","￥","class=\"DDD\">", "%"));
    kv["payment_method"] = extract(bstr, "class=\"detailedtopB3\">", "%", "<span class=\"EEE\">", "</span>");
    kv["award"] = "";
    
    kv["loan_period"] = extract(bstr,"class=\"detailedtopB3\">","%","<span class=\"DDD\">","</small>");
    string::size_type pos = kv["loan_period"].find("月");
    if (pos != string::npos){
        kv["loan_period"] = longtostring(s_atod(filternum(kv["loan_period"]).c_str())*30);
    } else{
        kv["loan_period"] = longtostring(s_atod(filternum(kv["loan_period"]).c_str()));
    } 
 

    kv["minimum_investment"] = extract(bstr, "class=\"progress\" >", "￥", "￥", "</span>");
    kv["maximum_investment"] = "";
    kv["release_time"] = "";
    kv["project_details"] = extract(bstr, "class=\"detailed\"", "id=\"deta_tabbox1\">", "还款信息", "<dd class=\"tab_con1\">");
    kv["end_time"] = "";
    kv["invested_amount"] = doubletostring(s_atod(kv["borrowing_amount"].c_str()) - s_atod(filternum(extract(bstr,"class=\"detailedtopB1c\">","借款协议书","距离还款时间","</span>")).c_str()));


    printf(filename, "html/%s.brec", idstr);
    buf = readfile(filename);

    int investornum = 0;
    {
        string retstr;
        string::size_type tmp =  bstr.find("投标记录");
        if(tmp != string::npos){
            tmp = bstr.find("投标人/关系",tmp+1);
        }
        string::size_type endpos = string::npos;
        if(tmp != string::npos){
            tmp =  bstr.find("</div>",tmp+1);
            endpos = bstr.find("class=\"invest-content-page\">", tmp);
        }
        if(tmp != string::npos && endpos != string::npos){

            string striv = bstr.substr(tmp, endpos - tmp);
            string ivname;
            string ivaccount;
            string ivtime;
            while ((ivname = extract(striv, "<ul>", "<span", ">", "</span>")) != "") {
                ivaccount = filternum(extract(striv, "<ul>", "%", "￥", "</span>"));
                ivtime = extract(striv, "￥", "￥", "class=\"DDD\">", "</span>");
                ivtime = longtostring(stringtotime(ivtime.c_str(), "%Y-%m-%d %H:%M:%S"));

                if(ivaccount == "")
                {
                    break;
                }

                retstr += ivtime + "|" + ivname + "|" + ivaccount + "|";
                investornum++;
                if (striv.find("</ul>") == string::npos) {
                    break;
                }
                striv = striv.substr(striv.find("</ul>") + 1);


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

