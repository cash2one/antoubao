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
    kv["site_id"] = "leadoor";
    kv["borrower"] = extract(bstr," <tbody><tr>","<td width=\"69%\" valign=\"to","\">","</a></div>");
    kv["credit_rating"] = extract(bstr, "<tbody><tr>", "信用评级", "title='", "分");
    kv["project_name"] = extract(bstr,"top\" align=\"right\">","jk_bor\">","<h1>"," <img src=");
    kv["project_id"] = extract(bstr,"<td valign=","借贷编号","：","</span>");
    kv["borrowing_amount"] = filternum(extract(bstr, "借款金额","：","￥","</b>&"));
    kv["annulized_rating"] = filternum(extract(bstr, "借款年利率", "：", "<span>", "%</span>"));
    kv["payment_method"] = extract(bstr,"</tbody></table>","<td width=\"34%","还款方式：","</td>");
    kv["award"] = "0";
    kv["loan_period"] = extract(bstr, "借款金额", "借款年利率", "借款期限：", "天</div>");
    kv["invested_amount"] = longtostring(s_atol(kv["borrowing_amount"].c_str()) - s_atol(filternum(extract(bstr,"笔投标","还需 ","\">￥","</span>")).c_str()));
    kv["minimum_investment"] = extract(bstr,"color:#666666","最低投标金额","￥","</font>");
    kv["maximum_investment"] = extract(bstr,"<td width=\"38%","最低投标金额","最高投标金额：","</span>");
    kv["release_time"] = "0";
    kv["end_time"]= "0";
    kv["project_details"] = extract(bstr,"conbox t10\">","借款详情介绍","margin:10px\">","</div>");
    {
        string tmp;
        string::size_type startpos = bstr.find(" 投标时间");
        if (startpos != string::npos) {
            startpos = bstr.find("<tr style=\"height: 30px;\">", startpos);
        }
        if (startpos != string::npos) {
            string::size_type endpos = bstr.find("<script>", startpos);
            if (endpos != string::npos) {
                tmp = bstr.substr(startpos + 1, endpos - startpos - 1);
            }
        }
        string ivname;
        string ivaccount;
        string ivtime;
        string retstr;
        while ((ivname = extract(tmp, " <td bgcolor=", "#FFFFFF", "></a> -->", " </div>")) != "") {
            ivaccount = extract(tmp, "#FFFFFF", "color:red\">", "￥"," </div>");
            ivtime = extract(tmp, "</a> -->", "￥", "0 5px;\">", "</div>");
            ivtime = longtostring(stringtotime(ivtime.c_str(), "%Y-%m-%d %H:%M"));
            retstr += ivname + "|" + ivtime + "|" + ivaccount + "|";
            if (tmp.find("<tr style=\"height: 30px;\">") == string::npos) {
                break;
            }
            tmp = tmp.substr(tmp.find("<tr style=\"height: 30px;\">") + 1);
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
