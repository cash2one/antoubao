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
    string tmp = string(buf);
    free(buf);
    map <string, string> kv;
    kv["site_id"] = "baikaiqi";
    kv["project_name"] = extract(tmp,"<head>","<meta http-equiv=", "<title>", "-");
    kv["project_id"] = idstr;
    kv["borrowing_amount"] = num_util(extract(tmp, "融资金额", "￥","money\">", "</div></div>"));
	kv["invested_amount"] = doubletostring(s_atod(kv["borrowing_amount"].c_str()) - s_atod(num_util(extract(tmp, "剩余份额", "￥", "\">", "</div>")).c_str()));
    kv["annulized_rating"] = filternum(extract(tmp,"<div class=\"cont\">","年化利率", "text\">", "%</div></div>"));
    kv["payment_method"] = extract(tmp,"<div class=\"cont\">","还款方式", "text\">","</div></div>");
    kv["loan_period"] = loanperiod_util(extract(tmp, "<div class=\"cont\">", "投资期限", "text\">","</div></div>"));
    kv["release_time"] = longtostring(stringtotime(extract(tmp,"<div class=\"ui_win\">","开标时间","：","最后投标").c_str(), "%Y-%m-%d"));
    
	
	{
		sprintf(filename,"html/%s.brec",idstr);
		buf = readfile(filename);
		string retstr;
		if(buf)
		{
			char *p = buf;
			size_t buflen = strlen(buf);
			while(p < buf + buflen - 8)
			{
				int len;
				sscanf(p,"%08x",&len);
				p += 8;
				string jstr = string(p,len);
				p += len;
				Value json = stringtojson(jstr);
				string tmp;
				if(has_string_member(json,"data"))
				{
					get_string_member(json,"data",tmp);
				}
				string ivname;
				string ivaccount;
				string ivtime;
				while((ivname = extract(tmp, "动", "</span>", "", "</div>")) != "")
				{
					ivaccount = num_util(extract(tmp, "", "￥", "money\">","</span>"));
					ivtime = extract(tmp, "元", "%", "time\">", "　");
					ivtime = longtostring(stringtotime(ivtime.c_str(), "%Y-%m-%d %H:%M:%S"));
					retstr += ivtime + "|" + ivname + "|" + ivaccount + "|";

					string::size_type pos = tmp.find("</div></div></div>");
					if (pos != string::npos)
					{
						tmp = tmp.substr(pos + 1);
					}
					else
						break;


				}


			}
		}
			
      kv["investor"] = retstr;    
    }


    if (kv["project_id"] == "" ) {
        return 1;
    }
   printstringmap(kv);
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
    
    
