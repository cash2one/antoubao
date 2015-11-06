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
    kv["site_id"] = "huanghecaifu";
    kv["borrower"] = extract(bstr,"class=\"title title_2\">","class=\"zhuanrang left\">","（借款人：","）");
    kv["project_name"] = extract(bstr, "class=\"project-item\"","class=\"title title_2\">","<a>","</a>");
    kv["project_id"] = idstr;
    kv["borrowing_amount"] = filternum(extract(bstr, "class=\"left span6\">", "融资总额", "￥", "</div>"));
    kv["annulized_rating"] = filternum(extracthtml(bstr, "class=\"left span6\">","预期年化利率","class=\"f22 f_red\">", "%"));
    kv["payment_method"] = extract(bstr, "class=\"wall fix\">", "class=\"fix\">", "还款方式", "</div>");
    kv["loan_period"] = longtostring(s_atod(extract(bstr,"class=\"left span6\">","借款期限","class=\"f22 f_red\">","个月").c_str())*30);
    kv["release_time"] = "";
    kv["project_details"] = extract(bstr, "class=\"right_ziliao\">", "个人资料", "class=\"shenhe\">", "</ul>");
    kv["end_time"] = "";
    kv["invested_amount"] = doubletostring(s_atod(kv["borrowing_amount"].c_str()) - s_atod(filternum(extract(bstr,"class=\"Transfer\">","class=\"shengyu_icon\"","￥","</div>")).c_str()));


    printf(filename, "html/%s.brec", idstr);
    buf = readfile(filename);

    int investornum = 0;
    {
        string retstr;
        string::size_type tmp =  bstr.find("投标记录");
        if(tmp != string::npos){
            tmp = bstr.find("投标人",tmp+1);
        }
        if(tmp != string::npos){
            tmp =  bstr.find("</tr>",tmp+1);
        }
        if(tmp != string::npos){
            tmp =  bstr.find("<td>",tmp+1);
        }
        if(tmp != string::npos){

            string striv = bstr.substr(tmp);
            string ivname;
            string ivaccount;
            string ivtime;
            while ((ivname = extract(striv, "", "</td>", "<td>", "</td>")) != "") {
                ivaccount = filternum(extract(striv, "%", "</td>", "<td>", "元"));
                ivtime = extract(striv, "元", "元", "<td>", "</td>");
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

