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
    kv["site_id"] = "haochedai";
    kv["borrower"] = extract(bstr, "用户名", "</li>", "<span>", "</span>");
    kv["project_name"] = extract(bstr, "<div class=\"estitle\">", "<h2>", "", "</h2>");
    kv["project_id"] = idstr;
    kv["borrowing_amount"] = filternum(extract(bstr, "项目总额", "￥", "</em>", "</p>"));
    kv["annulized_rating"] = filternum(extract(bstr, "年化利率", "</em>", "<p>", "%"));
    kv["payment_method"] = extract(bstr, "还款方式", "<em>", "", "</em>");
//    kv["award"] = filternum(extract(bstr, "年化利率", "<span style=\"\">", "+", "%"));
	
	kv["invested_amount"] = doubletostring(s_atod(kv["borrowing_amount"].c_str()) - \
			s_atod(filternum(extract(bstr,"剩余金额","￥","","</span>")).c_str()));

    kv["credit_rating"] = extract(bstr,"信用等级","<p>","","</p>");
    kv["minimum_investment"] =extract(bstr,"最低","","","元");
    kv["project_details"] = extract(bstr, "基本信息", "基本信息","<em>", "风控信息 end");
	kv["loan_period"] = extract(bstr, "投资期限","<p>", "", "</em>");
	if (kv["loan_period"].find("月") != string::npos) {
		kv["loan_period"] = doubletostring(s_atod(filternum(kv["loan_period"]).c_str())*30);
	}
	else{
		kv["loan_period"] = doubletostring(s_atod(filternum(kv["loan_period"]).c_str()));
	}
	kv["release_time"] = longtostring(stringtotime(extract(bstr,"开始招标","</dd>","<dd>","</dd>").c_str(),"%Y-%m-%d"));
    kv["end_time"] = longtostring(stringtotime(extract(bstr,"满标待审","</dd>","<dd>","</dd>").c_str(),"%Y-%m-%d"));





    int investornum = 0;
    {
        string retstr;
        string::size_type tmp =  bstr.find("投标人");
	    string::size_type endpos = bstr.find("<!-- <li class=\"tebord\">");
        if(tmp != string::npos){
            tmp = bstr.find("投标时间", tmp+1);
        }
        if(tmp != string::npos){
            tmp =  bstr.find("<li>",tmp+1);
        }
        if(tmp != string::npos && endpos != string::npos){

            string striv = bstr.substr(tmp,endpos - tmp);
            string ivname;
            string ivaccount;
            string ivtime;
            while ((ivname = extract(striv, "<li>", "", "", "</li>")) != "") {
                ivaccount = filternum(extract(striv, "</li>", "<li>","￥", "</li>"));
                ivtime = extract(striv, "</li>", "</li>", "<li>", "</li>");
                ivtime = longtostring(stringtotime(ivtime.c_str(), "%Y-%m-%d %H:%M:%S"));


				retstr += ivtime + "|" + ivname + "|" + ivaccount + "|";
		        investornum++;


//				if (striv.find("</tr>") == string::npos) {
//                    break;
//                }
                striv = striv.substr(striv.find("</li>") + 1);
				striv = striv.substr(striv.find("</li>") + 1);
				striv = striv.substr(striv.find("</li>") + 1);

//				retstr += ivtime + "|" + ivname + "|" + ivaccount + "|";
//              investornum++;
            }

        }
        kv["investor"] = retstr;
    }
    kv["investors_volume"] = longtostring(investornum);
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

