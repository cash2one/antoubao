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
    kv["site_id"] = "jiuxindai";
    kv["project_name"] = extract(bstr, "<head>", "<meta charset=", "<title>","玖信贷");
    kv["borrower"] = extract(bstr,"grid-e grid\">","用 户 名","：","</p>");
    kv["project_id"] = extract(bstr,"pro-con-h2\">","<form action=","value=\"","\">");
    kv["borrowing_amount"] = extract(bstr,"<ul class=","项目规模","<span>","</span></p></li>");
    string::size_type pos = kv["borrowing_amount"].find("万");
    if (pos != string::npos){
        kv["borrowing_amount"] = doubletostring(atof(filternum(kv["borrowing_amount"]).c_str())*10000);
    } else{
        kv["borrowing_amount"] = doubletostring(atof(filternum(kv["borrowing_amount"]).c_str()));
    }  

    kv["annulized_rating"] = filternum(extract(bstr,"起投金额","年化收益", "<span>", "%</span>"));
    kv["payment_method"] = extract(bstr,"<li style=","<li style=","还款方式：","</p>");
    kv["loan_period"] = extract(bstr, "<ul class=", "投资期限", "<span>","</span></p>");
    int pos1 = kv["loan_period"].find("月");
    if (pos1 != -1) {
        kv["loan_period"] = longtostring(atof(kv["loan_period"].c_str())*30);
    }
    else{

        kv["loan_period"] = longtostring(atof(kv["loan_period"].c_str()));
    }

     kv["invested_amount"] = doubletostring(s_atod(kv["borrowing_amount"].c_str()) - s_atod(filternum(extract(bstr,"<ul class=","可投金额","\">","元</span>")).c_str()));
   //  kv["release_time"] = extract(bstr,"还款方式","发布时间","\">","</span>");
     long long etime1 = stringtotime(extract(bstr,"<li style=","发布时间","：","</p>").c_str(), "%Y-%m-%d");
     if (etime1 > 1000000000) {
         kv["release_time"] = longtostring(etime1);
     }
    {
            string tmp;
            string::size_type startpos = bstr.find("状态");
            if (startpos != string::npos) {
                string::size_type endpos = bstr.find("<a class=", startpos);
                if (endpos != string::npos) {
                    tmp = bstr.substr(startpos, endpos - startpos);
                }
            }
            string ivname;
            string ivaccount;
            string ivtime;
            string retstr;
            tmp = tmp.substr(tmp.find("pro-blcok1\">") + 1);
            while ((ivname = extract(tmp, "<div class=", "a grid\">", "<p>", "</p>")) != "") {
                ivaccount = extract(tmp, "a grid\">", "grid\">", "¥","</p>");
                ivtime = extract(tmp, "¥", "grid\">", "<p>", "</p>");
                ivtime = longtostring(stringtotime(ivtime.c_str(), "%Y-%m-%d %H:%M:%S")
                        );
                retstr += ivtime + "|" + ivname + "|" + ivaccount + "|";
                string::size_type pos = tmp.find("pro-blcok1\">");
                if (pos != string::npos) {
                    tmp = tmp.substr(pos + 1);
                }
                else {
                   break;
            }
        }
      kv["investor"] = retstr;    
    }


    if (kv["project_id"] == "" ) {
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
