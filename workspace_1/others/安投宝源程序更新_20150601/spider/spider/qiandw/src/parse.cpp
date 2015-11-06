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
    kv["site_id"] = "qiandw";
    string brr = extract(bstr, "<table class=", "融资企业", "td2\">","</td>");
    if (brr != "") {
        kv["borrower"] = brr;
    }
    kv["project_name"] = extract(bstr,"</span>","<h1 class=", "\">", "</h1>");
    kv["project_id"] = idstr;
    kv["borrowing_amount"] = num_util(extract(bstr, "<table style=", "<span style=","&#165;", "</span>"));
    kv["annulized_rating"] = filternum(extract(bstr, "&#165","<td style=", "\">", "</span><span"));
    kv["payment_method"] = extract(bstr,"</table>","table\">", "></div>","</td>");
    kv["loan_period"] = loanperiod_util(extract(bstr, "<table style", "%</span>", "\">","</td>"));
     int pos1 = kv["loan_period"].find("月");
      if (pos1 != -1) {
          kv["loan_period"] = longtostring(atof(kv["loan_period"].c_str())*30);
           }
      else{ 
          kv["loan_period"] = longtostring(atof(kv["loan_period"].c_str()));
      }
    kv["remanent_amount"] = extract(bstr,"<div style","可投金额","&#165;","</span>元");
    string remanent;
    for (size_t i = 0; i < kv["remanent_amount"].size(); i++) {
        if (kv["remanent_amount"][i] != ',') {
            remanent += kv["remanent_amount"][i];
             }
    }
    kv["remanent_amount"] = remanent;
    kv["release_time"] = longtostring(stringtotime(extract(bstr,"可投金额","</span>元</div>","\">","开始售出").c_str(), "%m-%d %H:%M"));
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

            string::size_type spos = tmp.find("</thead>");
            string::size_type epos = tmp.find("</tbody>");
            if (spos == string::npos || epos == string::npos) {
                continue;
            }
            tmp = tmp.substr(spos + 1, epos - spos - 1);
            string ivname;
            string ivaccount;
            string ivtime;
            while ((ivname = extract(tmp, "<tr class=", "<td class", "\">", "</td>")) != "") {
                ivaccount = num_util(extract(tmp, "<td class=", "<td class=", "&#165;","</td>"));
                ivtime = extract(tmp, "<td class=", "<td class=", "\">", "</td>");
                ivtime = longtostring(stringtotime(ivtime.c_str(), "%Y-%m-%d %H:%M:%S"));
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
