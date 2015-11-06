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
    kv["site_id"] = "subangloan";
    kv["borrower"] = extract(bstr,"<span class=\"cf_title\">","昵  称","\">","</span>");
    kv["project_name"] = extract(bstr,"<div class=\"project_dl\">","项目名称","title=\"","\">");
    kv["project_id"] = extract(bstr,"<div class=\"loan-bg\">","<div class=\"loan_top \">","data-loanId=\"","\" id=");
    kv["borrowing_amount"] = filternum(extract(bstr, "标的总额","<span></span><span","\">","</span></li>"));
    kv["annulized_rating"] = filternum(extract(bstr, "年利率", "\" id=\"", "\">", "</span><span"));
    kv["payment_method"] = extract(bstr,"保障方式","还款方式","\">","</span></div>");
    kv["loan_period"] = extract(bstr, "还款期限", "\" id=\"", "\">","</span></li>");
    if (extract(bstr, "还款期限", "", "", "</span></li>").find("月") != string::npos) {
        kv["loan_period"] = doubletostring(atof(kv["loan_period"].c_str())*30); 
    }
    kv["invested_amount"] = longtostring(s_atol(kv["borrowing_amount"].c_str()) - s_atol(filternum(extract(bstr,"可投金额","￥","\">","</span>")).c_str()));
    kv["project_details"] = extract(bstr,"<div class=\"clear\">","<div class=\"project","项目情况：","<div class=\"loan_company loan-bg\">");
    {
        string::size_type spos = bstr.find("<ul class=\"loan_bidding_list_ul2\">");
        if (spos != string::npos) {
            string tmp= bstr.substr(spos + 1);;
            string ivname;
            string ivaccount;
            string ivtime;
            string retstr;
            int invnum = 0;
            while ((ivname = extract(tmp, "<li>", "", "", "</li>")) != "") {
                ivaccount = extract(tmp, "<li>", "￥", "\">","</span>");
                ivtime = "-1";
                retstr += ivtime + "|" + ivname + "|" + ivaccount + "|";
                invnum++;
                spos = tmp.find("<ul class=\"loan_bidding_list_ul2\">");
                if (spos == string::npos) {
                    break;
                }
                tmp = tmp.substr(spos+1);
            }
            kv["investor"] = retstr;
        }
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
