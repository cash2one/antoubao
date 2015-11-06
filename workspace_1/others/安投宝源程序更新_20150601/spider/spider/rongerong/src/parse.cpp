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
    kv["site_id"] = "rongerong";
    kv["borrower"] = "";
    kv["credit_rating"] = "";
    kv["project_name"] = extract(bstr, "class=\"jk_bor_le\">","class=\"jk_v_tit\""," />-->","</h1>");
    kv["project_id"] = idstr;
    kv["borrowing_amount"] = filternum(extract(bstr, "class=\"jk_v_in clearfix\">", "class=\"bigSpan\">", "<span>￥", "</span>"));
    kv["annulized_rating"] = filternum(extracthtml(bstr, "class=\"jk_v_in clearfix\">","元","<span>", "%"));
    kv["payment_method"] = extract(bstr, "class=\"dashedline\">", "还款方式：", "<span>", "</span>");
    kv["award"] = "";   
    kv["loan_period"] = longtostring(s_atod(extract(bstr,"class=\"bigSpan\">","%","<span>","个月").c_str())*30);
    kv["minimum_investment"] = extract(bstr, "class=\"dashedline\">", "最小认购金额：", ">", "</span>");
    kv["maximum_investment"] = "";
    kv["release_time"] = "";
    kv["project_details"] = extract(bstr, "class=\"conbox t30 m_box\">", "class=\"title_bor\">", "class=\"title_bor\">", "资金用途");
    kv["end_time"] = "";
    kv["invested_amount"] = doubletostring(s_atod(kv["borrowing_amount"].c_str()) - s_atod(filternum(extract(bstr,"class=\"bigSpan\">","align=\"right\">","","元")).c_str()));


    int investornum = 0;
    {
        string retstr;
        string::size_type tmp =  bstr.find("最近投资记录");
        if(tmp != string::npos){
            tmp = bstr.find("投标人",tmp+1);
        }
        if(tmp != string::npos){
            tmp =  bstr.find("<div",tmp+1);
        }
        if(tmp != string::npos){

            string striv = bstr.substr(tmp);
            string ivname;
            string ivaccount;
            string ivtime;
            while ((ivname = extract(striv, "</div>", "<td >", "\">", "</div>")) != "") {
                ivaccount = filternum(extract(striv, "</div>", "</div>", "￥", "</td>"));
                ivtime = extract(striv, "￥", "<td >", "\">", "</td>");
                ivtime = longtostring(stringtotime(ivtime.c_str(), "%Y-%m-%d %H:%M:%S"));
             
                retstr += ivtime + "|" + ivname + "|" + ivaccount + "|";
                
                if (striv.find("</tr>") == string::npos) {
                    break;
                }
                striv = striv.substr(striv.find("</tr>") + 1);
                investornum++;

            }
        }
        kv["investor"] = retstr;
    }
    kv["investors_volume"] = longtostring(investornum-1);
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

