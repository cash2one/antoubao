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
    kv["site_id"] = "firstp2p";
    kv["project_name"] = extract(bstr, "class=\"fix_width\">", "投资列表","> <label>", "</div>");
    kv["project_id"] = idstr;
    kv["borrowing_amount"] = num_util(extract(bstr, "class=\"tz_jine fl\">", "class=\"ketou\">", "投资总额：", "元"));
    kv["annulized_rating"] = filternum(extracthtml(bstr, "年化收益率", "<dd>", "", "</dd>"));
    kv["payment_method"] = extract(bstr, "class=\"tz_lilv fl\">", "class=\"clearfix\">", "保障方式：", "</span>");
    kv["loan_period"] = loanperiod_util(extract(bstr,"年化收益率：","收益方式：","<span>","</span>"));
    kv["minimum_investment"] = extract(bstr, "class=\"ketou\">", "已投：", "元 /", "元起投");
    kv["project_details"] = extract(bstr, "融资方信息", "简介：", "<strong>", "</tr>");
    string rtime = extract(bstr, "class=\"clearfix\">", "剩余时间：", "class=\"f14\">", "</span>");
    {
        int d, h, m;
        if (sscanf(rtime.c_str(), "%d天%d时%d分", &d, &h, &m) == 3) {
            kv["end_time"] = longtostring(time(NULL) + d*86400 + h*3600 + m * 60);
        }
    }
    kv["invested_amount"] = filternum(extract(bstr,"class=\"tz_jine fl\">","class=\"ketou\">","已投：","元"));

    int investornum = 0;
    {
        string retstr;
        string::size_type tmp =  bstr.find("投资记录");
        if(tmp != string::npos){
            tmp = bstr.find("投资人", tmp+1);
        }
        if(tmp != string::npos){
            tmp =  bstr.find("</tr>",tmp+1);
        }
        if(tmp != string::npos){

            string striv = bstr.substr(tmp);
            string ivname;
            string ivaccount;
            string ivtime;
            while ((ivname = extract(striv, "<tr", "<td>", "<span>", "</span>")) != "") {
                ivaccount = filternum(extract(striv, "</td>", "<td>", "class=\"color-yellow1\">", "</span>"));
                ivtime = extract(striv, "class=\"color-yellow1\">", "</span>", "<td>", "</td>");
                ivtime = longtostring(stringtotime(ivtime.c_str(), "%Y-%m-%d %H:%M"));
                if (striv.find("</tr>") == string::npos) {
                    break;
                }
                striv = striv.substr(striv.find("</tr>") + 1);

                retstr += ivtime + "|" + ivname + "|" + ivaccount + "|";
                investornum++;
            }
        }
        kv["investor"] = retstr;
    }
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

