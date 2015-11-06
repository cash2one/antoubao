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
       
    kv["site_id"] = "jubaocn";
    //kv["borrower"] = "";               
    kv["project_name"] = extract(bstr, "class=\"box1\">", "<li>", "class=\"box1_title\">","</span>");
    kv["project_id"] = idstr;
    kv["borrowing_amount"] = num_util(extract(bstr, "class=\"box1\">","<li>", "借款金额：", "元"));
    kv["annulized_rating"] = extract(bstr, "class=\"box1\">", "借款利率：", "", "%");
    kv["payment_method"] = extract(bstr, "class=\"box1\">", "还款方式：", "", "</li>");
    kv["loan_period"] = loanperiod_util(extract(bstr, "class=\"box1\">","借款期限：","","</li>"));
    //kv["release_time"] = "";
//    kv["invested_amount"] = longtostring(s_atol(kv["borrowing_amount"].c_str()) - s_atol(filternum(extract(bstr,"class=\"fxndetail_left_jd\">","满标还差:","<dt>","元")).c_str())); 
    
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

            string::size_type spos = tmp.find("<tr>");
            //string::size_type epos = tmp.find("");
            if (spos == string::npos) {
                continue;
            }
            //tmp = tmp.substr(spos + 1, epos - spos - 1);
            string ivname;
            string ivaccount;
            string ivtime;
            while ((ivname = extract(tmp, "<td>", "<td>", "", "</td>")) != "") {
                ivaccount = extract(tmp, "</td>", "</td>", "</td>","元");
                ivtime = extract(tmp, "元", "<td>", "", "</td>");
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
