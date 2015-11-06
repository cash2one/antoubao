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
    kv["site_id"] = "yingtianx";
    kv["borrower"] = extract(bstr, "借款情况描述", "<br>", "","<br><b");
    kv["project_name"] = extract(bstr,"class=\"box-title-txt\">","","","</strong>");
    kv["project_id"] = idstr;
    kv["borrowing_amount"] = num_util(extract(bstr, "贷款金额", "￥","","</span>"));

	kv["release_time"] = longtostring(stringtotime(extract(bstr,"发标时间","：","\">","</span>").c_str(),"%Y-%m-%d %H:%M"));

    kv["annulized_rating"] = filternum(extract(bstr, "利", "率","\">", "%"));
	kv["payment_method"] = extract(bstr,"还款方式","","<span>","</span>");
    kv["loan_period"] = loanperiod_util(extract(bstr, "贷款期限", ">", "","</span>"));

    {
        sprintf(filename, "html/%s.brec", idstr);
        buf = readfile(filename);
        size_t buflen = strlen(buf);
        char *p = buf;
        string retstr;
        while (p < buf + buflen - 8) {
            int len;
            sscanf(p, "%08X", &len);
            p += 8;
            string tmp = string(p, len);
            p += len;


			Value json = stringtojson(tmp);
			string ivname;
			string ivaccount;
			string ivtime;

			if(has_object_member(json,"data"))
			{
				if(has_array_member(json["data"],"list"))
				{
					for(int i = 0;i != json["data"]["list"].size();i++)
					{
						if(!get_string_member(json["data"]["list"][i],"uname",ivname)
									|| !get_string_member(json["data"]["list"][i],"money",ivaccount)
									|| !get_string_member(json["data"]["list"][i],"datetime",ivtime))
							continue;
						ivtime = longtostring(stringtotime(ivtime.c_str(),"%Y-%m-%d %H:%M:%S"));
						retstr += ivtime + "|" + ivname + "|" + ivaccount + "|";
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
