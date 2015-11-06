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
    kv["site_id"] = "yijiedai";
    kv["borrower"] = extract(bstr,"用户信息", "</h4>","<span class=\"udata-id\">", "</span>");
    kv["project_name"] = extract(bstr, "<div class=\"BorrowView-Title\">", "", "<span>", "</span>");
    kv["project_id"] = idstr;
    kv["borrowing_amount"] = num_util(extract(bstr, "协议编号", "借款金额", "<font>", "元"));
    kv["annulized_rating"] = filternum(extract(bstr, "借款金额","年利率","<font>", "%"));
    kv["payment_method"] = extract(bstr, "年利率", "还款方式", "<font>", "</font>");
	kv["invested_amount"] = doubletostring(s_atod(kv["borrowing_amount"].c_str()) - \
			s_atod(num_util(extract(bstr,"可投金额","：","</dt>","元")).c_str()));
    kv["release_time"] = longtostring(stringtotime((extract(bstr, "借款金额", "开始时间", "：", "</font>")).c_str(),"%Y-%m-%d %H:%M:%S"));
    long long endtime = s_atol(extract(bstr, "", "", "", "|").c_str());
    if (endtime > 0) {
        kv["end_time"] = longtostring(endtime);
    }

    kv["project_details"] = extract(bstr, "审核评语", "</h4>","<ul class=\"borrow-con-opinion\">", "</ul>");


    {
        string retstr;
        string striv = extracthtml(bstr, "id=\"invest_data\"", "序号", "</li", "</ul");
        string ivname;
        string ivaccount;
        string ivtime;
        while ((ivname = extract(striv, "<li", "<span", "class=\"ui-span2\">", "</span>")) != "") {
            ivaccount = filternum(extract(striv, "<li", "<span", "class=\"ui-span3\">", "</span>"));
            ivtime = extract(striv, "<li", "</span>", "class=\"ui-span5\">", "</span>");
            ivtime = longtostring(stringtotime(ivtime.c_str(), "%Y-%m-%d %H:%M:%S"));

            retstr += ivtime + "|" + ivname + "|" + ivaccount + "|";

            string::size_type pos = striv.find("</li>");
            if (pos == string::npos) {
                break;
            }
            striv = striv.substr(pos + 1);
        }
        kv["investor"] = retstr;
    }
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

