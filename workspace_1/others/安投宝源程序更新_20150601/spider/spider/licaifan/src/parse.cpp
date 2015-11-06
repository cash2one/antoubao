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
    kv["site_id"] = "licaifan";
    kv["borrower"] = extract(bstr,"姓名","><span style=","\">","</span></td>");
    kv["project_name"] = extract(bstr,"<meta property=","<meta name=","<title>","- ");
    kv["project_id"] = extract(bstr,"recharge-wrap\">","<form action=","detail/","\" method=");
    kv["borrowing_amount"] = extract(bstr, "<p class=\"date\">","bg-wrap3\">","detail-sprite\">","</span></div>");
    string::size_type pos = kv["borrowing_amount"].find("万");
    if (pos != string::npos){
         kv["borrowing_amount"] = doubletostring(atof(filternum(kv["borrowing_amount"]).c_str())*10000);
    } else{
         kv["borrowing_amount"] = doubletostring(atof(filternum(kv["borrowing_amount"]).c_str()));
    }
    kv["annulized_rating"] = filternum(extract(bstr, "main-msg clear\">", "<li class=\"bg-wrap1\">", "detail-sprite\">", "<span>%</span>"));
    kv["payment_method"] = extract(bstr,"sec-msg clear\">","bg-wrap1\">","</em><span>","</span></li>");
    kv["loan_period"] = extract(bstr, "<span>%</span>", "bg-wrap2\">", "\">","</span></div>");
    int pos1 = kv["loan_period"].find("月");
    if (pos1 != -1) {
        kv["loan_period"] = longtostring(atof(kv["loan_period"].c_str())*30);
    }
    else{
        kv["loan_period"] = longtostring(atof(kv["loan_period"].c_str()));
    }
    kv["invested_amount"] = longtostring(s_atol(kv["borrowing_amount"].c_str()) - s_atol(filternum(extract(bstr,"可投金额","：","元","</li>")).c_str()));
 {
        sprintf(filename, "html/%s.brec", idstr);
        buf = readfile(filename);
        size_t buflen = strlen(buf);
        char *p = buf;
        string retstr;
        while (p < buf + buflen - 8) {
            int len;
            sscanf(p, "%08X", &len);
            p += 8;
            string tmp = string(p, len);
            p += len;

            string::size_type spos = tmp.find("状态");
            string::size_type epos = tmp.find("</table>");
            if (spos == string::npos || epos == string::npos) {
                continue;
            }
            tmp = tmp.substr(spos + 1, epos - spos - 1);
            string ivname;
            string ivaccount;
            string ivtime;
            tmp = tmp.substr(tmp.find("</tr>") + 1);
            while ((ivname = extract(tmp, "first-td", "detail-sprite", "</td><td><span>", " <")) != "") {
                ivaccount = extract(tmp, "detail-sprite", "</td><td><span>", "</span></td><td>","元</td><td>");
                ivtime = extract(tmp, "</td><td><span>", "</span></td><td>", "元</td><td>", "</td><td>");
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
        }
        free(buf);
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
    
    
