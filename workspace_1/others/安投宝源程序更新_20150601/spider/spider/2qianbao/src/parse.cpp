#include <stdio.h>
#include <stdlib.h>
#include <ctype.h>
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
    kv["site_id"] = "2qianbao";
    kv["type"] = "1";
    kv["project_name"] = extract(bstr,"class=\"yrlc_cont\">","class=\"lc_tit01\">","class=\"lc_cont01\">", "</div>");
    kv["project_id"] = idstr;
    kv["annulized_rating"] = extracthtml(bstr, "class=\"lc_cont01_l\">", "今日年化收益", "<b>", "</b>");

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
