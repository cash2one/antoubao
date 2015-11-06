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
    kv["site_id"] = "huiyingdai";
    kv["project_name"] = extract(bstr, "投资详情", "<h3>", "</i>", "</h3>");
    kv["credit_rating"] = "";
    kv["borrower"] = extract(bstr, "借款编号", "</span>", "class=\"val\">", "</span>");
    kv["project_id"] = idstr;
    kv["borrowing_amount"] = filternum(extract(bstr, "标的总额", "元", "<em>", "</em>"));
    kv["annulized_rating"] = filternum(extract(bstr, "年化收益率","<strong>","id=\'em_apr\'>", "</em>"));
    kv["payment_method"] = extract(bstr, "还款方式", "</span>", "class=\"\">", "</span>");
    kv["award"] = "";
	kv["invested_amount"] = doubletostring(s_atod(kv["borrowing_amount"].c_str()) - \
			s_atod(filternum(extract(bstr,"可投金额","</label>","<em>","</em>")).c_str()));
    string lperiod = extract(bstr, "还款期限", "月", "id=\'em_period\'>", "</em>");
//    if (lperiod.find("月") != string::npos) {
//		        kv["loan_period"] = longtostring(s_atod(lperiod.c_str())*30);
//				    }
//  else {
//		kv["load_period"] = longtostring(s_atol(lperiod.c_str()));
//		 }
    kv["loan_period"] = lperiod;
	kv["minimum_investment"] = "";
    kv["maximum_investment"] = "";
    kv["release_time"] = longtostring(stringtotime((extract(bstr, "发标时间", "</span>", "class=\"num\">", "</span>")).c_str(),"%Y-%m-%d %H:%M"));
//    kv["end_time"] = longtostring(stringtotime(extract(bstr, "还款中","<tr>","align=\"center\">", "售完").c_str(),"%Y-%m-%d %H:%M:%S"));

    kv["project_details"] = extract(bstr, "项目信息", "<div class=\"lab-val\">"," <h2>", "</table>");

	
	sprintf(filename, "html/%s.brec", idstr);
    buf = readfile(filename);

    int investornum = 0;
    {
        string retstr;
        string::size_type tmp =  bstr.find("投标人");
	    string::size_type endpos;
        if(tmp != string::npos){
            tmp = bstr.find("投标时间", tmp+1);
        }
        if(tmp != string::npos){
            tmp =  bstr.find("</thead>",tmp+1);
	//		endpos = bstr.find("</table>", tmp+1);
        }
        if(tmp != string::npos){

            string striv = bstr.substr(tmp);
            string ivname;
            string ivaccount;
            string ivtime;
            while ((ivname = extract(striv, "<td>", "</td>", "<td>", "</td>")) != "") {
                ivaccount = filternum(extract(striv, "<td>", "</td>","<em>", "</em>"));
                ivtime = extract(striv, "<td>" , "元","<td>" , "</td>");
                ivtime = longtostring(stringtotime(ivtime.c_str(), "%Y-%m-%d %H:%M:%S"));
                if (striv.find("</tr>") == string::npos) {
                    break;
                }
                striv = striv.substr(striv.find("</tr>") + 1);

                retstr += ivtime + "|" + ivname + "|" + ivaccount + "|";
                investornum++;
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
}

int main(int argc, char *argv[])
{
    if (argc < 2) {
        return 0;
    }
    return parsefile(argv[1]);
}

