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

    kv["site_id"] = "dfjr580";
    kv["borrowing_amount"] = num_util(extract(bstr,"class=\"zqzrList3\">","融资金额", "<p>","</p>"));
    kv["project_id"] = idstr;
    kv["project_name"] = extract(bstr, "class=\"person_rzxqzqzr1\">", "class=\"zqzrTitle\"", ">", "</div>");
    kv["annulized_rating"] = extracthtml(bstr, "class=\"zqzrList\">", "预期年化收益率", "<u>", "%");
    kv["payment_method"] = extract(bstr,"class=\"zqzrList4\">", "还款方式", "<p>","</p>");
    //kv["invested_amount"] = "";
    kv["loan_period"] = loanperiod_util(extract(bstr,"class=\"zqzrList2\">","剩余回报周期","原项目回报周期:","</span>"));
    kv["borrower"] = extract(bstr,"class=\"firstP\">","用户昵称：","<span>","</span>");

    printf(filename, "html/%s", idstr);
    buf = readfile(filename);

    int investornum = 0;
    {
        string retstr;
        string::size_type tmp =  bstr.find("tzjl_title");
        if(tmp != string::npos){
            tmp = bstr.find("投资人",tmp+1);
        }
        if(tmp != string::npos){
            tmp =  bstr.find("<p>",tmp+1);
        }
        if(tmp != string::npos){

            string striv = bstr.substr(tmp);
            string ivname;
            string ivaccount;
            string ivtime;
            while ((ivname = extract(striv, "<div", "</div>", ">", "</div>")) != "") {
                ivaccount = filternum(extract(striv, "</div>", "</div>", "<u>", "</u>"));
                ivtime = extract(striv, "tzjl_title6", "tzjl_title7", ">", "</div>");
                ivtime = longtostring(stringtotime(ivtime.c_str(), "%Y-%m-%d %H:%M:%S"));
                if (striv.find("tzjl_title7") == string::npos) {
                    break;
                }
                striv = striv.substr(striv.find("tzjl_title7") + 1);

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

