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
    kv["site_id"] = "cqhrdai";
    kv["borrower"] = extract(bstr, "项目信息", "投资接受人", "</th>","</td>");
    kv["project_name"] = extract(bstr,"<div class=\"title blue\">","</p>","","</div>");
    kv["project_id"] = idstr;
    kv["borrowing_amount"] = num_util(extract(bstr, "融资金额", "￥","","</td>"));
//	kv["invested_amount"] = doubletostring(s_tod(kv["borrowing_amount"].c_str()) - s_tod(extract(bstr, "可投金额", "￥","","</p>").c_str()));
	kv["invested_amount"] = num_util(extract(bstr, "已投金额", "￥","","</td>"));

//	kv["release_time"] = longtostring(stringtotime(extract(bstr,"起投时间","：","","</div>").c_str(),"%Y-%m-%d %H:%M"));

    kv["annulized_rating"] = filternum(extract(bstr, "项目信息", "年化收益率","<td>", "%"));
    kv["payment_method"] = extract(bstr,"兑付方式","￥","<td>","</td>");
    kv["loan_period"] = loanperiod_util(extract(bstr,"项目信息","借款期限","<td>","</td>"));

    {

		string retstr;

        string::size_type spos = bstr.find("投资时间");
        string::size_type epos = bstr.find("</table>",spos + 1);
        if (spos != string::npos && epos != string::npos) {
        string tmp = bstr.substr(spos + 1, epos - spos);
		spos = tmp.find("</tr>");
		tmp = tmp.substr(spos + 1);
        string ivname;
        string ivaccount;
        string ivtime;
        while ((ivname = extract(tmp, "<td", "<td>", "", "</td>")) != "") {
			ivaccount = extract(tmp, "</td>", "￥", "","</td>");
            ivtime = extract(tmp,"￥", "<td>", "", "</td>");
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
