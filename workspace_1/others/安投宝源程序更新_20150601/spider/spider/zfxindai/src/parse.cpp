#include <stdio.h>
#include <stdlib.h>
#include <ctype.h>
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
    kv["site_id"] = "zfxindai";
    kv["project_name"] = extract(bstr,"class=\"con\">","class=\"cont2\"","class=\"p1\">", "</p>");
    kv["project_id"] = idstr;
    kv["borrowing_amount"] = filternum(extract(bstr, "class=\"cont2_left3_1\">", "总额度", "<span>", "</span>"));
    kv["annulized_rating"] = extracthtml(bstr, "年化收益", "class=\"p2\">", "<span id=\"lilv\">","</span>");
    kv["payment_method"] = extract(bstr,"class=\"cont2_left3\"", "还款方式", "class=\"p1\">","</p>");
    kv["invested_amount"] = longtostring(s_atol(kv["borrowing_amount"].c_str()) - s_atol(filternum(extract(bstr,"class=\"left_batun_right\"","剩余额度","<span>","</span>")).c_str()));
    kv["minimum_investment"] = extract(bstr,"class=\"relative fl ml5 lh40\"","class=\"touzi\"","\"最低","元起\"");
    kv["maximum_investment"] = "";
    kv["release_time"] = longtostring(stringtotime(extract(bstr,"class=\"p3\"","发布时间","","</p>").c_str(), "%Y-%m-%d"));
    kv["end_time"] = "";
    kv["loan_period"] = longtostring(s_atod(extract(bstr, "投资期限", "<span id=\"month\">", "", "</span>").c_str())*30);
    kv["borrower"] = "";
    kv["project_details"] = extract(bstr,"class=\"grid_10 box mt20 pb20 \"","借款人信息","class=\"row-fluid\"","</li>");


    printf(filename, "html/%s.brec", idstr);
    buf = readfile(filename);

    int investornum = 0;
    {
        string retstr;
        string::size_type tmp =  bstr.find("投标记录");
        if(tmp != string::npos){
            tmp = bstr.find("投资人",tmp+1);
        }
        if(tmp != string::npos){
            tmp =  bstr.find("cont6-bd-list",tmp+1);
        }
        if(tmp != string::npos){

            string striv = bstr.substr(tmp);
            string ivname;
            string ivaccount;
            string ivtime;
            while ((ivname = extract(striv, "<p>", "", "", "</p>")) != "") {
                ivaccount = filternum(extract(striv, "<p>", "<p>", "", "</p>"));
                ivtime = extract(striv, "<p>", "<p>", "<p>", "</p>");
                ivtime = longtostring(stringtotime(ivtime.c_str(), "%Y-%m-%d %H:%M"));
                if (striv.find("</li>") == string::npos) {
                    break;
                }
                striv = striv.substr(striv.find("</li>") + 1);

                retstr += ivtime + "|" + ivname + "|" + ivaccount + "|";
                investornum++;
            }
        }
        kv["investor"] = retstr;
    }

    kv["investors_volume"] = longtostring(investornum);

    printstringmap(kv);
    if (kv["project_id"] == "" || kv["release_time"] == "") {
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
