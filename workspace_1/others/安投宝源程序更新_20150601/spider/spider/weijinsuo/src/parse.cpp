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
	map<string,string> kv;
	string invstr;
	sprintf(filename, "html/%s", idstr);
    char *buf = readfile(filename);
	string investr;
	if(buf){
		char *p = buf;
		size_t buflen = strlen(buf);
        string jstr = string(p, buflen);
		Value json = stringtojson(jstr); 
		if (has_object_member(json, "result")) {
			int ival;
			string str;
			kv["site_id"] = "weijinsuo";
			kv["project_id"] = idstr;
			if(get_int_member(json["result"], "goalMoney", ival))
				kv["borrow_amount"] = longtostring(ival);
			if(get_int_member(json["result"], "currentMomey", ival))
				kv["invested_amount"] = longtostring(ival);
			if(get_string_member(json["result"], "interestRate", str))
				kv["annulized_rating"] = filternum(str);
			if(get_int_member(json["result"], "userid", ival))
				kv["borrower"] = longtostring(ival);
			if(get_string_member(json["result"], "loanPurposeDesc", str))
                kv["project_name"] = str;
			if(get_string_member(json["result"], "repaymentMonth", str))
			{
				if(get_int_member(json["result"], "month_or_day", ival))
				{
					if(ival == 1)
						kv["loan_period"] =longtostring(s_atol(str.c_str()) * 30);
					if(ival == 2)
						kv["loan_period"] = longtostring(s_atol(str.c_str()));

				}
			}
			if(get_string_member(json["result"], "uplinetime", str))
				kv["release_time"] = str;
			if(get_string_member(json["result"], "fullscaletime", str))
			    kv["end_time"] = str;
			if(get_string_member(json["result"], "type_name", str))
				kv["payment_method"] = str;
			if(get_string_member(json["result"], "description", str))
				kv["project_details"] = str;

		}
	}

	free(buf);



	sprintf(filename, "html/%s.brec", idstr);
    buf = readfile(filename);
 //   string invstr;
    if (buf) {
        char *p = buf;
        size_t buflen = strlen(buf);
		string jstr = string(p, buflen);
		Value json = stringtojson(jstr);
		string amount;
		string name; 
		string addtime;
		if (has_object_member(json, "result") && has_array_member(json["result"],"bidLog")) {
				for (int i = 0; i < json["result"]["bidLog"].size(); i++) {
				if (!get_string_member(json["result"]["bidLog"][i], "amountOfInvest", amount)
						|| !get_string_member(json["result"]["bidLog"][i], "realName", name)
						|| !get_string_member(json["result"]["bidLog"][i], "investEffectDate", addtime)) {
					continue;
				}
				invstr += longtostring(stringtotime(addtime.c_str(), "%Y-%m-%d %H:%M:%S")) + "|" + name + "|" + amount + "|";
//              invstr += longtostring(stringtotime(addtime.c_str(), "%Y-%m-%d %H:%M:%S")) + "|" + json["result"]["bidLog"][i]["realName"] + "|" + json["result"]["bidLog"][i]["amountOfInvest"]+ "|";
			}
				kv["investornum"] = longtostring(json["result"]["bidLog"].size());
		}
		if(has_array_member(json, "result")){
			for (int i = 0; i < json["result"].size(); i++){
			if (!get_string_member(json["result"][i], "amountOfInvest", amount)
					|| !get_string_member(json["result"][i], "realName", name)
					|| !get_string_member(json["result"][i], "investEffectDate", addtime)){
			continue;
			}
			invstr += longtostring(stringtotime(addtime.c_str(), "%Y-%m-%d %H:%M:%S")) + "|" + name + "|" + amount + "|";

			}
			kv["investornum"] = longtostring(json["result"].size());
		}
	}
	free(buf);
	kv["investor"] = invstr;

	printstringmap(kv);
	//    if (kv["project_id"] == "" || kv["release_time"] == "" || kv["borrower"] == "") {
	//        return 1;
	//    }

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

