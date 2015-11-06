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
    kv["site_id"] = "julend";
    kv["borrower"] = extract(bstr, "真实姓名", "<td", ">","</td>");
    kv["project_name"] = extract(bstr,"<span class=\"sf_con_wyjk_dq\">","","","</span>");
    kv["project_id"] = idstr;
    kv["borrowing_amount"] = num_util(extract(bstr, "借款总额", "<span",">","</span>"));
	kv["invested_amount"] = num_util(extract(bstr, "已投金额", "<td","\">","</td>"));

//	kv["release_time"] = longtostring(stringtotime(extract(bstr,"开始时间","\">","","</span>").c_str(),"%Y-%m-%d %H:%M:%S"));

    kv["annulized_rating"] = filternum(extract(bstr, "年利率", "<span","\">", "%"));
	kv["payment_method"] = extract(bstr,"还款方式","<td","\">","</td>");
    kv["loan_period"] = loanperiod_util(extract(bstr, "借款期限", "<td", "\">","</td>"));

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

            string::size_type spos = tmp.find("投标时间");
            string::size_type epos = tmp.find("</table>",spos + 1);
            if (spos == string::npos || epos == string::npos) {
                continue;
            }
            tmp = tmp.substr(spos, epos - spos);
			spos = tmp.find("</tr>");
			tmp = tmp.substr(spos + 1);
            string ivname;
            string ivaccount;
            string ivtime;
            while ((ivname = extract(tmp, "<td>", "<td>", "", "</td>")) != "") {
                ivaccount = num_util(extract(tmp, "<td>", "<td>", "<td>", "</td>"));
                ivtime = extract(tmp, "元", "<td>", "", "</td>");
				ivtime = longtostring(stringtotime(ivtime.c_str(), "%Y-%m-%d"));
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
