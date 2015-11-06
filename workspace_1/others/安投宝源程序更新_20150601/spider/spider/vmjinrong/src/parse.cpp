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
    kv["site_id"] = "vmjinrong";
    kv["project_name"] = extract(bstr, "<meta name=", "<meta http-equiv=", "<title>","_");
    kv["borrower"] = extract(bstr,"<div class=\"f-fl\">","<span id=\"li","\">","</span>");
    kv["project_id"] = extract(bstr,"var geteway = ","var data =","ProjectId:",",");
    kv["borrowing_amount"] = extract(bstr,"<div class=\"data\">","金额","&#165;","</p>");
    string::size_type pos = kv["borrowing_amount"].find("万");
    if (pos != string::npos){
        kv["borrowing_amount"] = doubletostring(atof(filternum(kv["borrowing_amount"]).c_str())*10000);
    } else{
        kv["borrowing_amount"] = doubletostring(atof(filternum(kv["borrowing_amount"]).c_str()));
    }  

    kv["annulized_rating"] = filternum(extract(bstr,"class=\"f-fr\">","年利率", "count\">", "%</p>"));
  //  kv["payment_method"] = extract(bstr,"<li class=\"none_b\">","还款方式","\">","");
    kv["loan_period"] = extract(bstr, "%</p>", "期限", "count\">","</p>");
    int pos1 = kv["loan_period"].find("月");
    if (pos1 != -1) {
        kv["loan_period"] = longtostring(atof(kv["loan_period"].c_str())*30);
    }
    else{

        kv["loan_period"] = longtostring(atof(kv["loan_period"].c_str()));
    }

     kv["invested_amount"] = doubletostring(s_atod(kv["borrowing_amount"].c_str()) - s_atod(filternum(extract(bstr,"%</span>","可投金额","&#165;","</span>")).c_str()));
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
            while ((ivname = extract(tmp, "<tr>", "</td>", "<td>", "</td>")) != "") {
                ivaccount = extract(tmp, "</td>", "</td>", "&#165;","</td>");
                ivtime = extract(tmp, "&#165;", "</td>", "<td>", "</td>");
                ivtime = longtostring(stringtotime(ivtime.c_str(), "%Y/%m/%d %H:%M:%S")
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
