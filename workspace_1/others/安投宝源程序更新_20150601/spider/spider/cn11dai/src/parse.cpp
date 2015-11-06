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
    kv["site_id"] = "cn11dai";
    kv["borrower"] = extract(bstr, "<div class=\"box-info-user\">", "<p", "\">","</p>") + "_" + extract(bstr, "站内关联用户名",
			"：", "","</p>");
    kv["project_name"] = extract(bstr,"<span class=\"box-info-detail-title\">","","","</span>");
    kv["project_id"] = idstr;
    kv["borrowing_amount"] = num_util(extract(bstr, "<ul class=\"clearfix ullist-invest\">", "￥","","</li>"));

//	kv["release_time"] = longtostring(stringtotime(extract(bstr,"起投时间","：","","</div>").c_str(),"%Y-%m-%d %H:%M"));

    kv["annulized_rating"] = filternum(extract(bstr, "<ul class=\"clearfix ullist-invest\">", "<li>","<li>", "%"));
//	kv["payment_method"] = extract(bstr,"<div class=\"h1_next\">","<span>","<span>","</span>");
    kv["loan_period"] = loanperiod_util(extract(bstr, "<ul class=\"clearfix ullist-invest\">", "%", "\">","</span>"));

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

            string::size_type spos = tmp.find("data");
            string::size_type epos = tmp.find("page",spos + 1);
            if (spos == string::npos || epos == string::npos) {
                continue;
            }
            tmp = tmp.substr(spos, epos - spos);
			spos = tmp.find("list");
			tmp = tmp.substr(spos);
            string ivname;
            string ivaccount;
            string ivtime;
            while ((ivname = extract(tmp, "username", ":\"", "", "\"")) != "") {
                ivaccount = extract(tmp, "money", ":\"", "", "\"");
                ivtime = extract(tmp, "addtime", ":\"", "", "\"");
//                ivtime = longtostring(stringtotime(ivtime.c_str(), "%Y-%m-%d %H:%M:%S"));
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
