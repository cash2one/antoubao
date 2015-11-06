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
    kv["site_id"] = "zrcaifu";
//    kv["borrower"] = extract(bstr, "<div class=", "<div class=\"tbname\">", "\">","");
    kv["project_name"] = extract(bstr,"<html>","<head>","<title>","-投资理财");
    kv["project_id"] = extract(bstr,"<div id=\"Zr_","project-title","data-id='","'>");
    kv["borrowing_amount"] = extract(bstr, "项目金额", "value-detail\">","big-number'>","</div>");
    string::size_type pos = kv["borrowing_amount"].find("万");
    if (pos != string::npos){
        kv["borrowing_amount"] = doubletostring(atof(filternum(kv["borrowing_amount"]).c_str())*10000);
    } else{
        kv["borrowing_amount"] = doubletostring(atof(filternum(kv["borrowing_amount"]).c_str()));
    }  

    kv["annulized_rating"] = filternum(extract(bstr,"预期年化收益", "value-detail\">", "big-number'", "</span><span"));
    kv["payment_method"] = extract(bstr,"<div class=\"col2\">","还款方式","<span>","</span></p>");
    kv["loan_period"] = extract(bstr, "投资周期", "value-detail\">", "big-number\">","天");
    int pos1 = kv["loan_period"].find("月");
    if (pos1 != -1) {
        kv["loan_period"] = longtostring(atof(kv["loan_period"].c_str())*30);
    }
    else{

        kv["loan_period"] = longtostring(atof(kv["loan_period"].c_str()));
    }

 //   kv["invested_amount"] = doubletostring(s_atod(kv["borrowing_amount"].c_str()) - s_atod(filternum(extract(bstr,"剩余时间","额","￥","</em></div>")).c_str()));
     long long etime1 = stringtotime(extract(bstr,"<div class=\"col1\">","发布日期：","<span>","</span></p>").c_str(), "%Y-%m-%d");
     if (etime1 > 1000000000) {
         kv["release_time"] = longtostring(etime1);
     }

  //  kv["project_details"] = extract(bstr,"<div class=\"clr\">","<div class=\"inv-menu\">","借款描述","<div class=\"clr\">");
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

            string::size_type spos = tmp.find("投资金额");
            string::size_type epos = tmp.find("</table>");
            if (spos == string::npos || epos == string::npos) {
                continue;
            }
            tmp = tmp.substr(spos + 1, epos - spos - 1);
            string ivname;
            string ivaccount;
            string ivtime;
            tmp = tmp.substr(tmp.find("<tr class=''>") + 1);
            while ((ivname = extract(tmp, "&nbsp;&nbsp;", "</td>", "<td>", "</td>")) != "") {
                ivaccount = extract(tmp, "</td>", "</td>", "<td>","元</td>");
                ivtime = extract(tmp, "", "<td>", "&nbsp;", "</td>");
                ivtime = longtostring(stringtotime(ivtime.c_str(), "%Y-%m-%d %H:%M:%S")
                        );
                retstr += ivtime + "|" + ivname + "|" + ivaccount + "|";
                string::size_type pos = tmp.find("<tr class=''>");
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
