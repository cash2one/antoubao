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
    kv["site_id"] = "wdw88";
    kv["borrower"] = extract(bstr, "借款人信息", "<div>", "","</div>");
    kv["project_name"] = extract(bstr,"编号","：","<strong>","</strong>");
    kv["project_id"] = idstr;
    kv["borrowing_amount"] = num_util(extract(bstr, "年化收益率", "<li","<span>","</span>"));

//	kv["release_time"] = longtostring(stringtotime(extract(bstr,"开标时间","<span","\">","</span>").c_str(),"%Y-%m-%d %H:%M:%S"));

    kv["annulized_rating"] = filternum(extract(bstr, "<span id=\"yearRate", "\">","", "%"));
//    kv["payment_method"] = extract(bstr,"还款方式","<span","\">","</span>");
    kv["loan_period"] = longtostring((stringtotime(extract(bstr,"债权赎回日期","<span","\">","</span>").c_str(), "%Y-%m-%d") - stringtotime(extract(bstr,"投标截止时间","<span","\">","</span>").c_str(), "%Y-%m-%d %H:%M")) / 86400) ;
	
{
        sprintf(filename, "html/%s.brec", idstr);
        buf = readfile(filename);
        size_t buflen = strlen(buf);
        char *p = buf;
        string tmp = string(p, buflen);
		string retstr;
		string ivname;
        string ivaccount;
        string ivtime;
		while ((ivname = extract(tmp, "NickName", ":\"", "", "\"")) != "") {
			ivaccount = extract(tmp, "PayMoney", ":\"", "","\"");
			ivtime = extract(tmp, "CreateTime", ":\"", "","\"");
            ivtime = longtostring(stringtotime(ivtime.c_str(), "%Y-%m-%d %H:%M:%S"));
			retstr += ivtime + "|" + ivname + "|" + ivaccount + "|";
			string::size_type pos = tmp.find("}");
			if (pos != string::npos) {
				tmp = tmp.substr(pos + 1);
			}
			else {
				break;
			}
		}
        
        free(buf);
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
