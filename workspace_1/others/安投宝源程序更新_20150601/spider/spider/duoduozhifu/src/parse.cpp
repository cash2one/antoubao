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
    kv["site_id"] = "duoduozhifu";
    kv["project_name"] = extract(bstr,"<div class=\"borrow-list-head\">","","","</div>");
    kv["project_id"] = idstr;
    kv["borrowing_amount"] = num_util(extract(bstr, "借款金额", "￥", "","</strong>"));
	kv["borrower"] = extract(bstr, "借款人", "<div", "\">","</div>");

//	kv["release_time"] = longtostring(stringtotime(extract(bstr,"","：","","</li>").c_str(),"%Y.%m.%d"));
    kv["invested_amount"] = doubletostring(s_atod(kv["borrowing_amount"].c_str()) - s_atod(num_util(extract(bstr, "目前可投金额", "\">", "", "</div>")).c_str()));

    kv["annulized_rating"] = filternum(extract(bstr, "年化利率", "<strong","\">", "%"));
	kv["loan_period"] = loanperiod_util(extract(bstr, "还款期限", "<strong", "\">","</strong>"));
	kv["payment_method"] = extract(bstr,"还款方式","：","","<");

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
			double ivaccount;
			string ivtime;
			if (has_array_member(json, "rows") )
			{
				for(int i = 0;i != json["rows"].size(); i++)
				{
					if(!get_string_member(json["rows"][i],"userName",ivname) 
							|| !get_double_member(json["rows"][i],"investAmount",ivaccount)
							|| !get_string_member(json["rows"][i],"investTime",ivtime))
						continue;
					ivtime = longtostring(stringtotime(ivtime.c_str(),"%Y-%m-%d %H:%M:%S"));
					retstr += ivtime + "|" + ivname + "|" + doubletostring(ivaccount) + "|";


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
