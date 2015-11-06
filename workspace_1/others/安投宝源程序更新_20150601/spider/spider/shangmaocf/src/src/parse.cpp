#include <stdio.h>
#include <stdlib.h>
#include <ctype.h>
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
    kv["site_id"] = "007bao";
    kv["credit_rating"] = "";
    kv["project_name"] = extract(bstr,"<head>","<","<a class=\"projectName\">", "</a>");
    kv["project_id"] = idstr;
    kv["borrowing_amount"] = filternum(extract(bstr, "class=\"pAmount\"", "class=\"amount\"", "<em>", "</em>"));
    kv["annulized_rating"] = extracthtml(bstr, "class=\"pApr\"", "class=\"apr\"", "<em>", "</em>");
    kv["payment_method"] = extract(bstr,"class=\"projectOther\"", "回款方式", "class=\"value\">","</span>");
    kv["award"] = "";
    kv["invested_amount"] = longtostring(s_atol(kv["borrowing_amount"].c_str()) - s_atol(filternum(extract(bstr,"class=\"projectOther\"","可投金额","class=\"value price\">","</em>")).c_str()));
    kv["minimum_investment"] = "";
    kv["maximum_investment"] = "";
    kv["release_time"] = longtostring(stringtotime(extract(bstr,"class=\"projectOther\"","起息日期","class=\"value\">","</span>").c_str(), "%Y-%m-%d"));
    kv["end_time"] = longtostring(stringtotime(extract(bstr,"class=\"projectOther\"","回款日期","class=\"value\">","</span>").c_str(), "%Y-%m-%d"));
    kv["loan_period"] = longtostring((s_atol(kv["end_time"].c_str()) - s_atol(kv["release_time"].c_str()))/86400);
    kv["project_details"] = strreplace(extract(bstr, "<", "DecriptionData.projectDes", "{\"ProjectPurpose\":\"", "\",\"LoanUserDescription\""), "\\r\\n", "\n", 1);
    vector <string> detail;
    strtovstr(detail, kv["project_details"].c_str(), "\n");
    kv["borrower"] = "";
    for (size_t i = 0; i < detail.size(); i++) {
        string::size_type a = detail[i].find("借款人");
        if (a == string::npos) {
            a = detail[i].find("债务人");
        }
        string::size_type b = detail[i].find("介绍");
        if (a != string::npos && b != string::npos && a < b) {
            for (size_t j = i + 1; j < detail.size(); j++) {
                string tmp = dhtml(detail[j]);
                if (tmp != "") {
                    kv["borrower"] = tmp;
                    break;
                }
            }
            break;
        }
    }

    string investor;
    int investornum = 0;
    {
        string striv = bstr.substr(bstr.find("</html>"));
        string::size_type pos = striv.find("<tbody>");
        if (pos != string::npos) {
            striv = striv.substr(pos);
            string ivname;
            string ivamt;
            string ivtime;
            while ((ivname = extract(striv, "<tr>", "<", "td>", "<")) != "") {
                ivamt = filternum(extract(striv, "<tr>", "<em>", "<td>", "</td>"));
                ivtime = longtostring(stringtotime(extract(striv, "<tr>", "元", "<td>", "</td>").c_str(), "%Y-%m-%d %H:%M:%S"));
                investor += ivtime + "|" + ivname + "|" + ivamt + "|";
                investornum++;
                pos = striv.find("</tr>", pos + 1);
                if (pos == string::npos) {
                    break;
                }
                striv = striv.substr(pos);
            }
        }
    }
    kv["investor"] = investor;
    kv["investors_volume"] = longtostring(investornum);

    printstringmap(kv);
    if (kv["project_id"] == "" || kv["release_time"] == "") {
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
