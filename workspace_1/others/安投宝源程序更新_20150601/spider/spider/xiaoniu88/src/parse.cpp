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
    kv["site_id"] = "xiaoniu88";
    kv["project_name"] = extract(bstr, "class=\"center detail-bg\"", "class=\"detail-til\"", "<h1>", "<div");
    kv["project_id"] = idstr ;
    kv["borrowing_amount"] =filternum(extract(bstr, "class=\"pro-info01 pro-zq\"", "data-un=\"", ">", "</span>"));
    kv["annulized_rating"] =doubletostring(s_atod(filternum(extract(bstr, "class=\"pro-info01 pro-zq\"", "年化收益率", "class=\"lay-l\"", "</span>")).c_str()));
    kv["payment_method"] = extract(bstr, "还款方式", "class=\"lay-f\"", ">", "</span>");
    string loanp = extract(bstr, "项目期限", "<", ">", "</li>");
    if (loanp.find("月") != string::npos) {
        kv["loan_period"] = doubletostring(s_atod(loanp.c_str()) * 30);
    }
    else {
        kv["loan_period"] = doubletostring(s_atod(loanp.c_str()));
    }
    string miniv = filternum(extract(bstr,">起投金额", "class=\"do-r\"", ">", "</span>") );
    if (miniv != "") {
        kv["minimum_investment"] = miniv;
    }
    long long releasetime = stringtotime(extract(bstr, "class=\"detail-con\"", "发布时间", "</span>", "</li>").c_str(), "%Y-%m-%d %H:%M:%S");
    if (releasetime > 1000000000) {
        kv["release_time"] = longtostring(releasetime);
    }
    long long remaintime = s_atol(extract(bstr, "fbdetail-time", "剩余时间", "down=\"", "\"").c_str());
    if (remaintime > 1) {
        kv["end_time"] = longtostring(time(NULL) + remaintime);
    }
    kv["invested_amount"] = doubletostring(s_atod(kv["borrowing_amount"].c_str()) - s_atod(filternum(extract(bstr,"剩余金额","strong data-un",">","</strong>")).c_str()));
    kv["project_details"] = extract(bstr, "detl-bottom\">", "项目简介", "<p>", "</p>");

    sprintf(filename, "html/%s.brec", idstr);
    buf = readfile(filename);
    string invstr;
    int invnum = 0;
    if (buf) {
        char *p = buf;
        size_t buflen = strlen(buf);
        string jstr = string(p, buflen);
            
        Value json = stringtojson(jstr);
        int total = 0;
        get_int_member(json, "totalRow", total);

        for (int i = 0; i < total; i++) {
            string uname;
            string addtime;
            double account;

            if (!get_string_member(json["data"][i], "userName", uname)
                || !get_string_member(json["data"][i], "investTimeString", addtime)
                || !get_double_member(json["data"][i], "investAmount", account))
            {
                continue;
            }

            addtime = longtostring(stringtotime(addtime.c_str(), "%Y-%m-%d %H:%M:%S"));
            invstr += addtime + "|" + uname + "|" + doubletostring(int(account)) + "|";
            invnum++;
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

