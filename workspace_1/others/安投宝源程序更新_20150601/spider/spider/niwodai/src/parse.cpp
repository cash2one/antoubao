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
    kv["site_id"] = "niwodai";
    kv["borrower"] = extract(bstr, "借款人信息", "基本信息", "用户名：","</");
    kv["credit_rating"] = extract(bstr, "<h4 class=", "信用状况", "ico_green\">", "</span>");
    if (kv["credit_rating"] == "") {
        kv["credit_rating"] = extract(bstr, "借款人信息", "<em id=\"level\"", ">", "<span");
    }
    kv["project_name"] = extract(bstr,"<meta name","description","content=\"","\" />");
    kv["project_id"] = extract(bstr,"<em class=","项目ID","：","</em>");
    kv["borrowing_amount"] = filternum(extract(bstr, "债权总额", "：","fs_32\">","</span>"));
    kv["annulized_rating"] = filternum(extract(bstr, "借款年利率", "</span>", "fs_32\">", "</span>"));
    kv["payment_method"] = extract(bstr,"还款期限","还款方式","<span>","</span>");
    kv["loan_period"] = extract(bstr, "还款期限", "：", "fs_32\">","</span></div>");
    int pos = kv["loan_period"].find("月");
    if (pos != -1) {
        kv["loan_period"] = longtostring(atof(kv["loan_period"].c_str())*30);
    }
    else{

        kv["loan_period"] = longtostring(atof(kv["loan_period"].c_str()));
    }

    kv["invested_amount"] = doubletostring(s_atod(kv["borrowing_amount"].c_str()) - s_atod(filternum(extract(bstr,"剩余金额","：",":none\">","</span>")).c_str()));
    long long etime = stringtotime(extract(bstr,"剩余时间","：",":none\">","</span>").c_str(), "%Y/%m/%d %H:%M:%S");
    if (etime > 1000000000) {
        kv["end_time"] = longtostring(etime);
    }
    kv["project_details"] = extract(bstr,"借款人描述","  <p class=","\">","</p>");
    {
        string tmp;
        string::size_type startpos = bstr.find("投标时间");
        if (startpos != string::npos) {
            string::size_type endpos = bstr.find("id=\"paymentContent\"", startpos);
            if (endpos != string::npos) {
                tmp = bstr.substr(startpos, endpos - startpos);
            }
        }
        string ivname;
        string ivaccount;
        string ivtime;
        string retstr;
        while ((ivname = extract(tmp, " <tr>", "<td class", "\"f\">", "</td>")) != "") {
            ivaccount = extract(tmp, "<td class=\"f\">", " <td class", "\"tr\"><span>","</span></td>");
            ivtime = extract(tmp, " <td class=\"l\">", "<span class=", "time\">", "</span></td>");
            ivtime = longtostring(stringtotime(ivtime.c_str(), "%Y-%m-%d %H:%M")
                    );

            retstr += ivtime + "|" + ivname + "|" + ivaccount + "|";
            string::size_type pos = tmp.find("</tr>");
            if (pos != string::npos) {
                tmp = tmp.substr(pos + 1);
            }
            else {
                break;
            }
        }
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
