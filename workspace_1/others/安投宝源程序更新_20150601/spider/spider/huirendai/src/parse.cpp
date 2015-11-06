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
    kv["site_id"] = "jiurong";
    kv["project_name"] = extract(bstr, "<meta http-equiv=", "<meta name=", "<title>"," - ");
  // kv["borrower"] = extract(bstr,"","","","");
    kv["project_id"] = extract(bstr,"class=\"hrd_grid\">","class=\"sumtitle\">","invest/a",".html");
    kv["borrowing_amount"] = extract(bstr,"<ul class=\"sumul\">","信用评级","<p>","元</p>");
    string::size_type pos = kv["borrowing_amount"].find("万");
    if (pos != string::npos){
        kv["borrowing_amount"] = doubletostring(atof(filternum(kv["borrowing_amount"]).c_str())*10000);
    } else{
        kv["borrowing_amount"] = doubletostring(atof(filternum(kv["borrowing_amount"]).c_str()));
    }  

    kv["annulized_rating"] = filternum(extract(bstr,"元</p>","借款金额", "<span><b>", "</b><i>%"));
  //  kv["payment_method"] = extract(bstr,"<li class=\"none_b\">","还款方式","","");
    kv["loan_period"] = extract(bstr, "借款金额", "<li class=\"limax\">", "<p>","</p>");
    int pos1 = kv["loan_period"].find("月");
    if (pos1 != -1) {
        kv["loan_period"] = longtostring(atof(kv["loan_period"].c_str())*30);
    }
    else{

        kv["loan_period"] = longtostring(atof(kv["loan_period"].c_str()));
    }

     kv["invested_amount"] = doubletostring(s_atod(kv["borrowing_amount"].c_str()) - s_atod(filternum(extract(bstr,"期限","libgnone\">","<p>","元</p>")).c_str()));
   //  kv["release_time"] = extract(bstr,"还款方式","发布时间","\">","</span>");
    //   kv["end_time"] = extract(bstr,"<ul class=\"d_date\">","<s>","满标时间：","</li>");  
    {
            string tmp;
            string::size_type startpos = bstr.find("备注");
            if (startpos != string::npos) {
                string::size_type endpos = bstr.find("<div class=\"record", startpos);
                if (endpos != string::npos) {
                    tmp = bstr.substr(startpos, endpos - startpos);
                }
            }
            string ivname;
            string ivaccount;
            string ivtime;
            string retstr;
            while ((ivname = extract(tmp, "", "<dd >", "<font>", "</font>")) != "") {
                ivaccount = extract(tmp, "%</font>", "元</font>", "<font>","元</font>");
                ivtime = extract(tmp, "元</font>", "</font>", "<i>", "</i>");
                ivtime = longtostring(stringtotime(ivtime.c_str(), "%Y-%m-%d %H:%M:%S")
                        );
                retstr += ivtime + "|" + ivname + "|" + ivaccount + "|";
                string::size_type pos = tmp.find("<font></font>");
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
