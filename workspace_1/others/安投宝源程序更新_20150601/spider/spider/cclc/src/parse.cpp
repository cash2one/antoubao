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
    kv["site_id"] = "cclc";
    kv["borrower"] = extract(bstr, "", "", "","<");
    kv["project_name"] = extract(bstr,"<div class=\"info_left_title\">","<div","\">","</div>");
    kv["project_id"] = idstr;
    kv["borrowing_amount"] = num_util(extract(bstr, "产品金额", "<span>","","</h2>"));
	kv["invested_amount"] = doubletostring(s_atod(kv["borrowing_amount"].c_str()) - s_atod(num_util(extract(bstr, "class=\"info_right_money_line\">", "剩余", "\">", "<")).c_str()));

	kv["release_time"] = longtostring(stringtotime(extract(bstr,"开始时间","\">","","</span>").c_str(),"%Y-%m-%d %H:%M:%S"));

    kv["annulized_rating"] = filternum(extract(bstr, "预期年化", "<span","\">", "%"));
	kv["payment_method"] = extract(bstr,"还款方式","<span","\">","</span>");
    kv["loan_period"] = loanperiod_util(extract(bstr, "理财期限", "<span>", "","</h2>"));

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

            string::size_type spos = tmp.find("total");
            string::size_type epos = tmp.find("pageno",spos + 1);
            if (spos == string::npos || epos == string::npos) {
                continue;
            }
            tmp = tmp.substr(spos, epos - spos);
			spos = tmp.find("list");
			tmp = tmp.substr(spos);
            string ivname;
            string ivaccount;
            string ivtime;
            while ((ivname = extract(tmp, "mobile", "\":", "\"", "\"")) != "") {
                ivaccount = extract(tmp, "amount", "\":", "", ",");
                ivtime = extract(tmp, "lastupdated", "\":", "", ",");
 //               ivtime = longtostring(stringtotime(ivtime.c_str(), "%Y-%m-%d %H:%M:%S"));
                ivtime = longtostring(s_atod(ivtime.c_str()) / 1000);
                retstr += ivtime + "|" + ivname + "|" + ivaccount + "|";
                string::size_type pos = tmp.find("}");
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
