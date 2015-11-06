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
    kv["site_id"] = "cgtz";
//    kv["borrower"] = extract(bstr, "项目总额", "<p>", "","</p>");
    kv["project_name"] = extract(bstr,"<div class=\"infoD\">","<h1>","","</h1>");
    kv["project_id"] = idstr;
    kv["borrowing_amount"] = num_util(extract(bstr, "项目总额", "<p>","","</p>"));
	kv["invested_amount"] = doubletostring(s_atod(kv["borrowing_amount"].c_str()) - s_atod(num_util(extract(bstr, "可投金额", ">", "", "</li>")).c_str()));

//	kv["release_time"] = longtostring(stringtotime(extract(bstr,"开始时间","\">","","</span>").c_str(),"%Y-%m-%d %H:%M:%S"));

    kv["annulized_rating"] = filternum(extract(bstr, "年化收益率", "<p","\">", "%"));
	kv["payment_method"] = extract(bstr,"收益方式","</span>","","</p>");
    kv["loan_period"] = loanperiod_util(extract(bstr, "理财期限", "<p>", "","</p>"));
	if(s_atod(kv["loan_period"].c_str()) <= 0)
		kv.erase("loan_period");


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

            string::size_type spos = tmp.find("links-->");
            string::size_type epos = tmp.find("<!--links-->",spos + 1);
            if (spos == string::npos || epos == string::npos) {
                continue;
            }
            tmp = tmp.substr(spos, epos - spos);
			spos = tmp.find("<tr>");
			tmp = tmp.substr(spos);
            string ivname;
            string ivaccount;
            string ivtime;
            while ((ivname = extract(tmp, "<td>", "", "", "</td>")) != "") {
                ivaccount = extract(tmp, "</td>", "</td>", "<em>", "元");
                ivtime = extract(tmp, "元", "<td>", "", "</td>");
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
