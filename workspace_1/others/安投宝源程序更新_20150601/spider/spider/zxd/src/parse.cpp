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
    kv["site_id"] = "zxd";
    kv["borrower"] = extract(bstr,"公司名称","：","<span>","</span></li>");
    kv["project_name"] = extract(bstr, " <P class=","<h4 class=", "qydTb\">","<i class=\"bao\">");
    kv["project_id"] = extract(bstr,"<input type","id=\"subjectId","value=\"","\" />");
    kv["borrowing_amount"] = extract(bstr,"<dl class=\"borrow","liat_al_1\">"," <dt><span>","</dt>");
    string::size_type pos = kv["borrowing_amount"].find("万");
    if (pos != string::npos){
        kv["borrowing_amount"] = doubletostring(atof(filternum(kv["borrowing_amount"]).c_str())*10000);
    } else{
        kv["borrowing_amount"] = doubletostring(atof(filternum(kv["borrowing_amount"]).c_str()));
    }  

    kv["annulized_rating"] = filternum(extract(bstr,"借款期限","_liat_al_3\">", "<dt><span>", "</span>%</dt>"));
    kv["payment_method"] = extract(bstr,"年利率","border:none;\">","<dt>","</dt>");
    kv["loan_period"] = extract(bstr, "借款金额", "borrow_liat_al_2\">", "<dt><span>","</dt>");
    int pos1 = kv["loan_period"].find("月");
    if (pos1 != -1) {
        kv["loan_period"] = longtostring(atof(kv["loan_period"].c_str())*30);
    }
    else{

        kv["loan_period"] = longtostring(atof(kv["loan_period"].c_str()));
    }

     kv["invested_amount"] = doubletostring(s_atod(kv["borrowing_amount"].c_str()) - s_atod(filternum(extract(bstr,"<li class=\"mr20\">","剩余金额","<span>","</span>元")).c_str()));
    sprintf(filename, "html/%s.brec", idstr);
    buf = readfile(filename);
    string invstr;
    int invnum = 0;
    if (buf) {
        char *p = buf;
        size_t buflen = strlen(buf);
        while (p < buf + buflen - 8) {
            int len;
            if (sscanf(p, "%08X", &len) != 1) {
                break;
            }
            p += 8;
            string jstr = string(p, len);
            p += len;
            Value json = stringtojson(jstr);
            if (!has_array_member(json, "result")
                //    || !has_array_member(json["result"], "userId")
                    ) {
                continue;
            }
            for (int i = 0; i < json["result"].size(); i++) {
                double account;
                double addtime;
                string username;
                if (!get_double_member(json["result"][i], "money", account)
                        || !get_double_member(json["result"][i], "createTime", addtime)
                        || !get_string_member(json["result"][i]["userId"], "loginName", username)) {
                    continue;
                }
                invstr += doubletostring(addtime/1000) + "|" + username + "|" + doubletostring(account/100) + "|";
                invnum++;
            }
        }
        free(buf);
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

