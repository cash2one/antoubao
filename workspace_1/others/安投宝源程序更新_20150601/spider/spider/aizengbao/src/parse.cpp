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
    kv["site_id"] = "aizengbao";
    string br1 = extract(bstr, "div class=\"tab-content", "企业代理人", "", "</dd");
    string br2 = extract(bstr, "div class=\"tab-content", "融资企业", "", "</dd");
    if (br1 != "") {
        kv["borrower"] = br1;
    }
    else if (br2 != "") {
        kv["borrower"] = br2;
    }
    kv["credit_rating"] = extract(bstr, "<div class=\"container\">", "<div class=\"pj_", "", "\"");
    kv["project_name"] = extract(bstr, "<div class=\"container\">", "project_title\">", "", "</div");
    kv["project_id"] = idstr;
    kv["borrowing_amount"] = num_util(extract(bstr, "<div class=\"container\">", "融资金额", "", "</div"));
    string ara = extract(bstr, "<div class=\"container\">", "预期年化收益率", "", "%");
    float ara_a, ara_b;
    if (sscanf(ara.c_str(), "%f+%f", &ara_a, &ara_b) == 2) {
        kv["award"] = doubletostring(ara_b);
    }
    kv["annulized_rating"] = doubletostring(ara_a);
    kv["payment_method"] = extract(bstr, "<div class=\"container\">", "<kbd", ">", "</div>");
    kv["loan_period"] = loanperiod_util(extract(bstr, "<div class=\"container\">", "融资时间", "", "</div"));
    kv["invested_amount"] = doubletostring(s_atod(kv["borrowing_amount"].c_str()) - s_atod(num_util(extract(bstr, "<div class=\"container\">", "融资金额", "可投金额", "元")).c_str()));
    long long et = stringtotime(extract(bstr, "<div class=\"container\">", "data-endtime=\"", "", "\"").c_str(), "%Y/%m/%d %H:%M:%S");
    if (et <= 0) {
        et = stringtotime(extract(bstr, "<div class=\"tab-content well\"", "投标截止日期", "", "</dl").c_str(), "%Y-%m-%d");
    }
    if (et > 0) {
        kv["end_time"] = longtostring(et);
    }

    {
        string invstr;
        string jstr = extracthtml(bstr, "<div>投标记录", "<tbody", "", "</tbody");
        string ivname;
        string ivtime;
        string ivacc;
        while ((ivname = extract(jstr, "<td", ">", "", "</td")) != "") {
            ivtime = longtostring(stringtotime(extract(jstr, "<td", "<td", ">", "</td").c_str(), "%Y-%m-%d"));
            ivacc = num_util(extract(jstr, "</td", "</td", ">", "</td"));
            invstr += ivtime + "|" + ivname + "|" + ivacc + "|";
            string::size_type pos = jstr.find("</tr");
            if (pos != string::npos) {
                jstr = jstr.substr(pos + 1);
            }
            else {
                break;
            }
        }
        kv["investor"] = invstr;
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

