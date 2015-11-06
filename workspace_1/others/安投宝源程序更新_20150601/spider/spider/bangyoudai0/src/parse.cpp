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
	kv["type"] = "1";
    kv["site_id"] = "bangyoudai";
//    kv["borrower"] = extract(bstr, "用户信息", "</span>", "\">","</span>");
    kv["project_name"] = extract(bstr,"<div class=\"detail_title f_l\">","","","</span>");
    kv["project_id"] = idstr;
    kv["borrowing_amount"] = num_util(extract(bstr, "计划金额", "￥","","</span>"));
    kv["invested_amount"] = doubletostring(s_atod(kv["borrowing_amount"].c_str()) - s_atod(num_util(extract(bstr, "剩余金额", "￥", "", "<")).c_str()));
	if(bstr.find("开始时间") != string::npos)
	{
		kv["release_time"] = longtostring(stringtotime(extract(bstr,"开始时间",">","","</span>").c_str(),"%Y年%m月%d日"));
	}

    kv["annulized_rating"] = filternum(extract(bstr, "预期年化收益", "<span","\">", "%"));
//    kv["payment_method"] = extract(bstr,"还款方式","<em>","","</em>");
    kv["loan_period"] = loanperiod_util(extract(bstr, "锁定期限", "<span", "\">","</span>"));

    {

		string retstr;

        string::size_type spos = bstr.find("购买人");
		string::size_type epos = bstr.find("</tbody>",spos + 1);
        if (spos != string::npos && epos != string::npos) {
        string tmp = bstr.substr(spos + 1,epos - spos);
		spos = tmp.find("</tr>");
		if (spos != string::npos)
		{
		tmp = tmp.substr(spos + 1);
        string ivname;
        string ivaccount;
        string ivtime;
        while ((ivname = extract(tmp, "<td", "<span", "\">", "</span>")) != "") {
			ivaccount = num_util(extract(tmp, "￥", "", "","</td>"));
            ivtime = extract(tmp,"￥", "<td", ">", "</td>");
            ivtime = longtostring(stringtotime(ivtime.c_str(), "%Y-%m-%d %H:%M"));
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
