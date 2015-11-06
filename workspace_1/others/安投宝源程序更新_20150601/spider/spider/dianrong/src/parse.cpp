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
    Value json = stringtojson(jstr);
    free(buf);
    map <string, string> kv;
    string tmps;
    double tmpd;
    int tmpi;

    if (!has_object_member(json, "content") || !has_object_member(json["content"], "loanInfo")
        || !has_object_member(json["content"], "loanData"))
    {
        return 1;
    }

    kv["site_id"] = "dianrong";

    if (has_object_member(json["content"], "borrowerPersonalInfo"))
    {
        if (get_string_member(json["content"]["borrowerPersonalInfo"], "username", tmps))
        {
            kv["borrower"] = tmps;
        }
    }

    if (get_string_member(json["content"]["loanInfo"], "grade", tmps))
    {
        kv["credit_rating"] = tmps;
    }

    if (get_string_member(json["content"]["loanInfo"], "title", tmps))
    {
        kv["project_name"] = tmps;
    }

    if (get_string_member(json["content"]["loanInfo"], "loanID", tmps))
    {
        kv["project_id"] = tmps;
    }

    if (get_double_member(json["content"]["loanData"], "amount", tmpd))
    {   
        kv["borrowing_amount"] = doubletostring(tmpd);
    }

    if (get_string_member(json["content"]["loanInfo"], "rate", tmps))
    {
        kv["annulized_rating"] = filternum(tmps);
    }

    if (get_string_member(json["content"]["loanInfo"], "repaymentMethod", tmps))
    {
        kv["payment_method"] = tmps;
    }

    if (get_double_member(json["content"]["loanInfo"], "submissionTime", tmpd))
    {   
        kv["release_time"] = longtostring((long)tmpd/1000);
    }
   
    if (get_double_member(json["content"]["loanInfo"], "expirationTime", tmpd))
    {
        kv["end_time"] = longtostring((long)tmpd/1000);
    }

    if (get_double_member(json["content"]["loanData"], "fundingReceived", tmpd))
    {
        kv["invested_amount"] = doubletostring(tmpd);
    }

    if (get_string_member(json["content"]["loanInfo"], "description", tmps))
    {
        kv["project_details"] = tmps;
    }
 
    sprintf(filename, "html/%s.brec", idstr);
    buf = readfile(filename);
    string invstr;

    int invnum = 0;
    if (buf) {
        size_t buflen = strlen(buf);
        string jstr = string(buf, buflen);
        free(buf);
            
        Value json = stringtojson(jstr);
        int total = 0;

        string res;
        if (has_string_member(json, "result") && json["result"] == "success")
        { 
            get_int_member(json["content"], "totalRecords", total);

            for (int i = 0; i < total; i++) {
                string uname;
                string addtime;
                double account;

                if (!get_string_member(json["content"]["records"][i], "username", uname)
                    || !get_string_member(json["content"]["records"][i], "buyDate", addtime)
                    || !get_double_member(json["content"]["records"][i], "amount", account))
                {
                    continue;
                }

                addtime = longtostring(stringtotime(addtime.c_str(), "%Y-%m-%dT%H:%M:%S"));
                invstr += addtime + "|" + uname + "|" + doubletostring(account) + "|";
                invnum++;
            }
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

