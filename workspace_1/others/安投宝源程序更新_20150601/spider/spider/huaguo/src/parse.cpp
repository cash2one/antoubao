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
    kv["site_id"] = "huaguo";
    kv["project_name"] = extract(bstr, "<head>", "<meta http-equiv=", "<title>","-");
//    kv["borrower"] = extract(bstr,"<td class=\"t1 tt1\">","借款人","：","</p>");
   // kv["project_id"] = extract(bstr,"pro-con-h2\">","<form action=","value=\"","");
    kv["borrowing_amount"] = extract(bstr,"融资总额","<tr ><td height=","px\">","</span></td>");
    string::size_type pos = kv["borrowing_amount"].find("万");
    if (pos != string::npos){
        kv["borrowing_amount"] = doubletostring(atof(filternum(kv["borrowing_amount"]).c_str())*10000);
    } else{
        kv["borrowing_amount"] = doubletostring(atof(filternum(kv["borrowing_amount"]).c_str()));
    }  

    kv["annulized_rating"] = filternum(extract(bstr,"年化利率","class=\"c51c22", "\">", "%</span>"));
    kv["payment_method"] = extract(bstr,"<tr><td  height","还款方式","\">","</td></tr>");
    kv["loan_period"] = extract(bstr, "投资周期", "%</span>", "\">","</span></td>");
    int pos1 = kv["loan_period"].find("月");
    if (pos1 != -1) {
        kv["loan_period"] = longtostring(atof(kv["loan_period"].c_str())*30);
    }
    else{

        kv["loan_period"] = longtostring(atof(kv["loan_period"].c_str()));
    }

     kv["invested_amount"] = doubletostring(s_atod(kv["borrowing_amount"].c_str()) - s_atod(filternum(extract(bstr,"可投金额","</span></td><td><span","\">","</span></td>")).c_str()));
    {
            string tmp;
            string::size_type startpos = bstr.find("投资记录");
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
            tmp = tmp.substr(tmp.find("<tr>") + 1);
            while ((ivname = extract(tmp, "", "", "<td>", "</td>")) != "") {
                ivaccount = extract(tmp, "</td>", "<td class=", "\">","元</td>");
                ivtime = extract(tmp, "</td>", "元</td>", "\">", "</td></tr>");
                ivtime = longtostring(stringtotime(ivtime.c_str(), "%m-%d %H:%M:%S")
                        );
                retstr += ivtime + "|" + ivname + "|" + ivaccount + "|";
                string::size_type pos = tmp.find("<tr>");
                if (pos != string::npos) {
                    tmp = tmp.substr(pos + 1);
                }
                else {
                   break;
            }
        }
      kv["investor"] = retstr;    
    }


    if (kv["annulized_rating"] == "" ) {
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
