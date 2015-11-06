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
    kv["site_id"] = "cnssdai";
//    kv["borrower"] = "";
    kv["project_name"] = extract(bstr, "class=\"det_top\">","class=\"det_title\">","<h1>","</h1>");
    kv["project_id"] = idstr;
    kv["borrowing_amount"] = num_util(extract(bstr, "class=\"det_jd\">", "class=\"det_sj\">", "<li>", "</li>"));
    kv["annulized_rating"] = filternum(extracthtml(bstr, "class=\"det_sj\">","</li>","</li>", "%"));
    kv["payment_method"] = extract(bstr, "class=\"det_sj\">","%", "%", "</div>");
    kv["loan_period"] = loanperiod_util(extract(bstr, "class=\"det_jd\">","class=\"det_sj\">","</li>","</li>"));
    kv["release_time"] = longtostring(stringtotime(extract(bstr,"class=\"det_jd\">","发布时间：","<strong>","</strong>").c_str(),"%Y-%m-%d"));


    printf(filename, "html/%s", idstr);
    buf = readfile(filename);

    int investornum = 0;
    {
        string retstr;
        string::size_type tmp =  bstr.find("借款资料");
        if(tmp != string::npos){
            tmp = bstr.find("投标人",tmp+1);
        }
        if(tmp != string::npos){
            tmp =  bstr.find("<tr>",tmp+1);
        }
        string::size_type etmp = string::npos;
        if (tmp != string::npos) {
            etmp = bstr.find("</table>", tmp);
        }

        if(tmp != string::npos && etmp != string::npos){
            string striv = bstr.substr(tmp + 1, etmp - tmp - 1);
            string ivname;
            string ivaccount;
            string ivtime;
            while ((ivname = extract(striv, "<td", "<td", ">", "</td>")) != "") {
                ivaccount = filternum(extract(striv, "</td>", "</td>", "￥", "</td>"));
                ivtime = extract(striv, "￥", "￥", "</td>", "</td>");
                ivtime = longtostring(stringtotime(ivtime.c_str(), "%Y-%m-%d %H:%M:%S"));
                if (striv.find("</tr>") == string::npos) {
                    break;
                }
                striv = striv.substr(striv.find("</tr>") + 1);

                retstr += ivtime + "|" + ivname + "|" + ivaccount + "|";
                investornum++;
            }
        }
        kv["investor"] = retstr;
    }
    kv["investors_volume"] = longtostring(investornum);
    printstringmap(kv);


    if (kv["project_id"] == "" || s_atol(kv["borrowing_amount"].c_str()) <= 0) {
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

