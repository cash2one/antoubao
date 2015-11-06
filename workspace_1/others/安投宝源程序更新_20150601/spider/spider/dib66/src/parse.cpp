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
    kv["site_id"] = "dib66";
    kv["project_name"] = extract(bstr, "<div class=\"first_floor\">", "<div", "<div class=\"title_left\">", "</div>");
    kv["project_id"] = idstr;
    kv["borrowing_amount"] = num_util(extract(bstr, "借款总额", "</tr>", "ass=\"span1\">", "</td>"));
    kv["annulized_rating"] = num_util(extract(bstr, "年利率","<tr>","class=\"span1\">", "%"));
    kv["payment_method"] = extract(bstr, "还款方式", "：", "<td>", "</td>");
	kv["invested_amount"] = doubletostring(s_atod(kv["borrowing_amount"].c_str()) - \
			s_atod(filternum(extract(bstr,"<div class=\"right\"","目前可投金额","<span class=\"span1\">","</span")).c_str()));

    kv["end_time"] = longtostring(s_atol(extract(bstr, "id=\"remainSeconds\"" ,"value=\"", "", "\"").c_str()) + time(NULL));

    //kv["project_details"] = extract(bstr, "借款详情", "项目信息","<div class=\"content\">", "<div class=\"switch_c_2\"");
    {
        string retstr;
        string striv = extracthtml(bstr, "<!--投资记录-->", "状态", "</tr", "</table");
        string ivname;
        string ivaccount;
        string ivtime;
        while ((ivname = extract(striv, "</td>", "", "", "</td>")) != "") {
            ivaccount = filternum(extract(striv, "</td>", "</td>", "", "</td>"));
            ivtime = extract(extracthtml(striv, "</td>", "</td>", "</td>", "</tr>"), "</td>", "", "", "</td");
            ivtime = longtostring(stringtotime(ivtime.c_str(), "%Y-%m-%d %H:%M:%S"));

            retstr += ivtime + "|" + ivname + "|" + ivaccount + "|";

            if (striv.find("</tr>") == string::npos) {
                break;
            }
            striv = striv.substr(striv.find("</tr>") + 1);
        }
        kv["investor"] = retstr;
    }

    printstringmap(kv);

    if (kv["project_id"] == "" || s_atol(kv["borrowing_amount"].c_str()) <= 0) {
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

