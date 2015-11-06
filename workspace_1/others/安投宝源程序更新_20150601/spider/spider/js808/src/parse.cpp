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
    kv["site_id"] = "js808";
    kv["borrower"] = extract(bstr,"<ul class=\"right\">","用户名：","nickname\">","</span></li>");
    kv["project_name"] = extract(bstr, "<div class=\"module\">", "module_t\">", "Lab_title\">","<a class='hastooltip");
    kv["project_id"] = extract(bstr, "<body>","<form name=","Detail_New.aspx?id=","\" id=");
    kv["borrowing_amount"] = extract(bstr,"<ul class=","借款金额","￥","</span></span>");
    string::size_type pos = kv["borrowing_amount"].find("万");
    if (pos != string::npos){
        kv["borrowing_amount"] = doubletostring(atof(filternum(kv["borrowing_amount"]).c_str())*10000);
    } else{
        kv["borrowing_amount"] = doubletostring(atof(filternum(kv["borrowing_amount"]).c_str()));
    }  

    kv["annulized_rating"] = filternum(extract(bstr,"￥","年化利率", "Lab_nll\">", "%</span></span>"));
    kv["payment_method"] = extract(bstr,"</li>","还款方式","Lab_hkfs\">","</span></span>");
    kv["loan_period"] = extract(bstr, "年化利率", "借款期限", "Lab_qx\">","</span></span>");
    int pos1 = kv["loan_period"].find("月");
    if (pos1 != -1) {
        kv["loan_period"] = longtostring(atof(kv["loan_period"].c_str())*30);
    }
    else{

        kv["loan_period"] = longtostring(atof(kv["loan_period"].c_str()));
    }

     kv["release_time"] = extract(bstr,"已投标数","发标时间","Lab_fbdt\">","</span></li>");
  long long etime1 = stringtotime(extract(bstr,"已投标数","发标时间","Lab_fbdt\">","</span></li>").c_str(), "%Y/%m/%d %H:%M:%S");
   if (etime1 > 1000000000) {
        kv["release_time"] = longtostring(etime1);
   }
     //  kv["project_details"] = extract(bstr,"借款详情","资料审核","投标记录","");
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

            string::size_type spos = tmp.find("当前状态");
            string::size_type epos = tmp.find("</table>");
            if (spos == string::npos || epos == string::npos) {
                continue;
            }
            tmp = tmp.substr(spos + 1, epos - spos - 1);
            string ivname;
            string ivaccount;
            string ivtime;
            while ((ivname = extract(tmp, "</tr>", "<tr>", "<td>", "</td>")) != "") {
                ivaccount = extract(tmp, "<tr><td>", "</td><td>", "</td><td>","</td>");
                ivtime = extract(tmp, "</td><td>", "</td><td>", "</td><td>", "</td><td>");
                ivtime = longtostring(stringtotime(ivtime.c_str(), "%Y/%m/%d %H:%M:%S")
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
     
