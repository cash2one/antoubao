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
    kv["site_id"] = "goodsure";
    kv["project_name"] = extract(bstr, "<meta http-equiv=", "<link href=", "<title>"," - ");
  //  kv["borrower"] = extract(bstr,"<div class=\"top-l\">","<span class=","title=\"","");
    kv["project_id"] = extract(bstr,"<form action=","><a class=","html?borrow_id=","\">");
    kv["borrowing_amount"] = extract(bstr,"金额","年利率","￥","<em class=");
    string::size_type pos = kv["borrowing_amount"].find("万");
    if (pos != string::npos){
        kv["borrowing_amount"] = doubletostring(atof(filternum(kv["borrowing_amount"]).c_str())*10000);
    } else{
        kv["borrowing_amount"] = doubletostring(atof(filternum(kv["borrowing_amount"]).c_str()));
    }  

    kv["annulized_rating"] = filternum(extract(bstr,"年利率","元</em></span>", "\">", "<em class="));
    kv["payment_method"] = extract(bstr,"投标进度","还款方式","<span class=\"fl\">","</span>");
    kv["loan_period"] = extract(bstr, "元</em></span>", "%</em></span>", "\">","</em></span>");
    int pos1 = kv["loan_period"].find("月");
    if (pos1 != -1) {
        kv["loan_period"] = longtostring(atof(kv["loan_period"].c_str())*30);
    }
    else{

        kv["loan_period"] = longtostring(atof(kv["loan_period"].c_str()));
    }

    // kv["invested_amount"] = doubletostring(s_atod(kv["borrowing_amount"].c_str()) - s_atod(filternum(extract(bstr,"剩余时间","额","￥","")).c_str()));
     kv["release_time"] = extract(bstr,"还款方式","发布时间","\">","</span>");
    kv["project_details"] = extract(bstr,"<div class=","<div class=\"span6\">","借款详情","</p>");
    {
            string tmp = bstr.substr(bstr.find("row-fluid tender-item \">"));
            string ivname;
            string ivaccount;
            string ivtime;
            string retstr;
             tmp = tmp.substr(tmp.find("row-fluid tender-item \">")+1);
            while ((ivname = extract(tmp, "<span class=", "<span class=", "\">", "</span>")) != "") {
                ivaccount = extract(tmp, "</span>", "</span>", "\">","元</span>");
                ivtime = extract(tmp, "</spa>", "元</span>", "\">", "</span>");
                ivtime = longtostring(stringtotime(ivtime.c_str(), "%Y-%m-%d %H:%M")
                        );
                retstr += ivtime + "|" + ivname + "|" + ivaccount + "|";
                string::size_type pos = tmp.find("row-fluid tender-item \">");
                if (pos != string::npos) {
                    tmp = tmp.substr(pos + 1);
                }
                else {
                   break;
            }
        }
      kv["investor"] = retstr;    
    }


    if (kv["project_id"] == "" ) {
        return 1;
    }
   printstringmap(kv);
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
