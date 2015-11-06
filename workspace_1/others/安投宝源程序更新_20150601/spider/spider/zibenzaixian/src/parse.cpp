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
    kv["site_id"] = "zibenzaixian";
    kv["project_name"] = extract(bstr, "<head>", "<meta http-equiv=", "<title>","</title>");
    kv["borrower"] = extract(bstr,"<img src=","</dt>","发布者：","</dd>");
    kv["project_id"] = extract(bstr,"<label class=","<label class=","标号：","</label>");
    kv["borrowing_amount"] = extract(bstr,"\"jine_tb\">","<label>","￥","</font></label>");
    string::size_type pos = kv["borrowing_amount"].find("万");
    if (pos != string::npos){
        kv["borrowing_amount"] = doubletostring(atof(filternum(kv["borrowing_amount"]).c_str())*10000);
    } else{
        kv["borrowing_amount"] = doubletostring(atof(filternum(kv["borrowing_amount"]).c_str()));
    }  

    kv["annulized_rating"] = filternum(extract(bstr,"\"li2 kd1\">","年利率", "\">", "<font>%</font>"));
    kv["payment_method"] = extract(bstr,"</span><label","还款方式","\">","</font> </span>");
    kv["loan_period"] = extract(bstr, "\"li2 kd2\">", "期限", "\">","</font>");
    int pos1 = kv["loan_period"].find("月");
    if (pos1 != -1) {
        kv["loan_period"] = longtostring(atof(kv["loan_period"].c_str())*30);
    }
    else{

        kv["loan_period"] = longtostring(atof(kv["loan_period"].c_str()));
    }

   long long etime1 = stringtotime(extract(bstr,"<div class=","发标时间","\">","</font></div>").c_str(), "%Y-%m-%d %H:%M:%S");
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
            while ((ivname = extract(tmp, "", "<tr>", "<td>", "</td>")) != "") {
                ivaccount = extract(tmp, "% </td>", "￥", "￥","</td>");
                ivtime = extract(tmp, "￥", "￥", "<td>", "</td>");
                ivtime = longtostring(stringtotime(ivtime.c_str(), "%Y-%m-%d %H:%M")
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
