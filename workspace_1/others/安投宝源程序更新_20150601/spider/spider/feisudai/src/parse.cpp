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
    kv["site_id"] = "feisudai";
    string brr = extract(bstr, "</h1>", "num fl\">", "借款人：","</div>");
    if (brr != "") {
        kv["borrower"] = brr;
    }
    kv["project_name"] = extract(bstr,"</div><div id=","<div class=", "<h1 class=\"fl\">", "</h1>");
    kv["project_id"] = extract(bstr,"</h1>","num fr\">","项目编号：","</div>");
    kv["borrowing_amount"] = num_util(extract(bstr, "<li class=\"top\">", "<div id=\"money\">","￥", "</em>"));
    kv["annulized_rating"] = filternum(extract(bstr,"<div class=\"item\">","<div id=\"apr", "\">", "%"));
    kv["payment_method"] = extract(bstr,"投标进度","<div class=\"item\">", "<div>","</div>");
    kv["loan_period"] = loanperiod_util(extract(bstr, "<li class=\"top\">", "</div>", "<div id=\"time\">","</div>"));
//    double rm = s_atod(num_util(extract(bstr, "<div id=\"main\"", "<div class=\"ketou\">", "", "</div")).c_str());
 //   kv["invested_amount"] = doubletostring(s_atod(kv["borrowing_amount"].c_str()) - rm);
    long long etime1 = stringtotime(extract(bstr,"最小/最大投标金额","<div class=","<div>","</div>").c_str(), "%Y-%m-%d %H:%M:%S");
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

            string::size_type spos = tmp.find("</thead>");
            string::size_type epos = tmp.find("</table>");
            if (spos == string::npos || epos == string::npos) {
                continue;
            }
            tmp = tmp.substr(spos + 1, epos - spos - 1);
            string ivname;
            string ivaccount;
            string ivtime;
            while ((ivname = extract(tmp, "<tr>", "</td>", ">", "</td>")) != "") {
                ivaccount = num_util(extract(tmp, "</td>", "</td>", ">","</td>"));
                ivtime = extract(tmp, "", "<tr>", ">", "</td>");
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
