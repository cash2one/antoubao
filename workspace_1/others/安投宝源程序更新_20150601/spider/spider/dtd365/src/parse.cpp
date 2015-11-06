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
       
    kv["site_id"] = "dtd365";
    kv["borrower"] = extract(bstr, "class=\"w200\">","出让人：",";","</span>");
    kv["project_name"] = extract(bstr, "class=\"fl\">", "class=\"p2pItemTit\"", ">","</h1>");
    kv["project_id"] = idstr;
    kv["borrowing_amount"] = num_util(extract(bstr, "class=\"fl\">","class=\"item-props\">", "￥", "</strong>"));
    kv["annulized_rating"] = extract(bstr, "class=\"item-props\">", "<p>", "", "%");
    kv["payment_method"] = extract(bstr, "class=\"detailtb\"", "还款方式：", "<td>", "</td>");
    kv["loan_period"] = loanperiod_util(extract(bstr, "借款金额","class=\"item-props\">","<p>","</p>"));
//    kv["invested_amount"] = "";
    
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

            string::size_type spos = tmp.find("投资人");
            //string::size_type epos = tmp.find("");
            if (spos == string::npos) {
                continue;
            }
            //tmp = tmp.substr(spos + 1, epos - spos - 1);
            string ivname;
            string ivaccount;
            string ivtime;
            while ((ivname = extract(tmp, "<tr>", "<th>", "<th>", "</th>")) != "") {
                ivaccount = extract(tmp, "<tr>", "</th>", "￥","</th>");
                ivtime = extract(tmp, "￥", "<th>", "<th>", "</th>");
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
