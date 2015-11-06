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
    kv["site_id"] = "beifangdai";
    kv["borrower"] = extract(bstr,"style=\"margin-left: 55px","width=\"80\" height=\"85\"","<strong>","</strong>");
    kv["project_name"] = extract(bstr,"content=\"text/html","charset=utf-8\" http-equiv=\"Content-Type\">","title>","</title>");
    kv["project_id"] = extract(bstr,"<div class=\"borrow_info\">","借款编号","<label class=\"info_remainlend\">","</label>");
        kv["borrowing_amount"] = extract(bstr, "<div class=\"pop-tb-l\">", "借款金额", "<strong>￥", "</strong>");
    string::size_type pos = kv["borrowing_amount"].find("万");
    if (pos != string::npos){
        kv["borrowing_amount"] = doubletostring(atof(filternum(kv["borrowing_amount"]).c_str())*10000);
    } else{
        kv["borrowing_amount"] = doubletostring(atof(filternum(kv["borrowing_amount"]).c_str()));
    }  

    kv["annulized_rating"] = filternum(extract(bstr,"<div class=\"pop-tb-l\">", "<ul>", "年利率：", "</li>"));
    kv["payment_method"] = extract(bstr,"还需借款：","借款期限：","还款方式：","</li>");
    kv["loan_period"] = extract(bstr,  "已经完成", "还需借款", "借款期限：", "</li>");
    int pos1 = kv["loan_period"].find("月");
    if (pos1 != -1) {
        kv["loan_period"] = longtostring(atof(kv["loan_period"].c_str())*30);
    }
    else{

        kv["loan_period"] = longtostring(atof(kv["loan_period"].c_str()));
    }

     kv["invested_amount"] = doubletostring(s_atod(kv["borrowing_amount"].c_str()) - s_atod(filternum(extract(bstr,"剩余可投","input id=\"left_count\" value=\"0.00\" type=\"hidden\">","<span id=\"borrowInvestBalance\" class=\"info_remainlend\">","</span>")).c_str()));
     kv["release_time"] = extract(bstr,"<td style=\"height:26px;line-height:26px;\">","开放时间","<span style=\"font-size:14px;\">","</span>");
    kv["project_details"] = extract(bstr,"借款详情","class=\"detail_menu_one\">","img alt=","</div>");
    {
        sprintf(filename, "html/%s.brec", idstr);
        buf = readfile(filename);
        size_t buflen = strlen(buf);
        char *p = buf;
        string retstr;
        while (p < buf + buflen - 8) {
            int len;
            sscanf(p, "%08X", &len);
            p += 8;
            string tmp = string(p, len);
            p += len;

            string::size_type spos = tmp.find("投标时间");
            string::size_type epos = tmp.find("<div id=\"loanbid_record\"");
            if (spos == string::npos || epos == string::npos) {
                continue;
            }
            tmp = tmp.substr(spos + 1, epos - spos - 1);
            string ivname;
            string ivaccount;
            string ivtime;
            while ((ivname = extract(tmp, "<ul class", "tab_tq\">", "<li>", "</li>")) != "") {
                ivaccount = extract(tmp, "</li>", "%</li>", "<li>","</li>");
                ivtime = extract(tmp, "%</li>", "</li>", "<li>", "</li>");
                ivtime = longtostring(stringtotime(ivtime.c_str(), "%Y-%m-%d")
                        );
                retstr += ivtime + "|" + ivname + "|" + ivaccount + "|";
                string::size_type pos = tmp.find("<ul class=\"tab_tq\">");
                if (pos != string::npos) {
                    tmp = tmp.substr(pos + 1);
                }
                else {
                   break;
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
    
    
