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

    
    kv["site_id"] = "shangmaocf";
    kv["borrower"] = extract(bstr,"class=\"invest2_table3\">","用户ID","class=\"td1\">","</td>");
    kv["project_name"] = extract(bstr,"class=\"invest2_table\">","<tr>","<td>", "</a>");
    kv["project_id"] = idstr;
    kv["borrowing_amount"] = filternum(extract(bstr, "class=\"invest2_table\"", "货款金额：", "￥", "</span>"));
    kv["annulized_rating"] = extracthtml(bstr, "class=\"invest2_table\"", "年化利率：", ">", "%");
    kv["payment_method"] = extract(bstr,"class=\"invest2_table\"", "还款方式：", ">","</span>");
    kv["invested_amount"] = longtostring(s_atol(kv["borrowing_amount"].c_str()) - s_atol(filternum(extract(bstr,"class=\"invest2_block2\"","class=\"fc5\">","","</p>")).c_str()));
    kv["loan_period"] = loanperiod_util(extract(bstr,"class=\"invest2_table\">","还款期限：","class=\"fc4\">","</span>"));

    string investor;
    int investornum = 0;
    {
        string::size_type pos = bstr.find("投标人/关系");
        string::size_type epos = bstr.find("借入标题",pos + 1);
        if (pos != string::npos && epos != string::npos) {
            string tmp = bstr.substr(pos, epos - pos);
            pos = tmp.find("</tr>");
            tmp = tmp.substr(pos + 1);

            string ivname;
            string ivamt;
            string ivtime;
            while ((ivname = extract(tmp, "<td>", "</td>", "<td>", "</td>")) != "") {
                ivamt = filternum(extract(tmp, "元", "</td>", ">", "</td>"));
                ivtime = longtostring(stringtotime(extract(tmp, "元", "元", "<td>", "</td>").c_str(), "%Y-%m-%d %H:%M:%S"));
                investor += ivtime + "|" + ivname + "|" + ivamt + "|";
                investornum++;
                pos = tmp.find("</tr>", pos + 1);
                if (pos == string::npos) {
                    break;
                }
                tmp = tmp.substr(pos);
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
