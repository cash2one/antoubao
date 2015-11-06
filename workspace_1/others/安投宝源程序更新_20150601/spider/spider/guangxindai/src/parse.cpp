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
    kv["site_id"] = "guangxindai";
    kv["project_name"] = extract(bstr, "<div class=\"invest_b\">", "<A title=","></A> "," <span class=");
    kv["borrower"] = extract(bstr,"<a title=","<p>","用户名：","<p>");
    kv["credit_rating"] = extract(bstr,"</div>","信用积分","title=\"","分\"");
    kv["project_id"] = extract(bstr,"<tr>","<td align=\"left\">","/borrows/index/","\" target=");
    kv["borrowing_amount"] = extract(bstr,"</h2>","借款金额","￥","</span></p>");
    string::size_type pos = kv["borrowing_amount"].find("万");
    if (pos != string::npos){
        kv["borrowing_amount"] = doubletostring(atof(filternum(kv["borrowing_amount"]).c_str())*10000);
    } else{
        kv["borrowing_amount"] = doubletostring(atof(filternum(kv["borrowing_amount"]).c_str()));
    }  

    kv["annulized_rating"] = filternum(extract(bstr,"借款金额","年利率", "\">", "%</span></p>"));
    kv["payment_method"] = extract(bstr,"</h2>","<p>","还款方式：","</p>");
    kv["loan_period"] = extract(bstr, "</h2>", "<p>", "借入期限：","</p>");
    int pos1 = kv["loan_period"].find("月");
    if (pos1 != -1) {
        kv["loan_period"] = longtostring(atof(kv["loan_period"].c_str())*30);
    }
    else{

        kv["loan_period"] = longtostring(atof(kv["loan_period"].c_str()));
    }

    // kv["invested_amount"] = doubletostring(s_atod(kv["borrowing_amount"].c_str()) - s_atod(filternum(extract(bstr,"剩余时间","额","￥","")).c_str()));
       long long etime1 = stringtotime(extract(bstr,"<ul>","<li>","审核时间：","</li>").c_str(), "%Y-%m-%d %H:%M:%S");
       if (etime1 > 1000000000) {
           kv["release_time"] = longtostring(etime1);
       }
   //    kv["end_time"] = extract(bstr,"<ul class=\"d_date\">","<s>","满标时间：","");  
    kv["project_details"] = extract(bstr,"<dl class=\"list_vi\">","借款详情","<dd>","<div class=\"invest");
    {
            string tmp;
            string::size_type startpos = bstr.find("自动排名");
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
            while ((ivname = extract(tmp, "<tr>", "</td>", "<td>", "</td> ")) != "") {
                ivaccount = extract(tmp, "￥","<td class=", "￥","</td>");
                ivtime = extract(tmp, "￥", "￥", "<td>", "</td>");
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

    printstringmap(kv);
    if (kv["project_id"] == "" ) {
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
