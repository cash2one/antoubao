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
    kv["site_id"] = "365edai";
    kv["borrower"] = extract(bstr, "列表号", "#", "\">","</span>");
    kv["project_name"] = extract(bstr,"<span id=\"lab_jkbt\">","","","<span");
    kv["project_id"] = idstr;
    kv["borrowing_amount"] = num_util(extract(bstr, "借款金额", "¥","\">","</span>"));

	kv["release_time"] = longtostring(stringtotime(extract(bstr,"发标日期","\">","","</span>").c_str(),"%Y-%m-%d %H:%M:%S"));

    kv["annulized_rating"] = filternum(extract(bstr, "借款年利率", "\">","", "%"));
    kv["payment_method"] = extract(bstr,"还款方式","\">","","</span>");
    kv["loan_period"] = loanperiod_util(extract(bstr, "借款期限", "\">", "","</li>"));

    {

		string retstr;

        string::size_type spos = bstr.find("投标时间");
        string::size_type epos = bstr.find("留言板");
        if (spos != string::npos && epos != string::npos) {
        string tmp = bstr.substr(spos + 1, epos - spos - 1);
		spos = tmp.find("</tr>");
		tmp = tmp.substr(spos + 1);
        string ivname;
        string ivaccount;
        string ivtime;
        while ((ivname = extract(tmp, "<td>", "", "", "&")) != "") {
			string::size_type pos = tmp.find("&");
			if(pos != string::npos)
			{
				tmp = tmp.substr(pos + 1);
				pos = tmp.find("</td>");
				if(pos != string::npos)
				{
					tmp = tmp.substr(pos + 1);
					ivaccount = extract(tmp, "</td>", "</td>", "\">","</td>");
					ivtime = extract(tmp,"动", "</td>", "\">", "</td>");
					ivtime = longtostring(stringtotime(ivtime.c_str(), "%Y-%m-%d %H:%M:%S"));
					retstr += ivtime + "|" + ivname + "|" + ivaccount + "|";
				}
			}
            pos = tmp.find("</tr>");
            if (pos != string::npos) {
				tmp = tmp.substr(pos + 1);
			}
			else {
                break;
			}
			}
			}
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
