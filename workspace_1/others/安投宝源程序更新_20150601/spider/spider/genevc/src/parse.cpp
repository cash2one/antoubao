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
    kv["site_id"] = "genevc";
    kv["project_name"] = extract(bstr, "<li><p><span", "标号：", "\">","</em></span>");
    kv["borrower"] = extract(bstr,"<p class=","用户昵称","</span>","</p>");
    kv["project_id"] = extract(bstr,"<a class=\"lookA","><input class=","investPage&id=","','_");
    kv["borrowing_amount"] = extract(bstr,"<li><p><span><em","债权总额","\">","</span><em style=");
    string::size_type pos = kv["borrowing_amount"].find("万");
    if (pos != string::npos){
        kv["borrowing_amount"] = doubletostring(atof(filternum(kv["borrowing_amount"]).c_str())*10000);
    } else{
        kv["borrowing_amount"] = doubletostring(atof(filternum(kv["borrowing_amount"]).c_str()));
    }  

    kv["annulized_rating"] = filternum(extract(bstr,"<li><p><span><em","年化利率", "&nbsp;&nbsp;", "%</em></span"));
    kv["payment_method"] = extract(bstr,"<li><p><em style","还款方式","nbsp;&nbsp;","</em></p>");
    kv["loan_period"] = extract(bstr, "<li><p><span><em", "回购期限", "&nbsp;&nbsp;","</em></p></li>");
    int pos1 = kv["loan_period"].find("月");
    if (pos1 != -1) {
        kv["loan_period"] = longtostring(atof(kv["loan_period"].c_str())*30);
    }
    else{

        kv["loan_period"] = longtostring(atof(kv["loan_period"].c_str()));
    }

    // kv["invested_amount"] = doubletostring(s_atod(kv["borrowing_amount"].c_str()) - s_atod(filternum(extract(bstr,"剩余时间","额","￥","")).c_str()));
   //  kv["release_time"] = extract(bstr,"还款方式","发布时间","\">","</span>");
   //    kv["end_time"] = extract(bstr,"<ul class=\"d_date\">","<s>","满标时间：","</li>");  
  //  kv["project_details"] = extract(bstr,"role=\"tablist\">","借款详情","id=\"jkxq\">","<div class=\"bid_jkzl\">");
    {
        sprintf(filename, "html/%s", idstr);
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
            string::size_type epos = tmp.find("</table>");
            if (spos == string::npos || epos == string::npos) {
                continue;
            }
            tmp = tmp.substr(spos + 1, epos - spos - 1);
            string ivname;
            string ivaccount;
            string ivtime;
            tmp = tmp.substr(tmp.find("</tr>") + 1);
            while ((ivname = extract(tmp, "","<tr>", "<td>", "</td>")) != "") {
                ivaccount = num_util(extract(tmp, "%</td>", "</td>", "<td>","元</td>"));
                ivtime = extract(tmp, "%</td>", "元</td>", "<td>", "</td>");
                ivtime = longtostring(stringtotime(ivtime.c_str(), "%Y-%m-%d %H:%M"));
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

    if (kv["project_id"] == "" || s_atod(kv["borrowing_amount"].c_str()) <= 0) {
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
    
    
