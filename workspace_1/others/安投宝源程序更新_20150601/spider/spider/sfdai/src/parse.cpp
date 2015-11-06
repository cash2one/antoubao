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
    kv["site_id"] = "sfdai";
    kv["borrower"] = extract(bstr, "借款人信息", "借款人", "<i>","</i>");
    kv["project_name"] = extract(bstr,"<tr class=\"tit\">","</a>","","</td>");
    kv["project_id"] = idstr;
    kv["borrowing_amount"] = num_util(extract(bstr, "项目总额", "<tr","<td>","</td>"));

	kv["release_time"] = longtostring(stringtotime(extract(bstr,"成立日期","</b>","","</li>").c_str(),"%Y-%m-%d %H:%M:%S"));

    kv["annulized_rating"] = filternum(extract(bstr, "<tr class=\"redfont\">", "</td>","</td>", "%"));
    kv["payment_method"] = extract(bstr,"还款方式","<b>","","</b>");
    kv["loan_period"] = loanperiod_util(extract(bstr, "<tr class=\"redfont\">", "<td>", "<td>","</td>"));

    {

		string retstr;

        string::size_type spos = bstr.find("投标方式");
        string::size_type epos = bstr.find("</div>",spos + 1);
        if (spos != string::npos && epos != string::npos) {
        string tmp = bstr.substr(spos, epos - spos);
		spos = tmp.find("<ul");
		tmp = tmp.substr(spos);
        string ivname;
        string ivaccount;
        string ivtime;
        while ((ivname = extract(tmp, "<dd", "<dd", ">", "</dd>")) != "") {
			ivaccount = extract(tmp, "<dd", "￥", "￥","</dd>");
            ivtime = extract(tmp,"￥", "<dd class=\"d3\">", "", "</dd>");
            ivtime = longtostring(stringtotime(ivtime.c_str(), "%Y-%m-%d %H:%M:%S"));
            retstr += ivtime + "|" + ivname + "|" + ivaccount + "|";
            string::size_type pos = tmp.find("</li>");
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
