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
    kv["site_id"] = "91kuaiche";
    kv["project_name"] = extract(bstr,"class=\"expeheader","<b>","","</b>");
    kv["project_id"] = idstr;
    kv["borrowing_amount"] = num_util(extract(bstr,"募集总额","<strong id=\"weighbold\">","","</strong>"));
	if(bstr.find("mess12-div") != string::npos)
	{
		kv["borrower"] = extract(bstr, "mess12-div", "借款人", "</span>","</li>");
	}

//	kv["release_time"] = longtostring(stringtotime(extract(bstr,"","：","","</li>").c_str(),"%Y.%m.%d"));
    kv["invested_amount"] = doubletostring(s_atod(kv["borrowing_amount"].c_str()) - s_atod(num_util(extract(bstr, "可投金额", "weighbold\">", "", "</strong>")).c_str()));

    kv["annulized_rating"] = filternum(extract(bstr, "年化收益", "margin-right:6px","\">", "%"));
	kv["loan_period"] = loanperiod_util(extract(bstr, "项目期限", "weighbold", "table-td1\">","</td>"));
	kv["payment_method"] = extract(bstr,"收益方式","<strong>","","</strong>");

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
				for(int i = 0;i != json.size(); i++)
				{
					if(!get_string_member(json[i],"account",ivname) 
							|| !get_string_member(json[i],"tender_money",ivaccount)
							|| !get_string_member(json[i],"create_time",ivtime))
						continue;
					//ivtime = longtostring(stringtotime(ivtime.c_str(),"%Y-%m-%d"));
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
