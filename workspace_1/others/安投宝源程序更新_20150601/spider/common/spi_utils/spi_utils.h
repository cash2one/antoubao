#ifndef _ATB_SPI_UTILS_H
#define _ATB_SPI_UTILS_H

#include <stdio.h>
#include <stdlib.h>
#include <string>
#include <map>
#include <time.h>
#include "json/json.h"
#include "../utils/utils.h"

using namespace std;
using namespace Json;

string filternum(const string &str);

char *timetostring(char *str, const char *format, time_t t);
time_t stringtotime(const char *str, const char *format);

string strreplace(const string &src, const string &sub, const string &rep, int all = 0);

//html extractor
string dhtml(const string &src);
string extract(const string &src, const string &anchor1, const string &anchor2, const string &anchor3, const string &end);
string extracthtml(const string &src, const string &anchor1, const string &anchor2, const string &anchor3, const string &end);

//string map function
int savestringmap(const map <string, string> &strmap, const char *filename);
int loadstringmap(map <string, string> &strmap, const char *filename);
int printstringmap(const map <string, string> &strmap);

//time or number string utils
string loanperiod_util(const string &lpstr);
string num_util(const string &num);

#endif

