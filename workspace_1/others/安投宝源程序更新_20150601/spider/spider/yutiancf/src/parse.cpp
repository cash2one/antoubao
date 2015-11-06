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

    

    kv["site_id"] = "yutiancf";
    kv["borrowing_amount"] = num_util(extract(bstr,"id=\"invest_main2\">","货款金额：", "￥","</span>"));
    kv["project_id"] = idstr;
    kv["project_name"] = extract(bstr, "id=\"invest_main2\">", "<tr>", "<td>", "</td>");
    kv["annulized_rating"] = extracthtml(bstr, "id=\"invest_main2\">", "年化利率：", "class=\"fc3\">", "%");
    kv["payment_method"] = extract(bstr,"id=\"invest_main2\">", "还款方式：", "","</span>");
    kv["loan_period"] = loanperiod_util(extract(bstr,"id=\"invest_main2\">","还款期限：","","</span>"));
    kv["borrower"] = extract(bstr,"class=\"invest2_table3\">","用户ID","class=\"td1\">","</td>");
    kv["invested_amount"] = doubletostring(s_atod(kv["borrowing_amount"].c_str()) - s_atod(filternum(extract(bstr,"class=\"invest2_block2\">","剩余可投","￥","</span>")).c_str()));    
    
    
    sprintf(filename, "html/%s", idstr);
    buf = readfile(filename);

    int investornum = 0;
    {
        string retstr;
        string::size_type tmp =  bstr.find("投标记录");
        if(tmp != string::npos){
            tmp = bstr.find("投标人",tmp+1);
        }
        if(tmp != string::npos){
            tmp =  bstr.find("<tr",tmp+1);
        }
        if(tmp != string::npos){

            string striv = bstr.substr(tmp);
            string ivname;
            string ivaccount;
            string ivtime;
            while ((ivname = extract(striv,  "</td>", "<td", ">", "</td>")) != "") {
                ivaccount = filternum(extract(striv, "元", "</td>", ">", "</td>"));
                ivtime = extract(striv, "元", "元", "</td>", "</td>");
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

