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
    kv["site_id"] = "sukedai";
    kv["borrower"] = extract(bstr, "概述", "<span>", "", "</span>");
    kv["project_name"] = extract(bstr, "<div class=\"qst_title\">", "", "", "</span>");
    kv["project_id"] = idstr;
    kv["borrowing_amount"] = num_util(filternum(extract(bstr, "<font class=\"fs30\">", "￥", "\">", "</font>")));
    kv["annulized_rating"] = filternum(extract(bstr, "借款利率", "：", "", "%"));
    kv["payment_method"] = extract(bstr, "还款方式", "：", "", "<");
	
	kv["loan_period"] = loanperiod_util(extract(bstr, "期限","<font", "\">", "</div> "));
	kv["release_time"] = longtostring(stringtotime(extract(bstr,"发标时间","：","","</li>").c_str(),"%Y-%m-%d"));





    {
        string retstr;
        string::size_type tmp =  bstr.find("投资时间");
        
		if(tmp != string::npos){
            tmp =  bstr.find("<tr>",tmp);
        }
        if(tmp != string::npos){

            string striv = bstr.substr(tmp);
            string ivname;
            string ivaccount;
            string ivtime;
            while ((ivname = extract(striv, "<td>", "", "", "</td>")) != "") {
                ivaccount = filternum(extract(striv, "<td>", "<td>","<td>", "</td>"));
                ivtime = extract(striv, "投标", "<td>", "<td>", "</td>");
                ivtime = longtostring(stringtotime(ivtime.c_str(), "%Y-%m-%d %H:%M:%S"));


				retstr += ivtime + "|" + ivname + "|" + ivaccount + "|";

				if (striv.find("</tr>") == string::npos) {
					break;
				}
                striv = striv.substr(striv.find("</tr>") + 1);

//				retstr += ivtime + "|" + ivname + "|" + ivaccount + "|";
            }

        }
        kv["investor"] = retstr;
    }
    printstringmap(kv);


    if (kv["project_id"] == "" || s_atol(kv["borrowing_amount"].c_str()) <= 0) {
        return 1;
    }

	sprintf(filename, "data/%s", idstr);
    return savestringmap(kv, filename);
	return 0;
}

int main(int argc, char *argv[])
{
    if (argc < 2) {
        return 0;
    }
    return parsefile(argv[1]);
}

