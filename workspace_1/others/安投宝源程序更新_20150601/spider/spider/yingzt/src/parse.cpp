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
    kv["site_id"] = "yingzt";
	kv["borrower"] = extract(bstr, "借款人信息", "姓名", "<b>","</b>");
    kv["project_name"] = extract(bstr,"class=\"ci-title-inner\">","projectName\">","","<");
    kv["project_id"] = idstr;
    kv["borrowing_amount"] = num_util(extract(bstr, "融资金额", "￥","","</strong>"));
	kv["invested_amount"] = doubletostring(s_atod(kv["borrowing_amount"].c_str()) - 
		s_atod(num_util(extract(bstr, "可投余额", "￥","","</strong>")).c_str()));

//	kv["release_time"] = longtostring(stringtotime(extract(bstr,"开始时间","\">","","</span>").c_str(),"%Y-%m-%d %H:%M:%S"));
    kv["annulized_rating"] = filternum(extract(bstr, "年化收益", "info\">","<strong>", "%"));
	kv["payment_method"] = extract(bstr,"还款方式","info\">","<span>","</span>");

	kv["loan_period"] = extract(bstr, "项目期限", "info\">", "<strong>","<span>");
	string loan_period_1 = filternum(extract(bstr, "项目期限", "info\">", "<strong>","<span>"));
	string period_t = extract(bstr, "项目期限", "<strong>", "<span>", "</span>");
	if(period_t.find("月") != string::npos && period_t.find("天") != string::npos)
	{
		string loan_period_2 = filternum(extract(bstr, "项目期限", "info\">", "<span>","</span>"));
		kv["loan_period"] = doubletostring(s_atod(loan_period_1.c_str()) * 30 + s_atod(loan_period_2.c_str()));
	}
	else if(period_t.find("月") != string::npos && period_t.find("天") == string::npos)
	{
		kv["loan_period"] = doubletostring(s_atod(loan_period_1.c_str()) * 30);
	}
	else if(period_t.find("月") == string::npos && period_t.find("天") != string::npos)
	{
		kv["loan_period"] = doubletostring(s_atod(loan_period_1.c_str()));
	}


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
		string bstr;
		if (get_string_member(json, "data",bstr) )
		{
			string::size_type spos = bstr.find("投资时间");
			string::size_type epos = bstr.find("</table>",spos + 1);
			if (spos != string::npos && epos != string::npos) {
				bstr = bstr.substr(spos, epos - spos);
				spos = bstr.find("</tr>");
				bstr = bstr.substr(spos + 1);
				while((ivname = extract(bstr, "<td>", "", "", "</td>")) != "")
				{
					ivaccount = extract(bstr, "￥", "", "","</td>");
					ivtime = extract(bstr,"￥", "<td>", "", "</td>");
					ivtime = longtostring(stringtotime(ivtime.c_str(), "%Y-%m-%d %H:%M:%S"));
					retstr += ivtime + "|" + ivname + "|" + ivaccount + "|";
					string::size_type pos = bstr.find("</tr>");
					if (pos != string::npos)
					{
						bstr = bstr.substr(pos + 1);
					}
					else
					{
						break;
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
