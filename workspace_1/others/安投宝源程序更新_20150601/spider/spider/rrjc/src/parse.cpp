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
    kv["site_id"] = "rrjc";
//    kv["borrower"] = extract(bstr,"<span class=\"cf_title\">","昵  称","\">","");
    kv["project_name"] = extract(bstr,"li_tittlebg\">","><span class=","\">","</span>");
    kv["project_id"] = extract(bstr,"<body>","<input type=","value=\"","\" id=");
    kv["borrowing_amount"] = filternum(extract(bstr, "金额","<tr class=\"f22","<div align=\"center\">","<span class"));
    kv["annulized_rating"] = filternum(extract(bstr, "预期收益", "元</span", "fya1\">", "%<span style"));
    kv["loan_period"] = extract(bstr, "预期收益", "<em></em>", "<div align=\"center\">","</span>");
    int pos1 = kv["loan_period"].find("月");
    if (pos1 != -1) {
        kv["loan_period"] = longtostring(atof(kv["loan_period"].c_str())*30);
    }
    else{
        kv["loan_period"] = longtostring(atof(kv["loan_period"].c_str()));
    }
    kv["invested_amount"] = longtostring(s_atol(kv["borrowing_amount"].c_str()) - s_atol(filternum(extract(bstr,"<p class=","剩余可投金额","\">","</b>元")).c_str()));
    long long etime1 = stringtotime(extract(bstr,"<p class=","发布时间","：","</p>").c_str(), "%Y.%m.%d");
    if (etime1 > 1000000000) {
        kv["release_time"] = longtostring(etime1);
    }
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

            string::size_type spos = tmp.find("状态");
            string::size_type epos = tmp.find("<div class=\"page\">");
            if (spos == string::npos || epos == string::npos) {
                continue;
            }
            tmp = tmp.substr(spos + 1, epos - spos - 1);
            string ivname;
            string ivaccount;
            string ivtime;
            tmp = tmp.substr(tmp.find("<div class=\"li_gaoliang\">") + 1);
            while ((ivname = extract(tmp, "FFFFFF\">", "</td>", "FFFFFF\">", "</td>")) != "") {
                ivaccount = extract(tmp, "FFFFFF\">", "FFFFFF\">", "FFFFFF\">","</td>");
                ivtime = extract(tmp, "*</td>", "FFFFFF\">", "FFFFFF\">", "</td>");
                ivtime = longtostring(stringtotime(ivtime.c_str(), "%Y.%m.%d %H:%M:%S")
                        );
                retstr += ivtime + "|" + ivname + "|" + ivaccount + "|";
                string::size_type pos = tmp.find("<div class=\"li_gaoliang\">");
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
    
    
