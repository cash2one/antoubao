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
    
    Value woqidai = stringtojson(bstr);

    kv["site_id"] = "woqidai";
    //kv["borrower"] = "";
    kv["project_name"] = woqidai["project_name"].asString();
    kv["project_id"] = idstr;
    kv["borrowing_amount"] = doubletostring(woqidai["financing"].asDouble());
    kv["annulized_rating"] = doubletostring(woqidai["irr"].asDouble()*100);
     //kv["payment_method"] = "";
    kv["release_time"] = longtostring(stringtotime(woqidai["publish_time"].asString().c_str(), "%Y-%m-%d %H:%M:%S"));
    kv["loan_period"] = doubletostring(woqidai["duration"].asDouble());

    sprintf(filename, "html/%s.brec", idstr);
    buf = readfile(filename);
    string invstr;
    int invnum = 0;
    if (buf) {
        string jstr = string(buf);
        Value json = stringtojson(jstr);
        if (has_array_member(json, "inverstors")) {
            for (int i = 0; i < json["inverstors"].size(); i++) {
                string uname;
                string addtime;
                double account;
                if (!get_string_member(json["inverstors"][i], "inverstor", uname)
                        || !get_double_member(json["inverstors"][i], "bid_amount", account)
                        || !get_string_member(json["inverstors"][i], "bid_date", addtime)) {
                    break;
                }
                addtime = longtostring(stringtotime(addtime.c_str(), "%Y-%m-%d %H:%M:%S"));
                invstr += addtime + "|" + uname + "|" + doubletostring(account) + "|";
                invnum++;
            }
        }
        free(buf);
    }
    kv["investor"] = invstr;

    printstringmap(kv);

    if (s_atol(kv["borrowing_amount"].c_str()) <= 0) {
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
