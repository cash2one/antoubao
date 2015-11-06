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
	kv["type"] = "1";
    kv["site_id"] = "juzilicai";
//    kv["borrower"] = extract(bstr, "", "</span>", "","</dd>");
    kv["project_name"] = extract(bstr,"<div class=\"ac-left fn-left fn-clear\">","<h2>","","<span>");
    kv["project_id"] = idstr;
    kv["borrowing_amount"] = num_util(extract(bstr, "加入总额", "\">","","</span>"));
	kv["invested_amount"] = doubletostring(s_atod(kv["borrowing_amount"].c_str()) - s_atod(num_util(extract(bstr, "可买", "\">", "", "</span>")).c_str()));

//	kv["release_time"] = longtostring(stringtotime(extract(bstr,"起投时间","：","","</div>").c_str(),"%Y-%m-%d %H:%M"));

    kv["annulized_rating"] = filternum(extract(bstr, "class=\"c-orange per\">", "\">","", "%"));
    kv["payment_method"] = extract(bstr,"<div class=\"ac-left fn-left fn-clear\">","<h2>","<span>","</span>");
//    kv["loan_period"] = loanperiod_util(extract(bstr, "还款期限", "<em>", "","</em>"));

	printstringmap(kv);

    if (kv["project_id"] == "" ) {
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
