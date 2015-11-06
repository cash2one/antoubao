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
    kv["site_id"] = "pccb";
  //  kv["borrower"] = extract(bstr, "<tbody>", "用户ID", "<td>","");
    kv["project_name"] = extract(bstr,"</div><div class=","revealFont fl\">","您选择的是","、");
    kv["project_id"] = extract(bstr,"cellspacing=\"0\"><tr><td width=","</td><td width=\"","/invest/report/bid/","\" target=");
    kv["borrowing_amount"] = extract(bstr, "cellspacing=\"0\">", "<th style=\"width:25%;\">","￥","</th><th>");
    string::size_type pos = kv["borrowing_amount"].find("万");
    if (pos != string::npos){
        kv["borrowing_amount"] = doubletostring(atof(filternum(kv["borrowing_amount"]).c_str())*10000);
    } else{
        kv["borrowing_amount"] = doubletostring(atof(filternum(kv["borrowing_amount"]).c_str()));
    }  

    kv["annulized_rating"] = filternum(extract(bstr,"id=\"invest_notice", "项目期限", "预期年化收益率：", "%</span><span>"));
    kv["award"] = extract(bstr,"<span class=\"cybft cybft1\">","%</span><span class=","+</span>","<span class=\"cybft cybft1\">");
    kv["payment_method"] = extract(bstr,"<td width=\"215\">","收益方式 ","class=\"red\">","</span></td></tr><tr><td>");
    kv["loan_period"] = extract(bstr, "class=\"revealFont fl", "id=\"invest_notice", "项目期限：","</span><span>预");
    int pos1 = kv["loan_period"].find("月");
    if (pos1 != -1) {
        kv["loan_period"] = longtostring(atof(kv["loan_period"].c_str())*30);
    }
    else{

        kv["loan_period"] = longtostring(atof(kv["loan_period"].c_str()));
    }

    kv["invested_amount"] = doubletostring(s_atod(kv["borrowing_amount"].c_str()) - s_atod(filternum(extract(bstr,"已投金额","<span class=\"red\">","￥","</span></td><td>")).c_str()));
     kv["release_time"] = extract(bstr,"已投金额","还差金额","</span></td><td>","准点发布");
    kv["project_details"] = extract(bstr,"target=\"_blank\"","<div class=\"tab_title tab_title_0\">","项目概述","<img src=\"http://");
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

            string::size_type spos = tmp.find("投资时间</th>");
            if (spos != string::npos) {
                spos = tmp.find("<tr>", spos+1);
            }
            string::size_type epos = string::npos;
            if (spos != string::npos) {
                epos = tmp.find("条记录");
            }
            if (spos == string::npos || epos == string::npos ) {
                continue;
            }
            tmp = tmp.substr(spos + 1, epos - spos - 1);
            string ivname;
            string ivaccount;
            string ivtime;
            while ((ivname = extract(tmp,  "<td", ">", "", "</td>")) != "") {
                ivaccount = extract(tmp, "%", "</td>", "","</td>");
                ivtime = extract(tmp,  "%","title=\"", "</td>", "</td></tr>");
                ivtime = longtostring(stringtotime(ivtime.c_str(), "%Y-%m-%d %H:%M:%S"));
                retstr += ivtime + "|" + ivname + "|" + ivaccount + "|";
                string::size_type pos = tmp.find("<tr><td style=\"background:#EFEFEF");
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
