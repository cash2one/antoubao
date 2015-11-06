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
    kv["site_id"] = "gzbfjr";
    kv["borrower"] = extract(bstr, "借款用途", "<span", "\">","</p>");
	if(kv["borrower"] == "")
		kv["borrower"] = extract(bstr, "借款描述", "</span>", "\">","</p>");
    kv["project_name"] = extract(bstr,"align=\"absmiddle\"","/>","","</h3>");
    kv["project_id"] = idstr;
    kv["borrowing_amount"] = num_util(extract(bstr, "借款金额", "id=\"count_money\">","","</em>"));

//	kv["release_time"] = longtostring(stringtotime(extract(bstr,"起投时间","：","","</div>").c_str(),"%Y-%m-%d %H:%M"));

    kv["annulized_rating"] = filternum(extract(bstr, "年利率", "<em","\">", "</em>"));
    kv["payment_method"] = extract(bstr,"还款方式","\">","","</span>");
    kv["loan_period"] = loanperiod_util(extract(bstr, "借款期限", "\">","<em>","</em>"));

    {

		string retstr;

        string::size_type spos = bstr.find("投标时间");
		string::size_type epos = bstr.find("</div>",spos + 1);
		if (spos != string::npos && epos != string::npos) {
        string tmp = bstr.substr(spos,epos - spos);
		spos = tmp.find("<li");
		tmp = tmp.substr(spos);
        string ivname;
        string ivaccount;
        string ivtime;
        while ((ivname = extract(tmp, "<span>", "", "", "</span>")) != "") {
			ivaccount = extract(tmp, "￥", "", "","</span>");
            ivtime = extract(tmp,"￥", "<span>", "", "</span>");
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
