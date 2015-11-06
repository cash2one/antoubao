#ifndef _ATB_UTILS_H_
#define _ATB_UTILS_H_

#include <stddef.h>
#include <string>
#include <time.h>
#include <sys/time.h>
#include <vector>

using namespace std;

long s_atol(const char *str, int *is_succ = NULL);

string longtostring(long num);

double s_atod(const char *str, int *is_succ = NULL);

string doubletostring(double num);

long long gettimestamp(void);

struct timeval *ts2timeval(struct timeval *tv, long long timestamp);

size_t strtovstr(vector <string> &vstr, const char *str, const char *delim);

string vstrtostr(const vector <string> &vstr, const char *delim);

string lltostring(long long num);

long long s_atoll(const char *str, int *is_succ = NULL);

inline long long s_atoll(const string &str, int *is_succ = NULL) {return s_atoll(str.c_str(), is_succ);}

string gen_code(int len);

string gen_hexcode(int len);

string gen_deccode(int len);

string gmtdatetimestring(time_t t);

char *datetimestr(char *timestr, time_t t);

string datetimestring(time_t t);

time_t time2timestamp(int year, int mon, int day, int hour, int min, int sec);

inline int getdaynum(time_t nowtime) {return (int)((nowtime - 1262534400LL)/86400);} //since 2010-01-04 00:00:00 CST

inline int gethournum(time_t nowtime) {return (int)((nowtime - 1262534400LL)/3600);} //since 2010-01-04 00:00:00 CST

template <class T> T vecvalue(vector <T> &vt, size_t i, T def_t)
{
    if (i >= vt.size()) {
        return def_t;
    }
    return vt[i];
}

template <class T> void set_vecvalue(vector <T> &vt, size_t i, T t, T def_t)
{
    if (i >= vt.size()) {
        vt.resize(i + 1, def_t);
    }
    vt[i] = t;
}


char *readfile(const char *filename);

#endif

