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
    kv["site_id"] = "financeofchina";
    kv["borrower"] = extract(bstr,"class=\"details\">","<dt>","用户名：","</dd>");
    kv["project_name"] = extract(bstr, "class=\"financial border \">","class=\"title clearfix\">","<h1>","</h1>");
    kv["project_id"] = idstr;
    kv["borrowing_amount"] = filternum(extract(bstr, "class=\"financial border \">", "借款金额：", "￥", "</span>"));
    kv["annulized_rating"] = filternum(extracthtml(bstr, "class=\"financial border \">","借款年利率：", "class=\"red\">", "%"));
    kv["payment_method"] = extract(bstr, "class=\"financial border \">", "还款方式：", "</p>", "</li>");
    kv["loan_period"] = loanperiod_util(extract(bstr,"class=\"financial border \">","借款期限：","class=\"red\">","<"));
    kv["minimum_investment"] = extract(bstr, "class=\"financial border \">", "最小投标额度：￥", "</p>", "</li>");
    kv["maximum_investment"] = filternum(extract(bstr,"class=\"financial border \">","最大投标额度：￥","</p>","</li>"));
    kv["project_details"] = extract(bstr, "class=\"financial border", "借款详情", ">", "<div class=\"financial border");
    kv["invested_amount"] = doubletostring(s_atod(kv["borrowing_amount"].c_str()) - s_atod(filternum(extract(bstr,"class=\"tz_jine fl\">","class=\"clearfix\">","可投金额：","元")).c_str()));

    sprintf(filename, "html/%s.brec", idstr);

    buf = readfile(filename);
    string invstr;
    if (buf) {
        Value json = stringtojson(string(buf));
        if (has_array_member(json, "InvestList")) {
            for (int i = 0; i < json["InvestList"].size(); i++) {
                string uname;
                string addtime;
                string account;
                if (!get_string_member(json["InvestList"][i], "MemberName", uname)
                        || !get_string_member(json["InvestList"][i], "Amount", account)
                        || !get_string_member(json["InvestList"][i], "CreateTime", addtime)) {
                    break;
                }
                addtime = longtostring(stringtotime(addtime.c_str(), "%Y/%m/%d %H:%M:%S"));
                invstr += addtime + "|" + uname + "|" + filternum(account) + "|";
            }
        }
        int ttmp;
        time_t nt = time(NULL);
        if (get_int_member(json, "DifferenceBiddingStratTimeOfSeconds", ttmp)) {
            kv["release_time"] = longtostring(nt + ttmp);
        }
        if (get_int_member(json, "DifferenceBiddingEndTimeOfSeconds", ttmp)) {
            kv["end_time"] = longtostring(nt + ttmp);
        }
        string stmp;
        if (get_string_member(json, "LoanDifference", stmp)) {
            kv["invested_amount"] = doubletostring(s_atod(kv["borrowing_amount"].c_str()) - s_atod(num_util(stmp).c_str()));
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

