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
    kv["site_id"] = "ered88";
    kv["project_name"] = extract(bstr, "<meta http-equiv=", "<title>", "投资项目-","-e人e贷");
//    kv["borrower"] = extract(bstr,"<div class=\"top-l\">","<span class=","title=\"","");
    kv["project_id"] = extract(bstr,"<form name=","method=\"post\"","bidding-",".html");
    kv["borrowing_amount"] = extract(bstr,"<tr height=\"","<td colspan=\"2\">","￥","</td>");
    string::size_type pos = kv["borrowing_amount"].find("万");
    if (pos != string::npos){
        kv["borrowing_amount"] = doubletostring(atof(filternum(kv["borrowing_amount"]).c_str())*10000);
    } else{
        kv["borrowing_amount"] = doubletostring(atof(filternum(kv["borrowing_amount"]).c_str()));
    }  

    kv["annulized_rating"] = filternum(extract(bstr,"<td colspan=\"2\">","￥", "<td colspan=\"2\">", "%"));
    kv["payment_method"] = extract(bstr,"<td width=","还款方式：","\">","</td>");
    kv["loan_period"] = extract(bstr, "￥", "%", "<td colspan=\"2\">","</td>");
    int pos1 = kv["loan_period"].find("月");
    if (pos1 != -1) {
        kv["loan_period"] = longtostring(atof(kv["loan_period"].c_str())*30);
    }
    else{

        kv["loan_period"] = longtostring(atof(kv["loan_period"].c_str()));
    }

//     kv["release_time"] = extract(bstr,"还款方式","发布时间","\">","</span>");
    {
            string tmp;
            string::size_type startpos = bstr.find("投标时间");
            if (startpos != string::npos) {
                string::size_type endpos = bstr.find("<div class=\"main_right\">", startpos);
                if (endpos != string::npos) {
                    tmp = bstr.substr(startpos, endpos - startpos);
                }
            }
            string ivname;
            string ivaccount;
            string ivtime;
            string retstr;
            tmp = tmp.substr(tmp.find("<div class=\"tab_text\">") + 1);
            while ((ivname = extract(tmp, "<tr>", "<td width=\"130\"", "1em;\">","</td>")) != "") {
                ivaccount = extract(tmp, " </td>", "￥", "￥","</td>");
                ivtime = extract(tmp, "￥", "￥", "\"center\">", "</td>");
                ivtime = longtostring(stringtotime(ivtime.c_str(), "%Y/%m/%d %H:%M:%S")
                        );
                retstr += ivtime + "|" + ivname + "|" + ivaccount + "|";
                string::size_type pos = tmp.find("<div class=\"tab_text\">");
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
