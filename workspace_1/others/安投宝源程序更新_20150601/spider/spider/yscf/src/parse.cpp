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
    kv["site_id"] = "yscf";
    kv["project_name"] = extract(bstr, "<div class=\"clearfix\"", "<div class=\"f_20\"", "\">","</div>");
    kv["borrower"] = extract(bstr,"<td class=\"t_r\"","借款人","\">","</td>");
    kv["project_id"] = extract(bstr,"<span class=\"f_16","借款编号","\">","</span>");
    kv["borrowing_amount"] = extract(bstr,"借款金额","<br /> ","￥","</span>");
    string::size_type pos = kv["borrowing_amount"].find("万");
    if (pos != string::npos){
        kv["borrowing_amount"] = doubletostring(atof(filternum(kv["borrowing_amount"]).c_str())*10000);
    } else{
        kv["borrowing_amount"] = doubletostring(atof(filternum(kv["borrowing_amount"]).c_str()));
    }  

    kv["annulized_rating"] = filternum(extract(bstr,"年化收益率","<br />", "\">", "</span>"));
    kv["payment_method"] = extract(bstr,"还款方式","<br />","\">","</span>");
    kv["loan_period"] = extract(bstr, "借款期限", "<br />", "\">","</div> ");
    int pos1 = kv["loan_period"].find("月");
    if (pos1 != -1) {
        kv["loan_period"] = longtostring(atof(kv["loan_period"].c_str())*30);
    }
    else{

        kv["loan_period"] = longtostring(atof(kv["loan_period"].c_str()));
    }

    // kv["invested_amount"] = doubletostring(s_atod(kv["borrowing_amount"].c_str()) - s_atod(filternum(extract(bstr,"剩余时间","额","￥","")).c_str()));
  //   kv["release_time"] = extract(bstr,"还款方式","发布时间","\">","");
        kv["end_time"] = extract(bstr,"<span class=\"f_16\"","<input id=\"hidden\"","value=\"","\" />");
    kv["project_details"] = extract(bstr,"<div class=\"page_block\">","<a id=\"tab1\"","借款信息","<div class=\"mt_20 mb_20");
    
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

            string::size_type spos = tmp.find("<tr class=\"tb_tr_true\">");
            string::size_type epos = tmp.find("</table>");
            if (spos == string::npos || epos == string::npos) {
                continue;
            }
            tmp = tmp.substr(spos + 1, epos - spos - 1);
            string ivname;
            string ivaccount;
            string ivtime;
            while ((ivname = extract(tmp, "<td class=", "</td>", "\">", "</td>")) != "") {
                ivaccount = extract(tmp, "</td>", "%</td>", "\">","</td>");
                ivtime = extract(tmp, "%</td>", "</td>", "\">", "</td>");
                ivtime = longtostring(stringtotime(ivtime.c_str(), "%Y-%m-%d")
                        );
                retstr += ivtime + "|" + ivname + "|" + ivaccount + "|";
                string::size_type pos = tmp.find("<tr class=\"tb_tr_true\">");
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
    
