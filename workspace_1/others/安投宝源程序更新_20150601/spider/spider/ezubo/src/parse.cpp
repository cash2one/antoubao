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
    kv["site_id"] = "ezubo";
//    kv["borrower"] = extract(bstr, "<div class=", "<div class=\"tbname\">", "\">","");
    kv["project_name"] = extract(bstr,"<meta http-equiv=","<title>","-","-");
    kv["project_id"] = extract(bstr,"invest-history-more\">","<a class=\"load-more","data-id=\"","\" ");
    kv["borrowing_amount"] = extract(bstr, "<p class=", "<p>","总额：","</p>");
    string::size_type pos = kv["borrowing_amount"].find("万");
    if (pos != string::npos){
        kv["borrowing_amount"] = doubletostring(atof(filternum(kv["borrowing_amount"]).c_str())*10000);
    } else{
        kv["borrowing_amount"] = doubletostring(atof(filternum(kv["borrowing_amount"]).c_str()));
    }  

    kv["annulized_rating"] = filternum(extract(bstr,"<div class=\"tlleft\">", "clearfix\">", "<em>", "<i>%</i>"));
    kv["payment_method"] = extract(bstr,"<p class=","赎回方式","underline\">","</span> </p>");
    kv["loan_period"] = extract(bstr, "<i>%</i>", "<div class=", "<em>","</i></em><br");
    int pos1 = kv["loan_period"].find("月");
    if (pos1 != -1) {
        kv["loan_period"] = longtostring(atof(kv["loan_period"].c_str())*30);
    }
    else{

        kv["loan_period"] = longtostring(atof(kv["loan_period"].c_str()));
    }

    kv["invested_amount"] = doubletostring(s_atod(kv["borrowing_amount"].c_str()) - s_atod(filternum(extract(bstr,"投资期限","divstyle03\">","可投：","/  总额")).c_str()));
    int pos2 = kv["invested_amount"].find("万");
    if (pos2 != -1) {
        kv["invested_amount"] = longtostring(atof(kv["invested_amount"].c_str())*10000);
    }
    else{
        kv["invested_amount"] = longtostring(atof(kv["invested_amount"].c_str()));
    }
    long long etime1 = stringtotime(extract(bstr,"<p class=","发布时间","&nbsp;","&nbsp").c_str(), "%Y-%m-%d");
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

            string::size_type spos = tmp.find("data");
            string::size_type epos = tmp.find("]");
            if (spos == string::npos || epos == string::npos) {
                continue;
            }
            tmp = tmp.substr(spos + 1, epos - spos - 1);
            string ivname;
            string ivaccount;
            string ivtime;
            while ((ivname = extract(tmp, "", "<tr>", "<td>", "<\\/td>")) != "") {
                ivaccount = extract(tmp, "<td>", "<\\/td>", "<td>","<\\/td>");
                ivtime = extract(tmp, "<\\/td>", "<\\/td>", "<td>", "<\\/td>");
                ivtime = longtostring(stringtotime(ivtime.c_str(), "%Y-%m-%d")
                        );
                retstr += ivtime + "|" + ivname + "|" + ivaccount + "|";
                string::size_type pos = tmp.find("<\\/tr>");
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

    if (kv["loan_period"] == "" ) {
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
