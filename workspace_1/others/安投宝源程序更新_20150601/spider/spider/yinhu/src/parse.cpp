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
    kv["site_id"] = "yinhu";
    kv["borrower"] = extract(bstr, "<div class=\"da_dl\">", "<dt>", "<dd>","</dd>");
    kv["project_name"] = extract(bstr,"<h3 class=\"p_stl3\">","</strong>","","</h3>");
    kv["project_id"] = idstr;
    kv["borrowing_amount"] = num_util(extract(bstr, "本期借款总额", "￥","","</td>"));

//	kv["release_time"] = longtostring(stringtotime(extract(bstr,"开始时间","\">","","</span>").c_str(),"%Y-%m-%d %H:%M:%S"));

    kv["annulized_rating"] = filternum(extract(bstr, "年化利率", "￥","tx_stl3\">", "%"));
	kv["payment_method"] = extract(bstr,"还款方式","<dd>","","</dd>");
    kv["loan_period"] = loanperiod_util(extract(bstr, "投资周期", "%", "tx_stl3\">","</td>"));

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

            string ivname;
            string ivaccount;
            string ivtime;
            while ((ivname = extract(tmp, "<td>", "<td>", "", "</td>")) != "") {
                ivaccount = extract(tmp, "<td>", "<td>", "<td>", "</td>");
                ivtime = extract(tmp, ".", "<td>", "<td>", "</td>");
				ivtime = longtostring(stringtotime(ivtime.c_str(), "%Y-%m-%d %H:%M"));
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
