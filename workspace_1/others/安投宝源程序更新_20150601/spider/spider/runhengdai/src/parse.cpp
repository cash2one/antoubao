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
        
    kv["site_id"] = "runhengdai";
    kv["project_name"] = extract(bstr, "class=\"bid_item\">", "class=\"pull-left\">", "<h3>","</h3>");    kv["project_id"] = idstr;
    kv["borrowing_amount"] = num_util(extract(bstr, "class=\"pull-left\">","借款总额", "</span>", "</li>"));  
    kv["annulized_rating"] = extract(bstr, "class=\"pull-left\">", "年化收益", "</span>", "%");
    kv["payment_method"] = extract(bstr, "class=\"even_info1\">", "还款方式", "</span>", "</li>");
    kv["loan_period"] = loanperiod_util(extract(bstr, "class=\"pull-left\">","借款期限","</span>","</li>"));  

    sprintf(filename, "html/%s.borrower", idstr);
    char *buff = readfile(filename);
    //kv["borrower"] = extract(bstr, "用户信息","借款人","</strong>","</li>");
    if (!buff) {
        return 1;
    }
    string bstrk = string(buff);
    free(buff);
    kv["borrower"] = extract(bstrk, "用户信息","借款人","</strong>","</li>");
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

            string::size_type spos = tmp.find("<tbody>");
            string::size_type epos = tmp.find("</tbody>");
            if (spos == string::npos || epos == string::npos) {
                continue;
            }
            tmp = tmp.substr(spos + 1, epos - spos - 1);
            string ivname;
            string ivaccount;
            string ivtime;
            while ((ivname = extract(tmp, "<td>", "</td>", "<td>", "</td>")) != "") {
                ivaccount = extract(tmp, "</td>", "</td>", "</td>","</td>");
                ivtime = extract(tmp, "tdl", "</td>", "</td>","</td>");
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
