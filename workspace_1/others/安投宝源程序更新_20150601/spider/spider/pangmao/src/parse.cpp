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
    kv["site_id"] = "pangmao";
    kv["borrower"] = extract(bstr, "username", "\">", "","</span>");
    kv["project_name"] = extract(bstr,"<span class=\"title\">","","","</span>");
    kv["project_id"] = idstr;
    kv["borrowing_amount"] = num_util(extract(bstr, "标的总额", "<div","<em>","</div>"));

//	kv["release_time"] = longtostring(stringtotime(extract(bstr,"开始时间","\">","","</span>").c_str(),"%Y-%m-%d %H:%M:%S"));

    kv["annulized_rating"] = filternum(extract(bstr, "年化收益率", "class=\"number\">","<em>", "%"));
	kv["payment_method"] = extract(bstr,"还款方式","<span>","","</span>");
    kv["loan_period"] = loanperiod_util(extract(bstr, "期限", "class=\"sp-time\"", "<em>","</span>"));

    {
		sprintf(filename, "html/%s.brec",idstr);
		buf = readfile(filename);
		size_t buflen = strlen(buf);
		char *p = buf;
		string jstr = string(p,buflen);
        string retstr;
		Value json = stringtojson(jstr);
		string ivname;
		double ivaccount;
		long ivtime;
		double ivtime_tmp;
		if (has_array_member(json, "list") )
			{
				for(int i = 0;i != json["list"].size(); i++)
				{
					if(!get_string_member(json["list"][i],"userCode",ivname) 
								|| !get_double_member(json["list"][i],"crAmt",ivaccount)
								|| !get_double_member(json["list"][i],"sysCreateTime",ivtime_tmp))
						continue;
					ivtime=static_cast<long>(ivtime_tmp) / 1000;
					retstr += longtostring(ivtime) + "|" + ivname + "|" + doubletostring(ivaccount) + "|";


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
