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
    kv["site_id"] = "minxindai";
    kv["borrower"] = extract(bstr, "<tbody>", "用户名", "<td>","</td>");
    kv["project_name"] = extract(bstr,"<div class=\"l\">","<h4 class=\"title\">","<span class=\"f18 title_position\">","</span>");
    kv["project_id"] = extract(bstr,"<div class=\"fixed_nav\">","<div class=\"link-wp\">","borrowid=","\" class=\"");
    kv["borrowing_amount"] = num_util(extract(bstr, "年化收益率", "投资期限","\">","元</p><p"));

    string ars = extract(bstr,"<span class=\"other\">", "<div class=\"count mt20 clear\">", "\">", "%");
    float ar = 0.0;
    float aw = 0.0;
    if (sscanf(ars.c_str(), "%f+%f", &ar, &aw) == 2) {
        kv["award"] = doubletostring(aw);
    }
    kv["annulized_rating"] = doubletostring(ar);

    kv["payment_method"] = extract(bstr,"预期总收益","还款方式","\">","</div></li");
    kv["loan_period"] = loanperiod_util(extract(bstr, "还款方式", "投资期限", "\">","</div></li>"));

    kv["invested_amount"] = doubletostring(s_atod(kv["borrowing_amount"].c_str()) - s_atod(num_util(extract(bstr,"投资期限","剩余金额","\">","元</div></li>")).c_str()));
    kv["project_details"] = extract(bstr,"<div class=\"clear\">","<div class=\"title\">","项目描述","<ul class=\"project_describe clear\">");
    {
        sprintf(filename, "html/%s.brec", idstr);
        buf = readfile(filename);
        size_t buflen = strlen(buf);
        char *p = buf;
        string retstr;
        while (p < buf + buflen - 8) {
            int len;
            sscanf(p, "%08X", &len);
            p += 8;
            string tmp = string(p, len);
            p += len;

            tmp = extracthtml(tmp, "通过日期", "<tr>", "", "</tbody");
            string ivname;
            string ivaccount;
            string ivtime;
            while ((ivname = extract(tmp, "<td", "<td", ">", "</td")) != "") {
                ivaccount = num_util(extract(tmp, "</td", "</td", ">","元</td>"));
                ivtime = extract(tmp, "</td>", "元</td", ">", "</td>");
                ivtime = longtostring(stringtotime(ivtime.c_str(), "%Y-%m-%d"));
                retstr += ivtime + "|" + ivname + "|" + ivaccount + "|";
                string::size_type pos = tmp.find("</tr>");
                if (pos != string::npos) {
                    tmp = tmp.substr(pos + 1);
                }
                else {
                    break;
                }
            }
        }
        free(buf);
        kv["investor"] = retstr;
    }

    printstringmap(kv);

    if (s_atod(kv["borrowing_amount"].c_str()) <= 0) {
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
