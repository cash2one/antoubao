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
    kv["site_id"] = "mgxtou";
    kv["borrower"] = extract(bstr, "<div class=\"main2\">", "<tr><td colspan=", "用户名：","</td></tr><tr>");
    kv["project_name"] = extract(bstr," />&nbsp","</table></div><div","><strong>","</strong>");
    kv["project_id"] = extract(bstr,"<div class=\"main2\">","class=\"jkxq_bh","借款编号：","</td></tr><tr>");
    kv["borrowing_amount"] = extract(bstr,"><table width=","额：","￥","</span><img");
    string::size_type pos = kv["borrowing_amount"].find("万");
    if (pos != string::npos){
        kv["borrowing_amount"] = doubletostring(atof(filternum(kv["borrowing_amount"]).c_str())*10000);
    } else{
        kv["borrowing_amount"] = doubletostring(atof(filternum(kv["borrowing_amount"]).c_str()));
    }  

    kv["annulized_rating"] = filternum(extract(bstr,"<div class=\"jkxq_grnr\">","<td width=\"273\" align=\"left\">", "年利率：", "%</td><td align="));
    kv["payment_method"] = extract(bstr,"</td></tr><tr><td align","</td><td align=","还款方式：","</td></tr></table>");
    kv["loan_period"] = extract(bstr, "<span class=", "</td><td align=", "借款期限:","</td><td><input name");
    int pos1 = kv["loan_period"].find("月");
    if (pos1 != -1) {
        kv["loan_period"] = longtostring(atof(kv["loan_period"].c_str())*30);
    }
    else{

        kv["loan_period"] = longtostring(atof(kv["loan_period"].c_str()));
    }

    // kv["invested_amount"] = doubletostring(s_atod(kv["borrowing_amount"].c_str()) - s_atod(filternum(extract(bstr,"剩余时间","额","￥","")).c_str()));
   long long etime1 = stringtotime(extract(bstr,"</td></tr><tr><td>","</td></tr><tr><td>","审核时间：","</td>").c_str(), "%Y-%m-%d %H:%M:%S");
   if (etime1 > 1000000000) {
       kv["release_time"] = longtostring(etime1);
   }
    //     kv["end_time"] = extract(bstr,"<ul class=\"d_date\">","<s>","满标时间：","</li>");  
//    kv["project_details"] = extract(bstr,"role=\"tablist\">","借款详情","id=\"jkxq\">","<div class=\"bid_jkzl\">");
    {
            string tmp;
            string::size_type startpos = bstr.find("投标状态");
            if (startpos != string::npos) {
                string::size_type endpos = bstr.find("</table></div><div id=", startpos);
                if (endpos != string::npos) {
                    tmp = bstr.substr(startpos, endpos - startpos);
                }
            }
            string ivname;
            string ivaccount;
            string ivtime;
            string retstr;
            tmp = tmp.substr(tmp.find("</td></tr><tr>") + 1);
            while ((ivname = extract(tmp, "<td", "class=", "xxk1_bgnr\">", "</td><td class")) != "") {
                ivaccount = extract(tmp, "id=\"tbje\">", "</td><td class=", "id=\"yxje\">￥","元</td><td");
                ivtime = extract(tmp, "元</td><td", "%</td><td", "xxk1_bgnr\">", "</td><td class=");
                ivtime = longtostring(stringtotime(ivtime.c_str(), "%Y-%m-%d %H:%M:%S")
                        );
                retstr += ivtime + "|" + ivname + "|" + ivaccount + "|";
                string::size_type pos = tmp.find("</td></tr><tr>");
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
