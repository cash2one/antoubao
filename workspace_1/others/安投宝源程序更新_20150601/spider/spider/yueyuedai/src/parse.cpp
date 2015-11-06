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
    kv["site_id"] = "yueyuedai";
    kv["borrower"] = extract(bstr,"借款用户", "<a class=",">", "</a>");
    kv["project_name"] = extract(bstr, "理财计算器", "</div>", "<span>", "</span>");
    kv["project_id"] = idstr;
    kv["borrowing_amount"] = num_util(extract(bstr, "贷款金额", "<tr>", "¥", "</em>"));
    kv["annulized_rating"] = num_util(extract(bstr, "年利率","贷款金额","<em>", "%"));
    kv["payment_method"] = extract(bstr, "还款方式", "：", "</em>", "</li>");
	kv["invested_amount"] = doubletostring(s_atod(kv["borrowing_amount"].c_str()) - \
			s_atod(num_util(extract(bstr,"可投金额","：","","元")).c_str()));
    kv["loan_period"] = loanperiod_util(extract(bstr, "div class=\"fr ImgBoxRight\"", "%<", ">" ,"¥"));

    //kv["project_details"] = extract(bstr, "贷款人信息", "借款记录","<li>", "贷款明细");

    {
        string retstr;
        string striv = extracthtml(bstr, "<div class=\"RecordsList\">", "", "", "</table");
        string ivname;
        string ivaccount;
        string ivtime;
        while ((ivname = extract(striv, "<td", "<a href", ">", "</a>")) != "") {
            ivaccount = filternum(extract(striv, "</td>", "</td>","￥", "</em>"));
            ivtime = extract(striv, "</td>", "</td>", "<td width=\"130\" >", "</td>");
            ivtime = longtostring(stringtotime(ivtime.c_str(), "%Y-%m-%d %H:%M:%S"));
            retstr += ivtime + "|" + ivname + "|" + ivaccount + "|";

            if (striv.find("</tr>") == string::npos) {
                break;
            }
            striv = striv.substr(striv.find("</tr>") + 1);
        }
        kv["investor"] = retstr;
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

