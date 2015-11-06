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
    kv["site_id"] = "qian88";
    kv["borrower"] = extract(bstr, " class=\"jk_inf\">", "<ul>", "用 户 名：", "</li>");
    kv["project_name"] = extract(bstr, "class=\"til\">", "借款信息详情", "class=\"list_tit\">", "</h3>");
    kv["project_id"] = idstr;
    kv["borrowing_amount"] = filternum(extract(bstr, "class=\"txttab\">", "借款金额：", "￥", "</strong>"));
    kv["annulized_rating"] = extract(bstr, "class=\"txttab\">", "借款年利率：", "<strong>", "%");
    kv["payment_method"] = extract(bstr, "class=\"txttab\">", "还款方式：", "<strong>", "</strong>");
    kv["loan_period"] = extract(bstr, "class=\"txttab\">", "借款期限：", "<strong>", "</strong>");
    kv["loan_period"] = loanperiod_util(kv["loan_period"]);
    kv["release_time"] = "";

    sprintf(filename, "html/%s.brec", idstr);
    buf = readfile(filename);
    if (buf) {
        bstr = string(buf);
        free(buf);
    }

    int investornum = 0;
    {
        string retstr;
        string::size_type tmp =  bstr.find("投标人/关系");
        if(tmp != string::npos){
            tmp = bstr.find("<tr>", tmp+1);
        }
        if(tmp != string::npos){

            string striv = bstr.substr(tmp);
            string ivname;
            string ivaccount;
            string ivtime;
            while ((ivname = extract(striv, "<td", "align=\"center\"", "-->", "<")) != "") {
                ivaccount = filternum(extract(striv, "<td", "<td", "</td>", "</td>"));
                ivtime = extract(striv, "动", "<td","</td>", "</td>");
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

