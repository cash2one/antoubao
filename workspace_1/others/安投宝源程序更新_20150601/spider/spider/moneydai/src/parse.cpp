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
    kv["site_id"] = "moneydai";
    kv["borrower"] = extract(bstr, "借款方", "<div", "\">","</div>");
    kv["project_name"] = extract(bstr,"项目详情","class=\"dwsp1_1\">","","</div>");
    kv["project_id"] = idstr;
    kv["borrowing_amount"] = num_util(extract(bstr, "借款金额", "￥","","</span>"));

//	kv["release_time"] = longtostring(stringtotime(extract(bstr,"开始时间","\">","","</span>").c_str(),"%Y-%m-%d %H:%M:%S"));

    kv["annulized_rating"] = filternum(extract(bstr, "还款方式", "<font","\">", "%"));
	kv["payment_method"] = extract(bstr,"还款方式","&","\">","</div>");
    kv["loan_period"] = loanperiod_util(extract(bstr, "还款方式", "%", "\">","</div>"));

    {
        sprintf(filename, "html/%s.brec", idstr);
        buf = readfile(filename);
        size_t buflen = strlen(buf);
        char *p = buf;
        string retstr;
		string tmp;
        while (p < buf + buflen - 8) {
            int len;
            sscanf(p, "%08X", &len);
            p += 8;
            string jstr = string(p, len);
            p += len;
			Value json = stringtojson(jstr);
			if (!get_string_member(json, "msg", tmp))
			{
				continue;
			}


            //string::size_type spos = tmp.find("sta");
            //string::size_type epos = tmp.find("}",spos + 1);
            //if (spos == string::npos || epos == string::npos) {
              //  continue;
            //}
            //tmp = tmp.substr(spos, epos - spos);
			//spos = tmp.find("<div");
			//tmp = tmp.substr(spos);
            string ivname;
            string ivaccount;
            string ivtime;
            while ((ivname = extract(tmp, "<li class=\"zh_l_32\">", "", "", "</li>")) != "") {
                ivaccount = extract(tmp, "<li class=\"zh_l_33\">", "", "", "</li>");
                ivtime = extract(tmp, "<li class=\"zh_l_34\">", "", "", "</li>");
                ivtime = longtostring(stringtotime(ivtime.c_str(), "%Y-%m-%d %H:%M:%S"));
                retstr += ivtime + "|" + ivname + "|" + ivaccount + "|";
                string::size_type pos = tmp.find("</div>");
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
