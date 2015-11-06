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
    kv["site_id"] = "rongjintong";
//    kv["borrower"] = "";
    kv["project_name"] = extract(bstr, "class=\"content clearfix\">","<a",">","</a>");
    kv["project_id"] = idstr;
    kv["borrowing_amount"] = filternum(extract(bstr, "借款金额", "<tr>", ">", "</td>"));
    kv["annulized_rating"] = filternum(extracthtml(bstr, "借款金额","30px;\">","30px;\">", "%"));
    kv["payment_method"] = extract(bstr, "借款金额", "还款方式：", "", "</td>");
    kv["loan_period"] = loanperiod_util(extract(bstr,"借款金额","<tr>","%","</tr>"));
    kv["release_time"] = longtostring(stringtotime(extract(bstr, "class=\"content clearfix\">","<tbody>","发布日期：","</td>").c_str(), "%Y-%m-%d"));

    printf(filename, "html/%s", idstr);
    buf = readfile(filename);

    int investornum = 0;
    {
        string retstr;
        string::size_type tmp =  bstr.find("投标记录");
        if(tmp != string::npos){
            tmp = bstr.find("投标人",tmp+1);
        }
        if(tmp != string::npos){
            tmp =  bstr.find("<tr>",tmp+1);
        }
        if(tmp != string::npos){

            string striv = bstr.substr(tmp);
            string ivname;
            string ivaccount;
            string ivtime;
            while ((ivname = extract(striv, "<td>", "", "", "</td>")) != "") {
                ivaccount = filternum(extract(striv, "%", "￥", "￥", "</td>"));
                ivtime = extract(striv, "￥", "￥", "<td>", "</td>");
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

