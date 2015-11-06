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
    kv["site_id"] = "gxyclub";
    kv["borrower"] = extract(bstr,"用户名","：","<strong>","</strong></td>");
    kv["project_name"] = extract(bstr,"<td valign=\"top\"","<table width=","size=\"5\">","</font></td>");
    kv["project_id"] = extract(bstr," class=\"banner_line\">","<input type=\"hidden","value=\"","\"/>");
    kv["borrowing_amount"] = filternum(extract(bstr, "<td style=","借款金额","￥","</font></td>"));
    kv["annulized_rating"] = filternum(extract(bstr, "￥", "年化利率", "display:block\">", "%"));
 //   kv["payment_method"] = extract(bstr,"保障方式","还款方式","\">","");
    kv["loan_period"] = extract(bstr, "化利率", "借款期限", "block\">","</font></font></td>");
    if (extract(bstr, "化利率", "借款期限", "block\">","</font></font></td>").find("月") != string::npos) {
        kv["loan_period"] = doubletostring(atof(kv["loan_period"].c_str())*30); 
    }
    kv["invested_amount"] = longtostring(s_atol(kv["borrowing_amount"].c_str()) - s_atol(filternum(extract(bstr,"剩余金额","￥","#b40519\">","</font></td>")).c_str()));
    {
        string::size_type spos = bstr.find("投资时间");
        if (spos != string::npos) {
            string tmp= bstr.substr(spos + 1);;
            string ivname;
            string ivaccount;
            string ivtime;
            string retstr;
            int invnum = 0;
            tmp = tmp.substr(tmp.find("</tr>") + 1);
            while ((ivname = extract(tmp, "</td>", "<td align=", "name\">", "</td>")) != "") {
                ivaccount = extract(tmp, "", "class=\"fred\">", "￥","</td>");
                ivtime = extract(tmp,"name\">","fred\">","align=\"center\">","</td>");
                ivtime = longtostring(stringtotime(ivtime.c_str(), "%Y-%m-%d %H:%M:%S"));
                retstr += ivtime + "|" + ivname + "|" + ivaccount + "|";
                invnum++;
                spos = tmp.find("</tr>");
                if (spos == string::npos) {
                    break;
                }
                tmp = tmp.substr(spos+1);
            }
            kv["investor"] = retstr;
        }
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
