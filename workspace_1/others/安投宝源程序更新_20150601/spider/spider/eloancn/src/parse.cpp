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
    kv["site_id"] = "eloancn";
    kv["borrower"] = extract(bstr, "class=\"ld_user fl\">", "<p>", "\">", "</a>");
    kv["credit_rating"] = extract(bstr,"class=\"ld_info fl\">","class=\"wd270\">","信用等级：","</span>");
    kv["project_name"] = extract(bstr, "class=\"ld_info fl\">", "<h2", "class=\"mt10\">", "</h2>");
    kv["project_id"] = idstr ;
    kv["borrowing_amount"] = num_util(extract(bstr, "class=\"ld_info fl\">","class=\"mt10\">", "借款金额：","元"));
    kv["annulized_rating"] = filternum(extract(bstr, "class=\"ld_info fl\">", "class=\"mt10\">","利率：", "%"));
    kv["payment_method"] = extract(bstr, "class=\"ld_info fl\">", "class=\"mt10\">","还款方式：", "<img");
    kv["loan_period"] = loanperiod_util(extract(bstr,"class=\"ld_info fl\">","class=\"wd180\">","期限：","</li"));
    kv["invested_amount"] = doubletostring(s_atod(filternum(extract(bstr, "class=\"ld_info fl\">", "借款进度：", "", "%")).c_str())
            * s_atod(kv["borrowing_amount"].c_str()) / 100.0);
    kv["project_details"] = extract(bstr,"<!--基本信息-->", "class=\"record\"", "基本信息", " <!--材料信息-->");

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

