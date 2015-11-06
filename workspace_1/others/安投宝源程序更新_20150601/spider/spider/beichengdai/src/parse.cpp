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

    kv["site_id"] = "beichengdai";
    kv["borrowing_amount"] = num_util(extract(bstr,"class=\"mainTop_bd\">","筹集金额", "￥","元"));
    kv["project_id"] = idstr;
    kv["project_name"] = extract(bstr, "main_top clearfix", "mainTop_left", "<span>", "</span>");
    kv["annulized_rating"] = extracthtml(bstr, "class=\"mainTop_bd\">", "年利率", "class=\"f22\">", "%");
    kv["payment_method"] = extract(bstr,"class=\"mainTop_item clearfix\">", "还款方式", "<dd>","</span>");
   // kv["invested_amount"] = ;
    kv["loan_period"] = loanperiod_util(extract(bstr,"class=\"mainTop_item clearfix\">","借款期限","<dd>","</dd>"));
    kv["borrower"] = extract(bstr,"lass=\"tab_con\">","借款人：","</span>","</li>");

    printf(filename, "html/%s", idstr);
    buf = readfile(filename);

    int investornum = 0;
    {
        string retstr;
        string::size_type tmp =  bstr.find("目前总投标金额");
        if(tmp != string::npos){
            tmp = bstr.find("投资人",tmp+1);
        }
        if(tmp != string::npos){
            tmp =  bstr.find("<tr>",tmp+1);
        }
        if(tmp != string::npos){

            string striv = bstr.substr(tmp);
            string ivname;
            string ivaccount;
            string ivtime;
            while ((ivname = extract(striv, "<td", "<!--", "-->", "<!--")) != "") {
                ivaccount = filternum(extract(striv, "<td", "</td>", "￥", "</td>"));
                ivtime = extract(striv, "</td>", "</td>", ">", "</td>");
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

