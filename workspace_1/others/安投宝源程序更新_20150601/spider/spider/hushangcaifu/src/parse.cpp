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
    kv["site_id"] = "hushangcaifu";
    kv["borrower"] = extract(bstr,"20px;\"></tr>","<td colspan=\"2","借款用户:","</td>");
    kv["project_name"] = extract(bstr,"<head>","<meta http-equiv=","<title>","-  我要投资");
    kv["project_id"] = extract(bstr,"还款本息","实际到期日期","\"/invest/",".html\" target=\"_blank\">");
    kv["borrowing_amount"] = extract(bstr, "借款金额", "<td>", "span class=\"borrow_info\">", "</span>元");
    kv["borrowing_amount"] = doubletostring(atof(kv["borrowing_amount"].c_str()));
    kv["annulized_rating"] = extract(bstr, "借款金额<", "年利率", "<td><span class=\"borrow_info\">", "</span>%</td>");
    string arate;
    for (size_t i = 0; i < kv["annulized_rating"].size(); i++) {
        if (kv["annulized_rating"][i] == '.' || isdigit(kv["annulized_rating"][i])) {
            arate += kv["annulized_rating"][i];
        }
    }
    kv["annulized_rating"] = arate;
    kv["payment_method"] = extract(bstr,"<tr>","<td colspan=\"2\"","还款方式:","</td>");
    kv["loan_period"] = extract(bstr, "借款期限", "%</td>", "<span class=\"borrow_info\">", "</td>");
    int pos = kv["loan_period"].find("月");
    if (pos != -1) {
    kv["loan_period"] = doubletostring(atof(kv["loan_period"].c_str())*30);
   }  else{

    kv["loan_period"] = doubletostring(atof(kv["loan_period"].c_str()));
   }
    kv["release_time"] = extract(bstr,"<tr style=\"","<td colspan=\"2\" style=","审核时间:","</td>");
       long long etime1 = stringtotime(extract(bstr,"<tr style=\"","<td colspan=\"2\" style=","审核时间:","</td>").c_str(), "%Y-%m-%d %H:%M:%S");
       if (etime1 > 1000000000) {
           kv["release_time"] = longtostring(etime1);
       }
 
    //  kv["project_details"] = extract(bstr,"<div id=\"show_box","<table border=","借款人简介：","</table>");
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
            while ((ivname = extract(tmp, " <tr","<td align=", "\"center\">", "</td>")) != "") {
                ivaccount = extract(tmp, "%</td>", "元</td>", "\"center\">", "元</td>");
                ivtime = extract(tmp, "元</td>", "元</td>", "\"center\">", "</td>");
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
    
    
    
