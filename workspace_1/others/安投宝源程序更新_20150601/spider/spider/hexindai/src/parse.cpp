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
    kv["site_id"] = "hexindai";
    kv["borrower"] = extract(bstr,"<div class=\"invest_bid_info\"","借款人：",""," </");
    kv["project_name"] = extract(bstr,"<div id=\"content\">","<span class=\"title_con\">","","</");
    kv["project_id"] = idstr;
    kv["borrowing_amount"] = num_util(extract(bstr, "<div class=\"invest_new_con\">", "<tbody",">", "元"));
    kv["annulized_rating"] = filternum(extract(bstr, "<div class=\"invest_new_con\">", "<tbody", "元", "%"));
    kv["payment_method"] = extract(bstr,"<div class=\"invest_bid_info\">","还款方式","：","</");
    kv["award"] = extract(bstr,"<div class=\"invest_new_con\">","class=\"td_award\">","","奖励");
    kv["loan_period"] = loanperiod_util(extract(bstr, "<div class=\"invest_new_con\">", "元</td", "/td>", "</td>"));
    kv["invested_amount"] = doubletostring(s_atod(kv["borrowing_amount"].c_str()) - s_atod(num_util(extract(bstr,"div class=\"invest_new_right","剩余可投金额：","","元")).c_str()));
    kv["release_time"] = longtostring(stringtotime(extract(bstr,"<div class=\"invest_bid_info\">","开标时间","：","</").c_str(), "%Y-%m-%d %H:%M:%S"));

    sprintf(filename, "html/%s.brec", idstr);
    buf = readfile(filename);
    string invstr;
    if (buf) {
        char *p = buf;
        size_t buflen = strlen(buf);
        while (p < buf + buflen - 8) {
            int len;
            if (sscanf(p, "%08X", &len) != 1) {
                break;
            }
            p += 8;
            string istr = string(p, len);
            p += len;
            string tstr = extracthtml(istr, "<div class=\"invest_con\">", "<table class=\"tbl_record\"", "<tbody", "<!--");
            string tmp;
            while ((tmp = extract(tstr, "<tr", ">", "", "</tr")) != "") {
                vector <string> vs;
                strtovstr(vs, tmp.c_str(), " ");
                if (vs.size() >= 8) {
                    invstr += longtostring(stringtotime((vs[7]+" "+vs[8]).c_str(), "%Y-%m-%d %H:%M:%S")) + "|" + vs[1] + "|" + vs[3] + "|";
                }
                string::size_type pos = tstr.find("</tr");
                if (pos != string::npos) {
                    tstr = tstr.substr(pos + 1);
                }
            }
        }
        free(buf);
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
