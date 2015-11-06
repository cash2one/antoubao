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
    kv["site_id"] = "tintinloan";
    kv["project_name"] = extract(bstr, "<div class=\"tender_detai\">", "<div class=\"tender", "<h2>","<img src=");
//    kv["borrower"] = extract(bstr,"<div class=\"top-l\">","<span class=","title=\"","");
    kv["project_id"] = extract(bstr,"<div class=\"tender_detai\">","<img src=","借款编号：","</span>");
    kv["borrowing_amount"] = extract(bstr,"tender_detai_lf\">","借款金额","\"f_c1\">","</em></span>");
    string::size_type pos = kv["borrowing_amount"].find("万");
    if (pos != string::npos){
        kv["borrowing_amount"] = doubletostring(atof(filternum(kv["borrowing_amount"]).c_str())*10000);
    } else{
        kv["borrowing_amount"] = doubletostring(atof(filternum(kv["borrowing_amount"]).c_str()));
    }  

    kv["annulized_rating"] = filternum(extract(bstr,"借款金额","年利率", "\"><em>", "</em>%</span>"));
    kv["payment_method"] = extract(bstr,"<li>","还款方式","basic_value\">","</span>");
    kv["loan_period"] = extract(bstr, "<li>", "还款期限", "\"><em>","</em></span>");
    int pos1 = kv["loan_period"].find("月");
    if (pos1 != -1) {
        kv["loan_period"] = longtostring(atof(kv["loan_period"].c_str())*30);
    }
    else{

        kv["loan_period"] = longtostring(atof(kv["loan_period"].c_str()));
    }

    // kv["invested_amount"] = doubletostring(s_atod(kv["borrowing_amount"].c_str()) - s_atod(filternum(extract(bstr,"剩余时间","额","￥","")).c_str()));
   //  kv["release_time"] = extract(bstr,"还款方式","发布时间","\">","</span>");
    //   kv["end_time"] = extract(bstr,"<ul class=\"d_date\">","<s>","满标时间：","</li>");  
  //  kv["project_details"] = extract(bstr,"role=\"tablist\">","借款详情","id=\"jkxq\">","<div class=\"bid_jkzl\">");
    {
            string tmp;
            string::size_type startpos = bstr.find("投标时间");
            if (startpos != string::npos) {
                string::size_type endpos = bstr.find("</table>", startpos);
                if (endpos != string::npos) {
                    tmp = bstr.substr(startpos, endpos - startpos);
                }
            }
            string ivname;
            string ivaccount;
            string ivtime;
            string retstr;
             tmp = tmp.substr(tmp.find("</tr>") + 1);
            while ((ivname = extract(tmp, "<tr>", "<td class=", "_list\">", "</td>")) != "") {
                ivaccount = extract(tmp, "</td>", "_list\">", ":","<em>元");
                ivtime = extract(tmp, "<em>元</em>", "_list\">", "_list\">", "</td>");
                ivtime = longtostring(stringtotime(ivtime.c_str(), "%Y-%m-%d %H:%M:%S")
                        );
                retstr += ivtime + "|" + ivname + "|" + ivaccount + "|";
                string::size_type pos = tmp.find("</tr>");
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
