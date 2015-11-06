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
       
    kv["site_id"] = "wjhz";
    //kv["borrower"] = "";               //无法注册，看不到借款人
    kv["project_name"] = extract(bstr, "class=\"ivDM_header clearfix\">", "ivD_loanStatus_container clearfix", "class=\"ivD_loanS_title orange\">","</h2>");
    kv["project_id"] = idstr;
    kv["borrowing_amount"] = num_util(extract(bstr, "id=\"ivD_info\">","借款金额：", "￥", "元"));
    kv["annulized_rating"] = extract(bstr, "id=\"ivD_info\"", "年利率：", "class=\"red\">", "%");
    kv["payment_method"] = extract(bstr, "id=\"ivD_info\">", "还款方式：", "", "</span>");
    kv["loan_period"] = loanperiod_util(extract(bstr, "id=\"ivD_info\"","借款期限：","","</span>"));
    //kv["release_time"] = "";
    kv["invested_amount"] = longtostring(s_atol(kv["borrowing_amount"].c_str()) - s_atol(filternum(extract(bstr,"class=\"ivD_progressing\"","class=\"fl lineH18\">","还差￥","</em>")).c_str())); 
    
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

            string::size_type spos = tmp.find("<tbody>");
            string::size_type epos = tmp.find("</table>");
            if (spos == string::npos || epos == string::npos) {
                continue;
            }
            tmp = tmp.substr(spos + 1, epos - spos - 1);
            string ivname;
            string ivaccount;
            string ivtime;
            while ((ivname = extract(tmp, "<tr>", "<td>", "", "</td>")) != "") {
                ivaccount = extract(tmp, "<td>", "</td>", "￥","</td>");
                ivtime = extract(tmp, "<td>", "<td>", "<td>", "</td>");
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
