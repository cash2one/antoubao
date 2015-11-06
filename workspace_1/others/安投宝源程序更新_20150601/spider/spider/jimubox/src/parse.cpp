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
    kv["site_id"] = "jimubox";
    kv["credit_rating"] = "";
    kv["project_name"] = extract(bstr, "div class=\"project-title\"", "h2", ">", "</h2>");
    kv["project_id"] = idstr;
    kv["invested_amount"] = filternum(extract(bstr, "div class=\"project-title\"", "h2", "已经完成投标", "元"));
    kv["annulized_rating"] = extract(bstr, "class=\"project-base-info\"", "data-tips", "important\">", "%");
    kv["payment_method"] = extract(bstr, "class=\"project-attribute\"", "</span>", "<span>", "</span>");
    kv["award"] = "";
    kv["loan_period"] = longtostring(s_atod(extract(bstr, "class=\"project-base-info\"", "class=\"glyphicons clock\"", ">", "个月").c_str()) * 30);
    long remamt = s_atol(filternum(extract(bstr, "<div class=\"row-fluid\">", "class=\"wall\"", "可投金额", "元")).c_str());
    kv["borrowing_amount"] = longtostring(s_atol(kv["invested_amount"].c_str()) + remamt);
    kv["minimum_investment"] = "";
    kv["maximum_investment"] = "";
    kv["release_time"] = "0";
    kv["project_details"] = strreplace(extract(bstr, "<!--Start: ProjectInfo -->", "", "", "<!--End: ProjectInfo -->"), "所有融资项目", "", 1);
    kv["borrower"] = extract(kv["project_details"], " ", "", "", "\n");
    long long endtime = stringtotime(extract(kv["project_details"], "投标截止时间 ", "", "", "\n").c_str(), "%Y-%m-%d %H:%M:%S");
    long long paytime = stringtotime(extract(bstr, "class=\"project-base-info\"", "class=\"glyphicons clock\"", "data-content=\"该项目借款到期日为", "\"").c_str(), "%Y-%m-%d");
    if (paytime > 0 && endtime > 0) {
        kv["loan_period"] = longtostring((paytime - endtime)/86400);
    }
    kv["end_time"] = longtostring(endtime);

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
            if (!has_array_member(json, "list")) {
                continue;
            }
            for (int i = 0; i < json["list"].size(); i++) {
                if (json["list"][i].size() < 4
                        || !json["list"][i][1].isString()
                        || !json["list"][i][2].isString()
                        || !json["list"][i][3].isString()) {
                    continue;
                }
                string atime = longtostring(stringtotime(json["list"][i][1].asString().c_str(), "%Y-%m-%d %H:%M:%S"));
                string uname = json["list"][i][2].asString();
                string amt = json["list"][i][3].asString();
                invstr += atime + "|" + uname + "|" + amt + "|";
                invnum++;
            }
        }
        free(buf);
    }
    kv["investor"] = invstr;
    kv["investors_volume"] = longtostring(invnum);

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

