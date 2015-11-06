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
    kv["site_id"] = "zhaocaibank";
    kv["project_name"] = extract(bstr,"<head>", "<meta http-equiv=", "<title>"," -");
    kv["borrower"] = extract(bstr,"<div class=","tan_info\">","借款人：","<br />");
    kv["project_id"] = extract(bstr,"<h1><div class=","<div class=","借款编号#","</div>");
    kv["borrowing_amount"] = extract(bstr,"<script type=","借款金额","￥","</strong></li");
    string::size_type pos = kv["borrowing_amount"].find("万");
    if (pos != string::npos){
        kv["borrowing_amount"] = doubletostring(atof(filternum(kv["borrowing_amount"]).c_str())*10000);
    } else{
        kv["borrowing_amount"] = doubletostring(atof(filternum(kv["borrowing_amount"]).c_str()));
    }  

    kv["annulized_rating"] = filternum(extract(bstr,"借款金额","年利率", "<u>", "%</u>"));
    kv["payment_method"] = extract(bstr,"</h1>","<ol class=","还款方式：","</li>");
    kv["loan_period"] = extract(bstr,"<ol class=", "</u></li>", "回报周期："," </li>");
    int pos1 = kv["loan_period"].find("月");
    if (pos1 != -1) {
        kv["loan_period"] = longtostring(atof(kv["loan_period"].c_str())*30);
    }
    else{

        kv["loan_period"] = longtostring(atof(kv["loan_period"].c_str()));
    }

    // kv["invested_amount"] = doubletostring(s_atod(kv["borrowing_amount"].c_str()) - s_atod(filternum(extract(bstr,"剩余时间","额","￥","")).c_str()));
      long long etime1 = stringtotime(extract(bstr,"<ol class=","</li>","审核时间：","</li>").c_str(), "%Y-%m-%d %H:%M:%S");
      if (etime1 > 1000000000) {
          kv["release_time"] = longtostring(etime1);
      }
    {
            string tmp;
            string::size_type startpos = bstr.find("投标时间");
            if (startpos != string::npos) {
                string::size_type endpos = bstr.find("</dl>", startpos);
                if (endpos != string::npos) {
                    tmp = bstr.substr(startpos, endpos - startpos);
                }
            }
            string ivname;
            string ivaccount;
            string ivtime;
            string retstr;
            while ((ivname = extract(tmp, "<span style=", "class=", "\">", "</span>")) != "") {
                ivaccount = extract(tmp, "%</span>", "元", "\">","元</span>");
                ivtime = extract(tmp, "元</span>", "元</span>", "\">", "</span>");
                ivtime = longtostring(stringtotime(ivtime.c_str(), "%Y-%m-%d %H:%M:%S")
                        );
                retstr += ivtime + "|" + ivname + "|" + ivaccount + "|";
                string::size_type pos = tmp.find("</dd>");
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
