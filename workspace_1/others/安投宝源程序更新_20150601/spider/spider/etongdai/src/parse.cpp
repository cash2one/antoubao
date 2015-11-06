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
    kv["site_id"] = "etongdai";
    kv["credit_rating"] = extract(bstr,"class=\"invest-details-list clearfix\">","class=\"item\">","信用等级", "</span>");
    kv["project_name"] = extract(bstr, "class=\"d_left floatl\">","class=\"invest_details_tit clearfix\">","floatl img2\">","合作机构");
    //kv["project_id"] = extract(bstr,"class=\"invest_details_tit clearfix\">","class=\"floatl img2\">","债权编号：","）</h1>");
    kv["project_id"] = idstr;
    kv["borrowing_amount"] = filternum(extract(bstr, "class=\"invest-details-list clearfix\">","class=\"item\">","借款金额","元"));
    kv["annulized_rating"] = filternum(extract(bstr, "class=\"invest-details-list clearfix\">","class=\"item\">","年化利率","%"));
    kv["payment_method"] = extract(bstr, "class=\"invest-details-main-list clearfix\">","还款期数：","还款方式：","违约保障类型：");
    kv["loan_period"] = extract(bstr, "class=\"invest-details-main-list clearfix\">","还款期数：","class=\"main\">","</span>").c_str();
    if (kv["loan_period"].find("月") != string::npos) {
        kv["loan_period"] = doubletostring(s_atod(kv["loan_period"].c_str())*30);
    }
    else {
        kv["loan_period"] = doubletostring(s_atod(kv["loan_period"].c_str()));
    }
    double minin = s_atod(extract(bstr, "投资金额：","class=\"digital_int input_three input_cash\"","value=\"","\"").c_str());
    if (minin >= 1.0) {
        kv["minimum_investment"] = doubletostring(minin);
    }
    kv["project_details"] = extract(bstr,"项目基本情况", "class=\"details_content clearfix\">", "class=\"details_div\">", "投标人/关系");
    long long rtime = stringtotime(extract(bstr, "剩余时间", "the_time($(\"#l_time\"),\"", "", "\"").c_str(), "%Y/%m/%d %H:%M:%S");
    if (rtime > 10000) {
        kv["end_time"] = longtostring(rtime);
    }
    kv["invested_amount"] = longtostring(s_atol(kv["borrowing_amount"].c_str()) - s_atol(extract(bstr, "class=\"top\">", "class=\"invest-borrowAmount\">", "可投金额", "元").c_str()));
    vector <string> vstr;
    strtovstr(vstr, kv["project_details"].c_str(), "\n");

    sprintf(filename, "html/%s.brec", idstr);
    buf = readfile(filename);
    string invstr;
    int invnum = 0;
    if (buf) {
        string jstr = string(buf);
        Value json = stringtojson(jstr);
        if (has_array_member(json, "body")) {
            for (int i = 0; i < json["body"].size(); i++) {
                string uname;
                double addtime;
                double account;
                if (!get_string_member(json["body"][i], "claInvestorLoginName", uname)
                        || !get_double_member(json["body"][i], "claInitSumYuan", account)
                        || !get_double_member(json["body"][i], "claCreateTime", addtime)) {
                    break;
                }
                //addtime = longtostring(stringtotime(addtime.c_str(), "%Y-%m-%d %H:%M:%S"));
                invstr += longtostring(addtime/1000) + "|" + uname + "|" + doubletostring(account) + "|";
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
