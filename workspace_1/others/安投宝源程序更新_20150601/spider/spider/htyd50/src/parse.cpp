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
    kv["site_id"] = "htyd50";
    kv["borrower"] = extract(bstr,"借款人", "<td",">", "</td>");
    kv["project_name"] = extract(bstr, "<div class=\"fl f_22\">", "", "", "</div>");
    kv["project_id"] = idstr;
    kv["borrowing_amount"] = filternum(extract(bstr, "借款金额", "</div>", "<div", "</div>"));
    kv["annulized_rating"] = filternum(extract(bstr, "年化收益","</div>","<div", "%"));
    kv["payment_method"] = extract(bstr, "<div class=\"fl f_22\">", "<span", "\">", "</span>");
	kv["loan_period"] = extract(bstr, "借款期限","</div>", "<div", "<div class=\"mt_20\">");
	if (kv["loan_period"].find("月") != string::npos) {
		kv["loan_period"] = doubletostring(s_atod(filternum(kv["loan_period"]).c_str())*30);
	}
	else{
		kv["loan_period"] = doubletostring(s_atod(filternum(kv["loan_period"]).c_str()));
	}
//	kv["invested_amount"] = doubletostring(s_atod(kv["borrowing_amount"].c_str()) - \
			s_atod(filternum(extract(bstr,"借款还需","：","","</div>")).c_str()));

 //   kv["release_time"] = longtostring(stringtotime((extract(bstr, "借款金额", "开始时间", "：", "</font>")).c_str(),"%Y-%m-%d %H:%M:%S"));
 //   kv["release_time"] = "";
 //   kv["end_time"] = longtostring(stringtotime(extract(bstr, "满标","：","", "</span>").c_str(),"%Y-%m-%d %H:%M"));

    kv["project_details"] = extract(bstr, "借款描述", "</div>","style=\"width:20%;\">", "用户材料");


	 sprintf(filename, "html/%s.brect", idstr);
	 buf = readfile(filename);
	 bstr=string(buf);
//   kv["release_time"] = extract(bstr, "招标中", "date=\"", "", "\"");





	free(buf);
	sprintf(filename, "html/%s.breco", idstr);
	buf = readfile(filename);
	bstr=string(buf);

    int investornum = 0;
    {
		 kv["invested_amount"] = filternum(extract(bstr, "已投", "", "", "元"));





        string retstr;
        string::size_type tmp =  bstr.find("投标人");
	//	string::size_type endpos;
        if(tmp != string::npos){
            tmp = bstr.find("备注", tmp+1);
        }
        if(tmp != string::npos){
            tmp =  bstr.find("<tr",tmp+1);
	//		endpos = bstr.find("<div class=\"ui-box-content J_box_tab\"", tmp+1);
        }
        if(tmp != string::npos){

            string striv = bstr.substr(tmp);
            string ivname;
            string ivaccount;
            string ivtime;
            while ((ivname = extract(striv, "</td>", "<td", "\">", "</td>")) != "") {
                ivaccount = filternum(extract(striv, "%", "<td","\">", "</td>"));
                ivtime = extract(striv, "%</td>", "</td>", "\">", ".");
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
	free(buf);


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

