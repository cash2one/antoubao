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
    kv["site_id"] = "xiaoyoucai";
    kv["borrower"] = extract(bstr, "借款用途", "：", "</div>","<a");
    kv["project_name"] = extract(bstr,"<div class=\"pm_tit\">","<h3>","","</span>");
    kv["project_id"] = idstr;
	if(extract(bstr, "融资", "\">","","</span>") != "")
	{
		kv["borrowing_amount"] = num_util(extract(bstr, "融资", "\">","","</span>"));
		kv["loan_period"] = loanperiod_util(extract(bstr, "期限", "\">", "","</span>"));
	}
	if(extract(bstr, "转让债权", "<span class=\"ft28\">","","</span>") != "")
	{
		kv["borrowing_amount"] = num_util(extract(bstr, "转让债权", "<span class=\"ft28\">","","</span>"));
		kv["loan_period"] = loanperiod_util(extract(bstr, "借款期限", "class=\"ft28\">", "","</div>"));
	}
//	kv["release_time"] = longtostring(stringtotime(extract(bstr,"开标时间","<span","\">","</span>").c_str(),"%Y-%m-%d %H:%M:%S"));

    kv["annulized_rating"] = filternum(extract(bstr, "标的收益", "年化","", "%"));
    kv["payment_method"] = extract(bstr,"还款方式","<span>","","</span>");

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
            while ((ivname = extract(tmp, "name", ":\"", "", "\"")) != "") {
                ivaccount = extract(tmp, "amount", ":\"", "", "\"");
                ivtime = extract(tmp, "time", ":\"", "", "\"");
                ivtime = longtostring(stringtotime(ivtime.c_str(), "%Y-%m-%d %H:%M:%S"));
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
