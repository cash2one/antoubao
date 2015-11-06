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
    kv["site_id"] = "gofobao";
    kv["borrower"] = extract(bstr, "<div class=\"pic\">", "<h3><a href=", "\">","</a></h3>");
    kv["project_name"] = extract(bstr,"</div>","<div class=\"credit\">","<h3>","</h3>");
    kv["project_id"] = extract(bstr,"<li class=","<li onclick=","getTenderList(",")\">");
    kv["borrowing_amount"] = extract(bstr, "<div class=\"plan\">", "金额：","￥","</b></li>");
    string::size_type pos = kv["borrowing_amount"].find("万");
    if (pos != string::npos){
        kv["borrowing_amount"] = doubletostring(atof(filternum(kv["borrowing_amount"]).c_str())*10000);
    } else{
        kv["borrowing_amount"] = doubletostring(atof(filternum(kv["borrowing_amount"]).c_str()));
    }  

    kv["annulized_rating"] = filternum(extract(bstr,"<li class=\"last\">","年利率", "<b>", "%"));
    kv["payment_method"] = extract(bstr,"</div>","<div class=\"col1\">","还款方式：","</div>");
    kv["loan_period"] = extract(bstr, "金额", "期限", "<b>","</b></li>");
    int pos1 = kv["loan_period"].find("月");
    if (pos1 != -1) {
        kv["loan_period"] = longtostring(atof(kv["loan_period"].c_str())*30);
    }
    else{

        kv["loan_period"] = longtostring(atof(kv["loan_period"].c_str()));
    }

  //  kv["invested_amount"] = doubletostring(s_atod(kv["borrowing_amount"].c_str()) - s_atod(filternum(extract(bstr,"剩余时间","额","￥","</em></div>")).c_str()));
  //   kv["release_time"] = extract(bstr,"还款方式","发布时间","<em>","</em></span></li>");
    kv["project_details"] = extract(bstr,"<div class=\"bar-profile\">","<ul>","<li class=\"on\">","</p></div>");
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
            if (!json.isArray()) {
                    continue;
            }
            for (int i = 0; i < json.size(); i++) {
                string account;
                string addtime;
                string username;
                if (!get_string_member(json[i], "tender_money", account)
                        || !get_string_member(json[i], "addtime", addtime)
                        || !get_string_member(json[i], "username", username)) {
                    continue;
                }
                addtime = longtostring(stringtotime(addtime.c_str(), "%Y-%m-%d %H:%M"));
                invstr += addtime + "|" + username + "|" + account + "|";
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

    
