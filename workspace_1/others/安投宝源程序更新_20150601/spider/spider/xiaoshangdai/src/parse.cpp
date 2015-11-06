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
    kv["site_id"] = "xiaoshangdai";
	kv["borrower"] = extract(bstr, "", "", "","<") + "_" + extract(bstr, "站内关联用户名", "：", "","</p>");
    kv["project_name"] = extract(bstr,"<div class=\"loanbid\">","class=\"span\">","","</span>");
    kv["project_id"] = idstr;
    kv["borrowing_amount"] = num_util(extract(bstr, "<div class=\"loanbox\">", "¥","","</span>"));

//	kv["release_time"] = longtostring(stringtotime(extract(bstr,"起投时间","：","","</div>").c_str(),"%Y-%m-%d %H:%M"));

    kv["annulized_rating"] = extract(bstr, "借款金额", "<span>","", "</span>");
	if(kv["annulized_rating"].find("日"))
		kv["annulized_rating"] = doubletostring(s_atod(filternum(kv["annulized_rating"]).c_str()) * 365);
	else if(kv["annulized_rating"].find("月"))
		kv["annulized_rating"] = doubletostring(s_atod(filternum(kv["annulized_rating"]).c_str()) * 12);
	else
		 kv["annulized_rating"] = filternum(kv["annulized_rating"]);
    kv["payment_method"] = extract(bstr,"还款方式","<td>","","</td>");
    kv["loan_period"] = loanperiod_util(extract(bstr, "利率", "<span>", "<span>","</span>"));

    {

		string retstr;

        string::size_type spos = bstr.find("投标类型");
		if(spos != string::npos)
			spos = bstr.find("<tr>",spos + 1);
        if (spos != string::npos) {
        string tmp = bstr.substr(spos);
        string ivname;
        string ivaccount;
        string ivtime;
        while ((ivname = extract(tmp, "<td", "\">", "", "</td>")) != "") {
			ivaccount = extract(tmp, "<td", "<td", "\">","元");
            ivtime = extract(tmp,"元", "<td", "\">", "</td>");
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
