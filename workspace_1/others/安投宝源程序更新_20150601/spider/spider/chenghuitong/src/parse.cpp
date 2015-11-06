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
    kv["site_id"] = "chenghuitong";
    //kv["borrower"] = "";
    kv["project_name"] = extract(bstr, "class=\"breadcrumb\">","优选专区","</li>","</li>");
    kv["project_id"] = idstr;
    kv["borrowing_amount"] = filternum(extract(bstr, "lass=\"invest-param-li1\">", "借款金额（元）", "class=\"font24px bold color-main\">￥", "</div>"));
    kv["annulized_rating"] = filternum(extracthtml(bstr, "class=\"invest-param-li2\">","借款年利率","class=\"font24px bold color-main\">", "%"));
    kv["payment_method"] = extract(bstr, "class=\"invest-param-p pull-left\">", "还款方式：", ">", "</span>");
//kv["award"] = extract(bstr, "class=\"invest-param-p pull-left\">", "投资奖励：", ">","%");
    kv["loan_period"] = longtostring(s_atod(extract(bstr,"class=\"invest-param-li3\">","借款期限","class=\"font24px bold color-main\">","个月").c_str())*30);
  //  kv["minimum_investment"] = extract(bstr, "class=\"love\">", "投标限额：", ">￥", " - 不限");
    //kv["maximum_investment"] = "";
    //kv["release_time"] = filternum(extract(bstr, "class=\"iniest-param-p pull-left\">", "发标时间：", ">", "</span>"));
   // kv["project_details"] = extract(bstr, "<!-- 项目详情 -->", "class=\"tab-pane active\"", "<tr>", "<!-- /项目详情 -->");
    //kv["end_time"] = "";
    kv["invested_amount"] = doubletostring(s_atod(kv["borrowing_amount"].c_str()) - s_atod(filternum(extract(bstr,"class=\"love\">","可投金额：","￥","</span>")).c_str()));


    sprintf(filename, "html/%s.brec", idstr);
    buf = readfile(filename);

    int investornum = 0;
    {
        string retstr;
        string::size_type tmp =  bstr.find("投标人/关系");
        if(tmp != string::npos){
            tmp =  bstr.find("<tr>",tmp+1);
        }
        if(tmp != string::npos){

            string striv = bstr.substr(tmp);
            string ivname;
            string ivaccount;
            string ivtime;
            while ((ivname = extract(striv, "<td", "class=\"text-center\"", ">", "</td>")) != "") {
                ivaccount = filternum(extract(striv, "</td>", "<td", "class=\"text-right\">", "元"));
                ivtime = extract(striv, "元", "元", "\">", "</td>");
                ivtime = longtostring(stringtotime(ivtime.c_str(), "%Y-%m-%d %H:%M:%S"));
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
    kv["investors_volume"] = longtostring(investornum);
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

