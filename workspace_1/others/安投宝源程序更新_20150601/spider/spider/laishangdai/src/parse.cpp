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
    kv["site_id"] = "anxin";
    kv["borrower"] = extract(bstr,"class=\"basic_user_info\">","<div>","class=\"info_username\">","</span>");
    kv["credit_rating"] = "";
    kv["project_name"] = extract(bstr, "class=\"div_big_title clearfix\" >","class=\"bkind_icon diya fl-l\"","class=\"fl-l\">","</h1>");
    kv["project_id"] = idstr;
    kv["borrowing_amount"] = filternum(extract(bstr, "lass=\"baisc_desc clearfix\">", "借款额度", "class=\"item_content\">￥", "</div>"));
    kv["annulized_rating"] = filternum(extracthtml(bstr, "class=\"baisc_desc clearfix\">","class=\"fl-l rate_c\"","年化利率", "%"));
    kv["payment_method"] = extract(bstr, "class=\"baisc_desc clearfix\">", "class=\"borrow_kind_c\"", "还款方式：", "</span>");
    kv["award"] = "";
    kv["loan_period"] = longtostring(s_atod(extract(bstr,"class=\"baisc_desc clearfix\">","借款期限","class=\"month_number\">","个月").c_str())*30);
    kv["minimum_investment"] = extract(bstr, "class=\"minimum_amount_c\" >", "最小投标金额：", ">￥", "</span>");
    kv["maximum_investment"] = "";
    kv["release_time"] = "";
    kv["project_details"] = extract(bstr, "class=\"apply_user_info_c unit_border unit_c_2\">", "class=\"unit_title_2\"", "个人信息", "审核信息");
    kv["end_time"] = "";
    kv["invested_amount"] = doubletostring(s_atod(kv["borrowing_amount"].c_str()) - s_atod(filternum(extract(bstr,"class=\"info_right fl-l\">","剩余金额：","class=\"left_amount\">","元")).c_str()));


    printf(filename, "html/%s.brec", idstr);
    buf = readfile(filename);

    int investornum = 0;
    {
        string retstr;
        string::size_type tmp =  bstr.find("投资记录");
        if(tmp != string::npos){
            tmp = bstr.find("用户名",tmp+1);
        }
        if(tmp != string::npos){
            tmp =  bstr.find("<tr>",tmp+1);
        }
        if(tmp != string::npos){

            string striv = bstr.substr(tmp);
            string ivname;
            string ivaccount;
            string ivtime;
            while ((ivname = extract(striv, "<td>", "", "", "</td>")) != "") {
                ivaccount = filternum(extract(striv, "<td>", "<td>", "", "</td>"));
                ivtime = extract(striv, "</td>", "</td>", "<td>", "</td>");
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

