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
    kv["site_id"] = "kfxiong";
    kv["project_name"] = extract(bstr, "<head>", "<meta charset", "<title>"," - ");
    kv["borrower"] = extract(bstr,"<script type=","<ul class=","借款人：","</li>");
    kv["project_id"] = extract(bstr,"<em class="," <a href=","borrow_id=","\" target=");
    kv["borrowing_amount"] = extract(bstr,"款人","借款金额","￥","</li>");
    string::size_type pos = kv["borrowing_amount"].find("万");
    if (pos != string::npos){
        kv["borrowing_amount"] = doubletostring(atof(filternum(kv["borrowing_amount"]).c_str())*10000);
    } else{
        kv["borrowing_amount"] = doubletostring(atof(filternum(kv["borrowing_amount"]).c_str()));
    }  

    kv["annulized_rating"] = filternum(extract(bstr,"metasLi\">","年利率", "<em>", "%</em></strong>"));
    kv["payment_method"] = extract(bstr,"<script type=","<ul class=","还款方式：","</li>");
    kv["loan_period"] = extract(bstr, "<script type=", "<ul class=", "借款期限：","</li>");
    int pos1 = kv["loan_period"].find("月");
    if (pos1 != -1) {
        kv["loan_period"] = longtostring(atof(kv["loan_period"].c_str())*30);
    }
    else{

        kv["loan_period"] = longtostring(atof(kv["loan_period"].c_str()));
    }

    // kv["invested_amount"] = doubletostring(s_atod(kv["borrowing_amount"].c_str()) - s_atod(filternum(extract(bstr,"剩余时间","额","￥","")).c_str()));
     long long etime1 = stringtotime(extract(bstr,"</small>","metasLi\">","发标时间：","</li>").c_str(), "%Y-%m-%d %H:%M:%S");
     if (etime1 > 1000000000) {
         kv["release_time"] = longtostring(etime1);
     }
//    kv["project_details"] = extract(bstr,"role=\"tablist\">","借款详情","id=\"jkxq\">","<div class=\"bid_jkzl\">");
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
            while ((ivname = extract(tmp, "</td>", "<td><a href=", "\">", "</a></td>")) != "") {
                ivaccount = extract(tmp, "%</td>", "元</td>", "\">","元</td>");
                ivtime = extract(tmp, "元</td>", "元</td>", "\">", "</td>");
                ivtime = longtostring(stringtotime(ivtime.c_str(), "%Y-%m-%d %H:%M:%S"));
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
