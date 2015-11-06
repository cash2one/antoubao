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

    size_t buflen = strlen(buf);
    string jstr = string(buf, buflen);
    free(buf);
    Value json = stringtojson(jstr);
    map <string, string> kv;
    int status = 0;
    string tmps;
    double tmpd;
    int tmpi;

    if (!get_int_member(json, "status", status) || status != 200
        || !has_object_member(json, "result"))
    {
        return 1;
    }

    kv["site_id"] = "touna";

    if (get_string_member(json["result"]["borrow"], "username", tmps))
    {
        kv["borrower"] = tmps;
    }

    if (get_string_member(json["result"]["borrow"], "name", tmps))
    {   
        kv["project_name"] = tmps;
    }

    if (get_int_member(json["result"]["borrow"], "id", tmpi))
    {
        kv["project_id"] = longtostring(tmpi);
    }

    kv["borrowing_amount"] = "";
    if (get_double_member(json["result"]["borrow"], "account", tmpd))
    {   
        kv["borrowing_amount"] = doubletostring((long)tmpd);
    }

    tmpi = 0;
    if (get_double_member(json["result"]["borrow"], "apr", tmpd) || get_int_member(json["result"]["borrow"], "apr", tmpi))
    {
        char rate[20];
        if (tmpi != 0) {
            sprintf(rate, "%d", tmpi);
        }
        else {
            sprintf(rate, "%.1f", tmpd);
        }
        kv["annulized_rating"] = string(rate);
    }

    if (get_string_member(json["result"]["borrow"], "repay_type_name", tmps))
    {
        kv["payment_method"] = tmps;
    }

    if (get_string_member(json["result"]["borrow"], "pubtime", tmps))
    {   
        kv["release_time"] = longtostring(stringtotime(tmps.c_str(), "%Y-%m-%d %H:%M:%S"));
    }
   
    if (get_int_member(json["result"]["borrow"], "account_yes", tmpi))
    {
        kv["invested_amount"] = longtostring((long)tmpi);
    }

    if (get_string_member(json["result"]["borrow"], "content", tmps))
    {
        kv["project_details"] = extract(tmps, "<p>", "<span style", ">", "</span>");
    }

    string invstr;
    int invnum = 0;
    {
        for (int i = 0; i < json["result"]["tenderList"].size(); i++)
        {
            string uname;
            string addtime;
            int account = 0;
            double accountd;

            if (!get_string_member(json["result"]["tenderList"][i], "username", uname)
                || !get_string_member(json["result"]["tenderList"][i], "addtime", addtime)
                || !get_int_member(json["result"]["tenderList"][i], "account", account))
            {
                continue;
            }

            char buf[20];
            if (account != 0)
            {
                sprintf(buf, "%d", account);
            }
            else
            {
                sprintf(buf, "%f", accountd);
            }

            invstr += addtime + "|" + uname + "|" + string(buf) + "|";
            invnum++;
        }
    }
    kv["investor"] = invstr;
    kv["investors_volume"] = longtostring(invnum);

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

