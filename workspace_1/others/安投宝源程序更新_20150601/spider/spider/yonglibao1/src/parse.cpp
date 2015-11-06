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
    kv["site_id"] = "yonglibao";
    kv["borrower"] = extract(bstr, "借款人信息", "div class=\"pd_content1\">", "","</div>");
    kv["project_name"] = extract(bstr,"<div class=\"pd_title\">","<h2 >","","<");
    kv["project_id"] = idstr;
    kv["borrowing_amount"] = num_util(extract(bstr, "投资金额", "<strong>","","</div>"));

//	kv["release_time"] = longtostring(stringtotime(extract(bstr,"起投时间","：","","</div>").c_str(),"%Y-%m-%d %H:%M"));

    kv["annulized_rating"] = filternum(extract(bstr, "年化收益", "<strong>","", "%"));
    kv["payment_method"] = extract(bstr,"还款方式","","","<");
    kv["loan_period"] = loanperiod_util(extract(bstr, "投资期限", "<strong>", "","</div>"));

    {

		string retstr;

        string::size_type spos = bstr.find("流转标样式");
        string::size_type epos = bstr.find("流转标样式",spos + 1);
        if (spos != string::npos && epos != string::npos) {
        string tmp = bstr.substr(spos , epos - spos );
		spos = tmp.find("投标人");
		tmp = tmp.substr(spos + 1);
		spos = tmp.find("投标人");
		tmp = tmp.substr(spos + 1);
		spos = tmp.find("</li>");
		tmp = tmp.substr(spos + 1);
        string ivname;
        string ivaccount;
		time_t ivtimep;
        string ivtime;
        while ((ivname = extract(tmp, "<span", "\">", "", "</span>")) != "") {
			ivaccount = extract(tmp, "天", "<span", "\">","</span>");
			time(&ivtimep);
            ivtime = longtostring(ivtimep);
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
