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
    kv["site_id"] = "zsloan";
    kv["borrower"] = extract(bstr, "融资人档案", " href=\"userView", "\">","</a>");
    kv["project_name"] = extract(bstr,"借贷编号","</span>","","</div>");
    kv["project_id"] = idstr;
    kv["borrowing_amount"] = num_util(extract(bstr, "融资金额", "￥","","</span>"));

	kv["release_time"] = longtostring(stringtotime(extract(bstr,"发标时间","： ","","</td>").c_str(),"%Y-%m-%d %H:%M:%S"));

    kv["annulized_rating"] = filternum(extract(bstr, "融资年利率", "<span","\">", "%"));
    kv["payment_method"] = extract(bstr,"还款方式","： ","","</td>");
    kv["loan_period"] = loanperiod_util(extract(bstr, "融资期限", "\">", "","</span>"));

    {

		string retstr;

        string::size_type spos = bstr.find("投标人");
        string::size_type epos = bstr.find("常见问题");
        if (spos != string::npos && epos != string::npos) {
        string tmp = bstr.substr(spos + 1, epos - spos - 1);
		spos = tmp.find("</tr>");
		tmp = tmp.substr(spos + 1);
        string ivname;
        string ivaccount;
        string ivtime;
        while ((ivname = extract(tmp, "<a href=\"UserView", "\">", "", "</a>")) != "") {
			ivaccount = extract(tmp, "￥", "", "","</div>");
            ivtime = extract(tmp,"￥", "<div", "\">", "</div>");
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
