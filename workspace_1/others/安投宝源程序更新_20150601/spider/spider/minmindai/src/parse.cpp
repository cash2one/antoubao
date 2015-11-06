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
    kv["site_id"] = "minmindai";
    kv["borrower"] = extract(bstr, "个人借款者信息", "用户名：", "target=\"_blank\">", "</a>");
    kv["project_name"] = extract(bstr, "class=\"warp2\" style=\"margin-bottom:20px;\"", "class=\"page_info_name\"", ">", "<span>");
    kv["project_id"] = idstr;
    kv["borrowing_amount"] = filternum(extract(bstr, "class=\"page_info\"", "class=\"page_info_list\"", "<strong>", "</strong>"));
    kv["annulized_rating"] = filternum(extract(bstr, "class=\"page_info\"", "借款金额", "<strong>", "</strong>"));
    kv["payment_method"] = extract(bstr, "class=\"page_info\"", "还款周期", "<span>", "</span>");
    kv["loan_period"] = loanperiod_util(extract(bstr, "class=\"page_info\"", "年利率", "<strong>", "</strong>"));

    kv["invested_amount"] = filternum(extract(bstr, "class=\"page_info\"", "本息共计", "<span>", "</span>"));
    kv["release_time"] = longtostring(stringtotime(extract(bstr, "class=\"page_info\"", "class=\"page_info_right\"", "<span>", "</span>").c_str(), "%Y-%m-%d %H:%M"));
    {
        string trt = extract(bstr, "<div class=\"page_info_right\">", "项目结束", ">", "剩余时间");
        int d, h, m;
        if (sscanf(trt.c_str(), "%d天%d时%d分", &d, &h, &m) == 3) {
            kv["end_time"] = longtostring(time(NULL) + d*86400 + h*3600 + m*60);
        }
    }
    kv["project_details"] = extract(bstr, "借款详情介绍", "<strong>一、我的借款描述：</strong>", "<br />", "</div>");

    string invstr;

    string tmps = extracthtml(bstr, "class=\"page_pinggu_buy\"", "<div class=\"buy\">", "<ul>", "</div>");

    string flag("<li>");
    size_t beg, end;
    beg = tmps.find(flag);

    while ( beg != string::npos )
    {  
        end = tmps.find(flag, beg+flag.size());

        string s;
        if (end != string::npos)
        {   
            s = tmps.substr(beg+flag.size(), end-beg);
        }   
        else
        {   
            s = tmps.substr(beg+flag.size());
        }   

        string uname = extract(s, "class=\"iCol5\"", "target=\"_blank\"", ">", "</a>");
        string account = filternum(extract(s, "class=\"iCol6\"", ">", "￥", "</span>"));
        string addtime = extract(s, "<span", "class=\"iCol7\"", ">", "</span>");

        invstr += longtostring(stringtotime(addtime.c_str(), "%Y-%m-%d %H:%M:%S")) + "|" + uname + "|" + account + "|";

        beg = end;
    }   

    kv["investor"] = invstr;

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

