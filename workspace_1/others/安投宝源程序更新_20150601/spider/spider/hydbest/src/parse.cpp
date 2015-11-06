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
    kv["site_id"] = "hydbest";
    kv["borrower"] = extract(bstr,"<table id=\"cumessage\">","用户名:","<th>","</th>");
    kv["project_name"] = extract(bstr, "项目详情</li>", "<img src=\"", "\"/>","</div>");
    kv["credit_rating"] = extract(bstr,"信用指数","</td>","<img src=\"","\" />");
    kv["project_id"] = extract(bstr,"click(function ()","window.location.href","GoToInvest?borrowId=","\";");
    kv["borrowing_amount"] = extract(bstr,"项目总额：","<span style=",";\">","</span></td>");
    string::size_type pos = kv["borrowing_amount"].find("万");
    if (pos != string::npos){
        kv["borrowing_amount"] = doubletostring(atof(filternum(kv["borrowing_amount"]).c_str())*10000);
    } else{
        kv["borrowing_amount"] = doubletostring(atof(filternum(kv["borrowing_amount"]).c_str()));
    }  

    kv["annulized_rating"] = filternum(extract(bstr,"产品类型","<div style=\"", "\">", "%</div>"));
    kv["payment_method"] = extract(bstr,"<tr>","还款方式：",";\">","</span>");
    kv["loan_period"] = extract(bstr, "产品类型", "%</div>", "\">","</div>");
    int pos1 = kv["loan_period"].find("月");
    if (pos1 != -1) {
        kv["loan_period"] = longtostring(atof(kv["loan_period"].c_str())*30);
    }
    else{

        kv["loan_period"] = longtostring(atof(kv["loan_period"].c_str()));
    }

//     kv["invested_amount"] = doubletostring(s_atod(kv["borrowing_amount"].c_str()) - s_atod(filternum(extract(bstr,"<li>"," 剩余金额:","￥","")).c_str()));
     long long etime1 = stringtotime(extract(bstr,"始日","<span style=","\">","</span></td>").c_str(), "%Y-%m-%d");
      if (etime1 > 1000000000) {
          kv["release_time"] = longtostring(etime1);
      }
     long long etime = stringtotime(extract(bstr,"结束日","<span style=","\">","</span></td>").c_str(), "%Y-%m-%d");
     if (etime > 1000000000) {
             kv["end_time"] = longtostring(etime);
    }
    kv["project_details"] = extract(bstr,"<div style=\"height:","<div id=\"navitop","<h4 name=","<script type=\"text/javascript\">");
    sprintf(filename, "html/%s.brec", idstr);
    buf = readfile(filename);
    string invstr;
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
                double account;
                string addtime;
                string username;
                if (!get_double_member(json["list"][i], "InvestAmount", account)
                        || !get_string_member(json["list"][i], "InvestTime", addtime)
                        || !get_string_member(json["list"][i], "Username", username)) {
                    continue;
                }
                addtime = longtostring(stringtotime(addtime.c_str(), "%Y-%m-%d %H:%M:%S"));
                invstr += addtime + "|" + username + "|" + doubletostring(account) + "|";
            }
        }
        free(buf);
    }
    kv["investor"] = invstr;

    if (s_atol(kv["borrowing_amount"].c_str()) <= 0) {
        return 1;
    }
    printstringmap(kv);
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

    
    
