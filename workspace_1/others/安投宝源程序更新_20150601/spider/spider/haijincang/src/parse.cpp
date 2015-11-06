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
    kv["site_id"] = "haijincang";
    kv["project_name"] = extract(bstr, "<head>", "<meta name=", "<title>","_");
  //  kv["borrower"] = extract(bstr,"<div class=\"top-l\">","<span class=","title=\"","");
    kv["project_id"] = extract(bstr,"<body>","<input type=","value=\"","\"/>");
    kv["borrowing_amount"] = extract(bstr,"借款期限","<li style=","￥","</span></p>");
    string::size_type pos = kv["borrowing_amount"].find("万");
    if (pos != string::npos){
        kv["borrowing_amount"] = doubletostring(atof(filternum(kv["borrowing_amount"]).c_str())*10000);
    } else{
        kv["borrowing_amount"] = doubletostring(atof(filternum(kv["borrowing_amount"]).c_str()));
    }  

    kv["annulized_rating"] = filternum(extract(bstr,"zq_l zq_l_c\">","<p><span class=", "font30\">", "</span>%</p>"));
    kv["payment_method"] = extract(bstr,"<div class=","date date_two\">","还款方式：","</span></p>");
    kv["loan_period"] = extract(bstr, "zq_l zq_l_c\">", "年化利率", "font30\">","</p>");
    int pos1 = kv["loan_period"].find("月");
    if (pos1 != -1) {
        kv["loan_period"] = longtostring(atof(kv["loan_period"].c_str())*30);
    }
    else{

        kv["loan_period"] = longtostring(atof(kv["loan_period"].c_str()));
    }

    {
            string tmp;
            string::size_type startpos = bstr.find("投资记录");
            if (startpos != string::npos) {
                string::size_type endpos = bstr.find("<div class=\"page page_s\">", startpos);
                if (endpos != string::npos) {
                    tmp = bstr.substr(startpos, endpos - startpos);
                }
            }
            string ivname;
            string ivaccount;
            string ivtime;
            string retstr;
            tmp = tmp.substr(tmp.find("投资时间") + 1);
            while ((ivname = extract(tmp, "", "<tr>", "<td>", "</td>")) != "") {
                ivaccount = extract(tmp, "</td>", "<td class=", "￥","</td>");
                ivtime = extract(tmp, "￥", "<td style=", "\">", "</td>");
                ivtime = longtostring(stringtotime(ivtime.c_str(), "%Y-%m-%d%H:%M:%S")
                        );
                retstr += ivtime + "|" + ivname + "|" + ivaccount + "|";
                string::size_type pos = tmp.find("size:12px;\">");
                if (pos != string::npos) {
                    tmp = tmp.substr(pos + 1);
            }
                else {
                   break;
            }
        }
      kv["investor"] = retstr;    
    }


    if (kv["loan_period"] == "" ) {
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
