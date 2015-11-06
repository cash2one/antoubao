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
    kv["site_id"] = "zjsdai";
    kv["borrower"] = extract(bstr, "class=\"data-list\">", "class=\"tal\"", "借款人资料", "<!-- data list -->");
    //kv["credit_rating"] = "";
    kv["project_name"] = extract(bstr, "class=\"tab-con1\">", "class=\"item clearfix\">", "\">", "</h2>");
    kv["project_id"] = idstr ;
    kv["borrowing_amount"] =filternum(extract(bstr, "class=\"basic-info\">","class=\"clearfix\">", "借款金额：","元"));
    kv["annulized_rating"] =filternum(extract(bstr, "class=\"basic-info\"", "class=\"clearfix\">","年利率：", "%"));
    //kv["payment_method"] = "";
    kv["award"] = filternum(extract(bstr,"class=\"basic-info\"","class=\"clearfix\">","奖　　励：","%"));
    kv["loan_period"] = loanperiod_util(extract(bstr,"class=\"basic-info\"","class=\"clearfix\">","借款期限：","<"));
    kv["minimum_investment"] = extract(bstr,"class=\"basic-info\"","class=\"clearfix\">","最小投资额：￥","</li>" );
    kv["maximum_investment"] = extract(bstr,"class=\"basic-info\"","class=\"clearfix\">","最大投资额：","</li>" );
    kv["invested_amount"] = doubletostring(s_atod(kv["borrowing_amount"].c_str())
            - s_atod(filternum(extract(bstr, "div class=\"basic-info\"", "发布时间", "差：", "<")).c_str()));
    kv["project_details"] = extract(bstr,"class=\"borrowings\">", "借款介绍", "class=\"data-list\">", "</td>");
    kv["release_time"] = longtostring(stringtotime(extract(bstr,"class=\"basic-info\"","class=\"clearfix\">","发布时间：","</li>").c_str(), "%Y-%m-%d %H:%M:%S"));

    printf(filename, "html/%s.brec", idstr);
    buf = readfile(filename);

    {
        string retstr;
        string::size_type tmp =  bstr.find("投标记录");
        if(tmp != string::npos){
            tmp = bstr.find("投标人", tmp+1);
        }
        if(tmp != string::npos){
            tmp =  bstr.find("<tbody>",tmp+1);
        }
        if(tmp != string::npos){

            string striv = bstr.substr(tmp);
            string ivname;
            string ivaccount;
            string ivtime;
            while ((ivname = extract(striv, "", "<tr>", "<td>", "</td>")) != "") {
                ivaccount = filternum(extract(striv, "</td>", "</td>", "￥", "</td>"));
                ivtime = extract(striv, "￥", "￥", "<td>", "</td>");
                ivtime = longtostring(stringtotime(ivtime.c_str(), "%Y-%m-%d %H:%M:%S"));
                if (striv.find("</tr>") == string::npos) {
                    break;
                }
                striv = striv.substr(striv.find("</tr>") + 1);

                retstr += ivtime + "|" + ivname + "|" + ivaccount + "|";
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

