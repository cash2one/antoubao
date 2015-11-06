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

    kv["site_id"] = "kexindai";
    kv["borrowing_amount"] = num_util(extract(bstr,"class=\"box-3-item\">","class=\"w225\">", "借款总额(￥)","元"));
    kv["project_id"] = idstr;
    kv["project_name"] = extract(bstr, "class=\"box-3\">", "class=\"hd\">", "</i>", "<em");
    kv["annulized_rating"] = extracthtml(bstr, "class=\"box-3\">", "年利率", "class=\"strong co1\">", "</em>");
    kv["payment_method"] = extract(bstr,"class=\"box-3\">", "class=\"box-3-item\">", "还款方式：","</p>");
    kv["invested_amount"] = longtostring(s_atol(kv["borrowing_amount"].c_str()) - s_atol(filternum(extract(bstr,"class=\"box-3-r\">","可投标金额","class=\"strong co2\">","元")).c_str()));
     //kv["invested_amount"] = extract(bstr,"class=\"box-3-r\">","可投标金额","class=\"strong co2\">","元");
    kv["loan_period"] = loanperiod_util(extract(bstr,"class=\"box-3-item\">","还款期限","<dd>","</dd>"));
    kv["borrower"] = extract(bstr,"class=\"box4-bd-item\">","姓名","","</em>");

    printf(filename, "html/%s", idstr);
    buf = readfile(filename);

    int investornum = 0;
    {
        string retstr;
        string::size_type tmp =  bstr.find("前总投标额");
        if(tmp != string::npos){
            tmp = bstr.find("投标人",tmp+1);
        }
        if(tmp != string::npos){
            tmp =  bstr.find("ui-list-item",tmp+1);
        }
        if(tmp != string::npos){

            string striv = bstr.substr(tmp);
            string ivname;
            string ivaccount;
            string ivtime;
            while ((ivname = extract(striv, "<span", "<em", ">", "</em>")) != "") {
                ivaccount = filternum(extract(striv, "<span", "元", "</span>", "</em>"));
                ivtime = extract(striv, "元", "元", "</span>", "</em>");
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

