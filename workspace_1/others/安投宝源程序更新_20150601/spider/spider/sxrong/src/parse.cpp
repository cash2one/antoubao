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
    kv["site_id"] = "sxrong";
    kv["project_id"] = idstr;
    kv["borrower"] = extract(bstr, "class=\"box jiekuan\"", "class=\"myinfo\">", ">", "</a>");
    kv["project_name"] = extract(bstr, "class=\"box jiekuan\"", "<h2", ">", "</h2>");
    kv["borrowing_amount"] = num_util(extract(bstr, "class=\"jiekuan-b clearfix\"", "标的总额", "<dd>&#165;", "</dd>"));
    kv["loan_period"] = loanperiod_util(extract(bstr, "class=\"jiekuan-b clearfix\"", "还款期限", "<dd>", "</em>"));
    kv["release_time"] = longtostring(stringtotime(extract(bstr, "class=\"jiekuan-b clearfix\"", "发布时间", "<dd>", "</dd>").c_str(), "%Y-%m-%d %H:%M"));
    kv["payment_method"] = extract(bstr, "class=\"jiekuan-b clearfix\"", "还款方式", "<dd>", "</dd>");

    kv["investor"] = "";
    kv["investors_volume"] = "0";

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

