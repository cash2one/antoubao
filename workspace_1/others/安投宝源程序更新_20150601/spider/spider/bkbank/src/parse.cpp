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
    kv["site_id"] = "bkbank";
    kv["borrower"] = extract(bstr, "<div class=\"detai-licont-divp\">", "<dt>", "","</dt>");
    kv["project_name"] = extract(bstr,"class=\"detai-plantit-a\">","","","</a>");
    kv["project_id"] = idstr;
    kv["borrowing_amount"] = num_util(extract(bstr, "<ul class=\"detai-with-ul\">", "￥","</span>","</p>"));
	kv["invested_amount"] = doubletostring(s_atod(kv["borrowing_amount"].c_str()) - s_atod(num_util(extract(bstr, "可投余额", "<p>", "\">", "</p>")).c_str()));

//	kv["release_time"] = longtostring(stringtotime(extract(bstr,"起投时间","：","","</div>").c_str(),"%Y-%m-%d %H:%M"));

    kv["annulized_rating"] = filternum(extract(bstr, "<ul class=\"detai-with-ul\">", "<p",">", "%"));
//    kv["payment_method"] = extract(bstr,"<a title=","\"","","\">");
    kv["loan_period"] = loanperiod_util(extract(bstr, "<ul class=\"detai-with-ul\">", "奖励", "<p class=\"detai-with-money\">","</p>"));

    {

		string retstr;

        string::size_type spos = bstr.find("投标时间");
        string::size_type epos = bstr.find("</div>",spos + 1);
        if (spos != string::npos && epos != string::npos) {
        string tmp = bstr.substr(spos, epos - spos);
		spos = tmp.find("</dt>");
		tmp = tmp.substr(spos);
        string ivname;
        string ivaccount;
        string ivtime;
        while ((ivname = extract(tmp, "<dd>", "\">", "", "</span>")) != "") {
			ivaccount = num_util(extract(tmp, "<span>", "", "","<em>"));
            ivtime = extract(tmp,"<span>", "<span>", "", "</span>");
            ivtime = longtostring(stringtotime(ivtime.c_str(), "%Y-%m-%d %H:%M"));
            retstr += ivtime + "|" + ivname + "|" + ivaccount + "|";
            string::size_type pos = tmp.find("</dd>");
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
