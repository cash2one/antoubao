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
    kv["site_id"] = "cashlai";
//    kv["borrower"] = extract(bstr, "融资金额", "￥", "", "</p>");
    kv["project_name"] = extract(bstr, "<div class=\"pto_li_title\">", "<font>", "", "</font>");
    kv["project_id"] = idstr;
    kv["borrowing_amount"] = filternum(extract(bstr, "融资金额", "￥", "", "</p>"));
    kv["annulized_rating"] = filternum(extract(bstr, "年化利率", "<font class=\"fl\">", "<font class=\"fl\">", "<span"));
    kv["payment_method"] = extract(bstr, "<div class=\"psoe_isj fr\">", "", "", "</div>");
	
	string success_amount = filternum(extract(bstr, "成功融资", "￥", "", "</div>"));
	if(success_amount != "")
		kv["invested_amount"] = success_amount;
	else
		kv["invested_amount"] = doubletostring(s_atod(kv["borrowing_amount"].c_str()) - \
				s_atod(filternum(extract(bstr,"可投","￥","","</span>")).c_str()));



    kv["project_details"] = extract(bstr, "项目介绍", "项目情况","项目情况", "</span>");
	kv["loan_period"] = extract(bstr, "融资期限","<i", "\">", "</span>");
	if (kv["loan_period"].find("月") != string::npos) {
		kv["loan_period"] = doubletostring(s_atod(filternum(kv["loan_period"]).c_str())*30);
	}
	else{
		kv["loan_period"] = doubletostring(s_atod(filternum(kv["loan_period"]).c_str()));
	}




    int investornum = 0;
    {
        string retstr;
        string::size_type tmp =  bstr.find("投资时间");
	    string::size_type endpos = bstr.find("投资记录  [end]");
        if(tmp != string::npos){
            tmp = bstr.find("</tr>", tmp+1);
        }
        if(tmp != string::npos){
            tmp =  bstr.find("<tr>",tmp+1);
        }
        if(tmp != string::npos && endpos != string::npos){

            string striv = bstr.substr(tmp,endpos - tmp);
            string ivname;
            string ivaccount;
            string ivtime;
            while ((ivname = extract(striv, "<td>", "", "", "</td>")) != "") {
                ivaccount = filternum(extract(striv, "</td>", "<td>","", "</td>"));
                ivtime = extract(striv, "<td>", "</span>", "<td>", "</td>");
                ivtime = longtostring(stringtotime(ivtime.c_str(), "%Y-%m-%d %H:%M:%S"));


				retstr += ivtime + "|" + ivname + "|" + ivaccount + "|";
		        investornum++;


				if (striv.find("</tr>") == string::npos) {
                    break;
                }
                striv = striv.substr(striv.find("</tr>") + 1);

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

