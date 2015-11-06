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
    kv["site_id"] = "yooli";
    kv["project_name"] = extract(bstr,"<div class=\"head\">","<h2>","","</h2>");
    kv["project_id"] = idstr;
    kv["borrowing_amount"] = num_util(extract(bstr, "借款金额", "￥", "<em>","</em>"));
	kv["borrower"] = extract(bstr, "用户ID", "val\">", "","</span>");

//	kv["release_time"] = longtostring(stringtotime(extract(bstr,"","：","","</li>").c_str(),"%Y.%m.%d"));
    kv["invested_amount"] = doubletostring(s_atod(kv["borrowing_amount"].c_str()) - s_atod(num_util(extract(bstr, "投资金额", "可投", "￥", "元")).c_str()));

    kv["annulized_rating"] = filternum(extract(bstr, "年化利率", "","", "%"));
	kv["loan_period"] = loanperiod_util(extract(bstr, "还款期限", "<em>", "","</dd>"));
	kv["payment_method"] = extract(bstr,"<div class=\"repay\">",">","","<");

    {
		sprintf(filename, "html/%s.brec",idstr);
		buf = readfile(filename);
		size_t buflen = strlen(buf);
		char *p = buf;
		string retstr;
		while(p < buf + buflen - 8)
		{
			int len;
			sscanf(p,"%08x",&len);
			p += 8;
			string jstr = string(p, len);
			p += len;
			Value json = stringtojson(jstr);
			string ivname;
			string ivaccount;
			string ivtime;
			if (has_array_member(json, "voList") )
			{
				for(int i = 0;i != json["voList"].size(); i++)
				{
					if(!get_string_member(json["voList"][i],"investorNickname",ivname) 
							|| !get_string_member(json["voList"][i],"toBeCollectedPrincipal",ivaccount)
							|| !get_string_member(json["voList"][i],"investTime",ivtime))
						continue;
					ivtime = extract(ivtime,"","","",".");
					ivtime = longtostring(stringtotime(ivtime.c_str(),"%Y-%m-%d"));
					retstr += ivtime + "|" + ivname + "|" + ivaccount + "|";


				}
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
