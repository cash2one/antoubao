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
    kv["site_id"] = "ppmoney";
    kv["project_name"] = extract(bstr,"<div class=\"l-proj","<h1>","","</h1>");
    kv["project_id"] = idstr;
    kv["borrowing_amount"] = num_util(extract(bstr, "融资金额", "<span", ">","</li>"));
//	kv["borrower"] = extract(bstr, "用户ID", "val\">", "","</span>");

//	kv["release_time"] = longtostring(stringtotime(extract(bstr,"","：","","</li>").c_str(),"%Y.%m.%d"));
    kv["invested_amount"] = doubletostring(s_atod(kv["borrowing_amount"].c_str()) 
			- s_atod(num_util(extract(bstr, "", "", "", "<")).c_str()));

    kv["annulized_rating"] = filternum(extract(bstr, "<ul class=\"cf\">", "年化","\">", "%"));
	kv["loan_period"] = loanperiod_util(extract(bstr, "<ul class=\"cf\">", "期限", "\">","</li>"));
	kv["payment_method"] = extract(bstr,"<ul class=\"cf\">","偿还方式","</span>","</");

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
			long long ivtime_tmp;
			if (has_object_member(json, "Data") )
			{
				if(has_array_member(json["Data"],"Rows"))
				{
					for(int i = 0;i != json["Data"]["Rows"].size(); i++)
					{
						if(!get_string_member(json["Data"]["Rows"][i],"Surname",ivname) 
								|| !get_double_member(json["Data"]["Rows"][i],"Amount",ivaccount)
								|| !get_string_member(json["Data"]["Rows"][i],"ApplyTime",ivtime))
							continue;
						ivtime = extract(ivtime,"(","","","+");
						ivtime_tmp = s_atoll(ivtime.c_str()) / 1000;
						ivtime = lltostring(ivtime_tmp);
						retstr += ivtime + "|" + ivname + "|" + doubletostring(ivaccount) + "|";
					}
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
