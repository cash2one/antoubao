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
    kv["site_id"] = "junfup2p";
    kv["project_name"] = extract(bstr, "<div class=\"loanbid\"", "<h4", ">", "</h4");
    kv["project_id"] = idstr;
    kv["borrowing_amount"] = num_util(extract(bstr, "<div class=\"loanbox\"", ">", "", "借款金额"));
    string ar = extract(bstr, "<div class=\"loanbox\"", "<li", "<li", "</li");
    double rt = s_atod(filternum(ar).c_str());
    if (ar.find("日") != string::npos) {
        rt *= 365;
    }
    else if (ar.find("月") != string::npos) {
        rt *= 30;
    }
    kv["annulized_rating"] = doubletostring(rt);
    kv["payment_method"] = extract(bstr, "<div class=\"loanbid\"", "还款方式", "", "</td");
    kv["award"] = extract(bstr, "<div class=\"loanbid\"", "利率", "", "投标奖励");
    kv["loan_period"] = loanperiod_util(extract(bstr, "<div class=\"loanbid\"", "续投奖励", "", "借款期限"));
    kv["invested_amount"] = doubletostring(s_atod(kv["borrowing_amount"].c_str()) - s_atod(num_util(extract(bstr, "<div class=\"loanbid\"", "借款期限", ">", "剩余金额")).c_str()));

    string invstr;
    {
        string jstr = extracthtml(bstr, "id=\"bidrecord\"", "<tbody", "", "</tbody");
        string ivname;
        string ivtime;
        string ivacc;
        while ((ivname = extract(jstr, "<td", ">", "", "<td")) != "") {
            ivacc = num_util(extract(jstr, "<td", "<td", ">", "<"));
            ivtime = longtostring(stringtotime(extract(jstr, "<td", "元</td>", ">", "<").c_str(), "%Y/%m/%d %H:%M:%S"));
            invstr += ivtime + "|" + ivname + "|" + ivacc + "|";
            string::size_type pos = jstr.find("</tr");
            if (pos != string::npos) {
                jstr = jstr.substr(pos + 1);
            }
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

