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

    Value weidai = stringtojson(bstr);

    kv["site_id"] = "weidai";
    kv["borrower"] = weidai["user"]["un"].asString();
    kv["project_name"] = weidai["binfo"]["name"].asString();
    kv["project_id"] = weidai["binfo"]["bid"].asString();
    kv["borrowing_amount"] = weidai["binfo"]["account"].asString();
    kv["annulized_rating"] = weidai["binfo"]["borrow_apr"].asString();
    kv["payment_method"] = weidai["binfo"]["show_borrow_style"].asString();
    kv["award"] = weidai["binfo"]["borrow_jiangli"].asString();
    int dtmp = s_atol(weidai["binfo"]["days"].asString().c_str());
    if (dtmp > 0) {
        kv["loan_period"] = longtostring(dtmp);
    }
    else {
        kv["loan_period"] = longtostring(s_atol(weidai["binfo"]["borrow_period"].asString().c_str()) * 30);
    }
    kv["minimum_investment"] = weidai["binfo"]["tender_account_min"].asString();
    kv["maximum_investment"] = weidai["binfo"]["tender_account_max"].asString();
    kv["release_time"] = longtostring(stringtotime(weidai["binfo"]["verify_time"].asString().c_str(), "%Y-%m-%d %H:%M:%S"));
    if (weidai["binfo"]["lefttime"].asInt() > 0) {
        kv["end_time"] = longtostring(time(NULL) + weidai["binfo"]["lefttime"].asInt());
    }
    
    for (int i = 0; i < weidai["diya_list"].size(); i++) {
        kv["project_details"] += "车辆品牌: " +  weidai["diya_list"][i]["name"].asString() + "\n"
            "车牌号: " + weidai["diya_list"][i]["chepai"].asString() + "\n"
            "公里数: " + weidai["diya_list"][i]["gonglishu"].asString() + "\n"
            "购买价格: " +  weidai["diya_list"][i]["buymoney"].asString() + "\n"
            "抵押估价: " +  weidai["diya_list"][i]["money"].asString() + "\n"
            "审核时间: " +  weidai["diya_list"][i]["verify_time"].asString() + "\n"
            "审核说明: " +  weidai["diya_list"][i]["verify_remark"].asString() + "\n";
    }
    kv["invested_amount"] = doubletostring(s_atod(kv["borrowing_amount"].c_str()) - s_atod(weidai["binfo"]["borrow_account_wait"].asString().c_str()));

    string invstr;
    int invnum = 0;
    if (has_array_member(weidai, "tender_list")){
        for (int i = 0; i < weidai["tender_list"].size(); i++) {
            string account;
            string addtime;
            string username;
            if (!get_string_member(weidai["tender_list"][i], "account", account)
                    || !get_string_member(weidai["tender_list"][i], "time_h", addtime)
                    || !get_string_member(weidai["tender_list"][i], "un", username)){
                break;
            }
            addtime = longtostring(stringtotime(addtime.c_str(),"%Y-%m-%d %H:%M:%S"));
            invstr += addtime + "|" + username + "|" + filternum(account) + "|";
            invnum++;
        }
    }
    kv["investor"] = invstr;
    kv["investors_volume"] = longtostring(invnum);
    printstringmap(kv);

   if (kv["project_id"] == "" || s_atol(kv["borrowing_amount"].c_str()) <= 0)
    {
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

