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
    kv["site_id"] = "itouzi";
  //  kv["borrower"] = extract(bstr, "<tbody>", "用户ID", "<td>","");
    kv["project_name"] = extract(bstr,"<link rel=","<link rel=","<title>"," -");
    kv["project_id"] = extract(bstr,"<h1 class=\"large","</h1><span","债务方编号：","</span>");
    kv["borrowing_amount"] = extract(bstr, "<dl>", "项目规模","<dd>","</span></dd>");
    string::size_type pos = kv["borrowing_amount"].find("万");
    if (pos != string::npos){
        kv["borrowing_amount"] = doubletostring(atof(filternum(kv["borrowing_amount"]).c_str())*10000);
    } else{
        kv["borrowing_amount"] = doubletostring(atof(filternum(kv["borrowing_amount"]).c_str()));
    }  

    kv["annulized_rating"] = filternum(extract(bstr,"<dl>", "年化收益", "<dd class=\"ffA\">", "</em><em"));
 //   kv["award"] = extract(bstr,"<span class=\"cybft cybft1\">","%</span><span class=","+</span>","");
    kv["payment_method"] = extract(bstr,"<p class=\"mgt\">","<li class=\"clearfix\">","还款方式：","</li>");
    kv["loan_period"] = extract(bstr, "%</em></dd>","投资期限","<dd>","</span></dd>");
    int pos1 = kv["loan_period"].find("月");
    if (pos1 != -1) {
        kv["loan_period"] = longtostring(atof(kv["loan_period"].c_str())*30);
    }
    else{

        kv["loan_period"] = longtostring(atof(kv["loan_period"].c_str()));
    }

//    kv["invested_amount"] = doubletostring(s_atod(kv["borrowing_amount"].c_str()) - s_atod(filternum(extract(bstr,"已投金额","<span class=\"red\">","￥","")).c_str()));
     kv["release_time"] = extract(bstr,"<dd><strong class="," <p class=\"mgt\">","发布日期：","&nbsp");
    kv["project_details"] = extract(bstr,"<tbody id=\"calcList\">","</tbody>","</table>","投资记录");

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
            if (!has_object_member(json, "data")
                    || !has_array_member(json["data"], "borrow_tender")) {
                continue;
            }
            for (int i = 0; i < json["data"]["borrow_tender"].size(); i++) {
                string account;
                string addtime;
                string username;
                if (!get_string_member(json["data"]["borrow_tender"][i], "account", account)
                        || !get_string_member(json["data"]["borrow_tender"][i], "addtime", addtime)
                        || !get_string_member(json["data"]["borrow_tender"][i], "username", username)) {
                    continue;
                }
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

    
 

