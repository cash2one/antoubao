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
    kv["site_id"] = "myrongbangdai";
    kv["borrower"] = extract(bstr, "借款户信息", "用户 名", "&nbsp;","&nbsp;");
    kv["project_name"] = extract(bstr,"<div class=\"infoD\">","/>","","</h1>");
    kv["project_id"] = idstr;
    kv["borrowing_amount"] = num_util(extract(bstr, "项目总额", "<p>","","</p>"));

//	kv["release_time"] = longtostring(stringtotime(extract(bstr,"开始时间","\">","","</span>").c_str(),"%Y-%m-%d %H:%M:%S"));

    kv["annulized_rating"] = filternum(extract(bstr, "年化收益率", ">","", "%"));
	kv["payment_method"] = extract(bstr,"收益方式","</span>","","</p>");
    kv["loan_period"] = loanperiod_util(extract(bstr, "理财期限", "<p>", "","</p>"));

    {
		sprintf(filename, "html/%s.brec",idstr);
		buf = readfile(filename);
		size_t buflen = strlen(buf);
		char *p = buf;
		string jstr = string(p,buflen);
        string retstr;
		Value json = stringtojson(jstr);
		string ivname;
		string ivaccount;
		string ivtime;
		string ivtime_tmp;
		if (has_array_member(json, "BidList") )
			{
				for(int i = 0;i != json["BidList"].size(); i++)
				{
					if(!get_string_member(json["BidList"][i],"GodName",ivname) 
								|| !get_string_member(json["BidList"][i],"Amount",ivaccount)
								|| !get_string_member(json["BidList"][i],"CreateTime",ivtime_tmp))
						continue;
					ivtime=longtostring(stringtotime(ivtime_tmp.c_str(),"%Y年%m月%d日 %H:%M:%S"));
					retstr += ivtime + "|" + ivname + "|" + ivaccount + "|";


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
