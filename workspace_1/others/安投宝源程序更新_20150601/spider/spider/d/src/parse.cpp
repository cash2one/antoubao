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
	char * piv = buf;
    string bstr = string(buf);
	int  last_page_nums;
	sscanf(piv,"%08X",&last_page_nums);
	piv += 8;
	int  page_num;
	sscanf(piv,"%08X",&page_num);
    free(buf);
    map <string, string> kv;
    kv["site_id"] = "d";
//    kv["borrower"] = extract(bstr, "借款情况描述", "<br>", "","<br><b");
    kv["project_name"] = extract(bstr,"<h2 class=\"loan_title\">","","","<span");
    kv["project_id"] = idstr;
    kv["borrowing_amount"] = num_util(extract(bstr, "借款额度", "<div>","","</i>"));
	kv["invested_amount"] = num_util(extract(bstr, "%#%", "","","<"));

//	kv["release_time"] = longtostring(stringtotime(extract(bstr,"发标时间","：","\">","</span>").c_str(),"%Y-%m-%d %H:%M"));

    kv["annulized_rating"] = filternum(extract(bstr, "预计年化率", "<div>","", "%"));
	kv["payment_method"] = extract(bstr,"还款方式","<div>","","</div>");
    kv["loan_period"] = loanperiod_util(extract(bstr, "借款期限", "<div>", "","</div>"));

    {
        sprintf(filename, "html/%s.brec", idstr);
        buf = readfile(filename);
        size_t buflen = strlen(buf);
        char *p = buf;
        string retstr;
		long page_current = 1;
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
			string iv_list = string(idstr) + string("_tender_page_") + longtostring(page_current);

			if(has_object_member(json,"data"))
			{
				if(has_object_member(json["data"],iv_list.c_str()))
				{
					if(has_array_member(json["data"][iv_list.c_str()],"tender"))
					{
							for(int i = 0; i != json["data"][iv_list.c_str()]["tender"].size(); i++)
							{
								if(!get_string_member(json["data"][iv_list.c_str()]["tender"][i],"username",ivname)
										|| !get_string_member(json["data"][iv_list.c_str()]["tender"][i],"money",ivaccount)
										|| !get_string_member(json["data"][iv_list.c_str()]["tender"][i],"timeadd",ivtime))
									continue;
								ivtime = longtostring(stringtotime(ivtime.c_str(),"%Y-%m-%d %H:%M:%S"));
								retstr += ivtime + "|" + ivname + "|" + ivaccount + "|";
							}

					}
					if(has_object_member(json["data"][iv_list.c_str()],"tender") && (page_current != page_num))
					{
						long index_p = (page_current - 1) * 100;
						for(int i = 0; i != 100; i++)
						{
							int index = index_p + i;
							string iv_index = longtostring(index);
							if(!get_string_member(json["data"][iv_list.c_str()]["tender"][iv_index.c_str()],"username",ivname)
									|| !get_string_member(json["data"][iv_list.c_str()]["tender"][iv_index.c_str()],"money",ivaccount)
									|| !get_string_member(json["data"][iv_list.c_str()]["tender"][iv_index.c_str()],"timeadd",ivtime))
							{
								continue;
							}
							ivtime = longtostring(stringtotime(ivtime.c_str(),"%Y-%m-%d %H:%M:%S"));
							retstr += ivtime + "|" + ivname + "|" + ivaccount + "|";
						}
					}
					if(has_object_member(json["data"][iv_list.c_str()],"tender") && page_current == page_num)
					{
						long index_p = (page_current - 1) * 100;
						for(int i = 0; i != last_page_nums; i++)
						{
							int index = index_p + i;
							string iv_index = longtostring(index);
							if(!get_string_member(json["data"][iv_list.c_str()]["tender"][iv_index.c_str()],"username",ivname)
									|| !get_string_member(json["data"][iv_list.c_str()]["tender"][iv_index.c_str()],"money",ivaccount)
									|| !get_string_member(json["data"][iv_list.c_str()]["tender"][iv_index.c_str()],"timeadd",ivtime))
								continue;
							ivtime = longtostring(stringtotime(ivtime.c_str(),"%Y-%m-%d %H:%M:%S"));
							retstr += ivtime + "|" + ivname + "|" + ivaccount + "|";
						}
					}
				}
			}

			page_current++;
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
