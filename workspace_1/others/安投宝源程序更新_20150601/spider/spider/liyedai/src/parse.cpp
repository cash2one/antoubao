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
    kv["site_id"] = "liyedai";
    kv["project_name"] = extract(bstr, "</script><div class=", "<span class=", "bottom:12px;\">","<i class=\"");
  //  kv["borrower"] = extract(bstr,"<div class=\"top-l\">","<span class=","title=\"","");
    kv["project_id"] = extract(bstr,"</script><input","id=\"in_id"," value=\"","\"/>");
    kv["borrowing_amount"] = extract(bstr,"% </p>","年化收益","class=\"f22\">","</p>");
    string::size_type pos = kv["borrowing_amount"].find("万");
    if (pos != string::npos){
        kv["borrowing_amount"] = doubletostring(atof(filternum(kv["borrowing_amount"]).c_str())*10000);
    } else{
        kv["borrowing_amount"] = doubletostring(atof(filternum(kv["borrowing_amount"]).c_str()));
    }  

    kv["annulized_rating"] = filternum(extract(bstr,"<ul>","<li class=\"lineb\">", "class=\"f22\">", "</span>%"));
    kv["payment_method"] = extract(bstr,"<tr>","<td><i class=","还款方式：","</td>");
    kv["loan_period"] = extract(bstr, "债权总额", "<li class=\"lineb\">", "class=\"f22\">","</p>");
    int pos1 = kv["loan_period"].find("月");
    if (pos1 != -1) {
        kv["loan_period"] = longtostring(atof(kv["loan_period"].c_str())*30);
    }
    else{

        kv["loan_period"] = longtostring(atof(kv["loan_period"].c_str()));
    }

    // kv["invested_amount"] = doubletostring(s_atod(kv["borrowing_amount"].c_str()) - s_atod(filternum(extract(bstr,"剩余时间","额","￥","")).c_str()));
    long long etime1 = stringtotime(extract(bstr,"<table class=","<td><i class=","发布时间：","</td>").c_str(), "%Y-%m-%d %H:%M:%S");
    if (etime1 > 1000000000) {
         kv["release_time"] = longtostring(etime1);
    }
  //   kv["end_time"] = extract(bstr,"<ul class=\"d_date\">","<s>","满标时间：","</li>");  
  //  kv["project_details"] = extract(bstr,"role=\"tablist\">","借款详情","id=\"jkxq\">","<div class=\"bid_jkzl\">");
    {
            string tmp;
            string::size_type startpos = bstr.find("状态");
            if (startpos != string::npos) {
                string::size_type endpos = bstr.find("</table>", startpos);
                if (endpos != string::npos) {
                    tmp = bstr.substr(startpos, endpos - startpos);
                }
            }
            string ivname;
            string ivaccount;
            string ivtime;
            string retstr;
         //   tmp = tmp.substr(tmp.find("</tr>") + 1);
            while ((ivname = extract(tmp, "</tr>", "<tr>", "<td>", "</td>")) != "") {
                ivaccount = extract(tmp, "<td><span>", "%</span></td>", "￥","</b></td>");
                ivtime = extract(tmp, "</b></td>", "</span></td>", "center\">", "</td>");
                ivtime = longtostring(stringtotime(ivtime.c_str(), "%Y-%m-%d %H:%M:%S")
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
