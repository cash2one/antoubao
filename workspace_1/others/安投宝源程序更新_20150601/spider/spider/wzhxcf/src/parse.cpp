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
    kv["site_id"] = "wzhxcf";
    kv["borrower"] = extract(bstr, "<div class=\"jkxq-info\">", "<h3>", "","</h3>");
    kv["project_name"] = extract(bstr,"<div class=\"in-title\">","<h3","title=\"","\">");
    kv["project_id"] = idstr;
    kv["borrowing_amount"] = num_util(extract(bstr, "借款金额", "<span","<em>","</span>"));
	 kv["invested_amount"] = doubletostring(s_atod(kv["borrowing_amount"].c_str()) - s_atod(num_util(extract(bstr, "还差", "￥", "", "</p>")).c_str()));

	kv["release_time"] = longtostring(stringtotime(extract(bstr,"发标时间","<span",">","</span>").c_str(),"%Y-%m-%d %H:%M:%S"));

    kv["annulized_rating"] = filternum(extract(bstr, "年利率", "<span","<em>", "%"));
    kv["payment_method"] = extract(bstr,"还款方式","<span",">","</span>");
    kv["loan_period"] = loanperiod_util(extract(bstr, "借款期限", "</em>", "","</span>"));

    {



		sprintf(filename,"html/%s.brec",idstr);
		buf = readfile(filename);
		if (!buf)
		{
			return 1;
		}
		bstr = string(buf);
		free(buf);


		string retstr;

        string::size_type spos = bstr.find("投标时间");
        string::size_type epos = bstr.find("</table>",spos + 1);
        if (spos != string::npos && epos != string::npos) {
        string tmp = bstr.substr(spos + 1, epos - spos);
		spos = tmp.find("</tr>");
		tmp = tmp.substr(spos + 1);
        string ivname;
        string ivaccount;
        string ivtime;
        while ((ivname = extract(tmp, "<td", "<u>", "", "</u>")) != "") {
			ivaccount = num_util(extract(tmp, "￥", "", "","</td>"));
            ivtime = extract(tmp,"￥", "<td", "\">", "</td>");
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
