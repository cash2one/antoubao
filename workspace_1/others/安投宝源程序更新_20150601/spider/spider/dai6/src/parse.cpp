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
    kv["site_id"] = "dai6";
    //kv["borrower"] = extract(bstr,"<dl class=","借款人:","<dd>","</dd>");
    kv["project_name"] = extract(bstr,"<div class=\"listoneaa\">","<a style=\"color","\">","</a>");
    kv["project_id"] = extract(bstr,"<div class=\"listoneaa\">","<a style=\"color","/lend/detailPage/","/\">");
        kv["borrowing_amount"] = extract(bstr, "<div class=\"", "借款金额", "￥", "</div>");
    string::size_type pos = kv["borrowing_amount"].find("万");
    if (pos != string::npos){
        kv["borrowing_amount"] = doubletostring(atof(filternum(kv["borrowing_amount"]).c_str())*10000);
    } else{
        kv["borrowing_amount"] = doubletostring(atof(filternum(kv["borrowing_amount"]).c_str()));
    }  

    kv["annulized_rating"] = filternum(extract(bstr,"<div class=", "年利率：", "\">", "%+"));
  //  kv["payment_method"] = extract(bstr,"还需借款：","借款期限：","还款方式：","");
    kv["loan_period"] = extract(bstr,  " <div class=", "借款期限", "\">", "</span>");
    int pos1 = kv["loan_period"].find("月");
    if (pos1 != -1) {
        kv["loan_period"] = longtostring(atof(kv["loan_period"].c_str())*30);
    }
    else{

        kv["loan_period"] = longtostring(atof(kv["loan_period"].c_str()));
    }

//     kv["invested_amount"] = doubletostring(s_atod(kv["borrowing_amount"].c_str()) - s_atod(filternum(extract(bstr,"剩余可投","input id=\"left_count\" value=\"0.00\" type=\"hidden\">","<span id=\"borrowInvestBalance\" class=\"info_remainlend\">","</span>")).c_str()));
   //  kv["release_time"] = extract(bstr,"<td style=\"height:26px;line-height:26px;\">","开放时间","<span style=\"font-size:14px;\">","</span>");
    //kv["project_details"] = extract(bstr,"<div id=\""," 借款说明","<div class=\"span12\">","<div class=\"divtxt\">");
    {
        sprintf(filename, "html/%s.brec", idstr);
        buf = readfile(filename);
        size_t buflen = strlen(buf);
        char *p = buf;
        string retstr;
        while (p < buf + buflen - 8) {
            int len;
            sscanf(p, "%08X", &len);
            p += 8;
            string tmp = string(p, len);
            p += len;

            string::size_type spos = tmp.find("投标时间");
            string::size_type epos = tmp.find("</table>");
            if (spos == string::npos || epos == string::npos) {
                continue;
            }
            tmp = tmp.substr(spos + 1, epos - spos - 1);
            string ivname;
            string ivaccount;
            string ivtime;
            while ((ivname = extract(tmp,"", "</tr>", "<tr><td>", "</td><td")) != "") {
                ivaccount = extract(tmp, "<tr><td>", "</td><td>", "￥","</td><td>");
                ivtime = extract(tmp, "<tr><td>", "￥", "</td><td>", "</td><td");
                ivtime = longtostring(stringtotime(ivtime.c_str(), "%Y/%m/%d %H:%M")
                        );
                retstr += ivtime + "|" + ivname + "|" + ivaccount + "|";
                string::size_type pos = tmp.find("<tr><td>");
                if (pos != string::npos) {
                    tmp = tmp.substr(pos + 1);
                }
                else {
                   break;
            }
        }
        }
        free(buf);
        kv["investor"] = retstr;
    }



    printstringmap(kv);

    if (kv["project_id"] == "" ) {
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
    
    
