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
    
    kv["site_id"] = "hcdai";
    kv["project_name"] = extract(bstr,"class=\"jkInfoML\">"," class=\"jkInfoMLimg\" >","\">", "</strong>");
    kv["project_id"] = idstr;
    kv["borrowing_amount"] = num_util(extract(bstr, "class=\"jkInfoMR\">", "class=\"jkInfoMRT\"", "借款金额：", "</td>"));
    kv["annulized_rating"] = extract(bstr, "class=\"jkInfoMR\"", "class=\"jkInfoMRT\"", "年利率：", "%");
    kv["payment_method"] = extract(bstr,"class=\"jkInfoMR\"", "class=\"jkInfoMRT\"", "还款方式：","借款用途");
   // kv["release_time"] = "";
    kv["loan_period"] = loanperiod_util(extract(bstr,"class=\"jkInfoMR\"","class=\"jkInfoMRT\"","借款期限：","</span>"));
    kv["borrower"] = extract(bstr,"<div", "jkInfoMLfont lheight24 mgt10","借款人代码：","借款编号：");


    sprintf(filename, "html/%s.brec", idstr);
    buf = readfile(filename);
    string invstr = "";
    if (buf) {
        bstr = string(buf);
        free(buf);
        string::size_type tpos = bstr.find("出借人");
        if (tpos != string::npos) {
            tpos = bstr.find("<table", tpos + 1);
        }
        while (tpos != string::npos) {
            bstr = bstr.substr(tpos + 1);
            string ivtime;
            string ivname;
            string ivaccount;
            ivtime = longtostring(stringtotime(extract(bstr, "<tr>", "</td>", "</td>", "</td>").c_str(), "%Y-%m-%d %H:%M:%S"));
            ivname = extract(bstr, "<tr>", "<td", "align=\"center\">", "</td>");
            ivaccount = filternum(extract(bstr, "<tr>", "</td>", "align=\"center\">", "</td>"));
            if (ivname == "") {
                break;
            }
            invstr += ivtime + "|" + ivname + "|" + ivaccount + "|";
            tpos = bstr.find("</tr");
        }
    }
    kv["investor"] = invstr;

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

