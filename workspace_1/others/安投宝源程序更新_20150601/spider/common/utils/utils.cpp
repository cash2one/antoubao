#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <errno.h>
#include <sys/time.h>
#include <sys/types.h>
#include <sys/stat.h>
#include <unistd.h>
#include "utils.h"

long long gettimestamp(void)
{
    struct timeval tv1;
    gettimeofday(&tv1, NULL);
    return tv1.tv_sec * 1000000LL + tv1.tv_usec;
}

struct timeval *ts2timeval(struct timeval *tv, long long timestamp)
{
    tv->tv_sec = timestamp / 1000000;
    tv->tv_usec = timestamp % 1000000;
    return tv;
}

string lltostring(long long num)
{
    char buf[128];
    if (snprintf(buf, 128, "%lld", num) < 128) {
        return string(buf);
    }
    return "NaN";
}

string longtostring(long num)
{
    char buf[128];
    if (snprintf(buf, 128, "%ld", num) < 128) {
        return string(buf);
    }
    return "NaN";
}

string doubletostring(double num)
{
    char buf[128];
    if (snprintf(buf, 128, "%f", num) < 128) {
        return string(buf);
    }
    return "NaN";
}

long s_atol(const char *str, int *is_succ)
{
    if (str == NULL) {
        if (is_succ) {
            *is_succ = 0;
        }
        return 0;
    }
    char *endp = NULL;
    errno = 0;
    long ret = strtol(str, &endp, 10);
    if (is_succ) {
        *is_succ = 1;
        if (errno != 0 || endp == str || *endp != '\0') {
            *is_succ = 0;
        }
    }
    return ret;
}

long long s_atoll(const char *str, int *is_succ)
{
    if (str == NULL) {
        if (is_succ) {
            *is_succ = 0;
        }
        return 0;
    }
    char *endp = NULL;
    errno = 0;
    long long ret = strtoll(str, &endp, 10);
    if (is_succ) {
        *is_succ = 1;
        if (errno != 0 || endp == str || *endp != '\0') {
            *is_succ = 0;
        }
    }
    return ret;
}

double s_atod(const char *str, int *is_succ)
{
    if (str == NULL) {
        if (is_succ) {
            *is_succ = 0;
        }
        return 0;
    }
    char *endp = NULL;
    errno = 0;
    double ret = strtod(str, &endp);
    if (is_succ) {
        *is_succ = 1;
        if (errno != 0 || endp == str || *endp != '\0') {
            *is_succ = 0;
        }
    }
    return ret;
}

static const char *bcode = "0123456789abcdefghijklmnopqrstuvwxyz";
static const int bcode_size = 36;
static const char *hcode = "0123456789abcdef";
static const int hcode_size = 16;
static const char *dcode = "0123456789";
static const int dcode_size = 10;

string gen_code_in(const char *code, int code_size, int len)
{
    string ret;
    ret.resize(len, '-');
    for (int i = 0; i < len; i++) {
        ret[i] = code[rand()%code_size];
    }
    return ret;
}

string gen_code(int len)
{
    return gen_code_in(bcode, bcode_size, len);
}

string gen_hexcode(int len)
{
    return gen_code_in(hcode, hcode_size, len);
}

string gen_deccode(int len)
{
    return gen_code_in(dcode, dcode_size, len);
}

const char *wdaystr[] = {
    "Sun",
    "Mon",
    "Tue",
    "Wed",
    "Thu",
    "Fri",
    "Sat",
};

const char *monstr[] = {
    "Jan",
    "Feb",
    "Mar",
    "Apr",
    "May",
    "Jun",
    "Jul",
    "Aug",
    "Sep",
    "Oct",
    "Nov",
    "Dec",
};

string gmtdatetimestring(time_t t)
{
    struct tm tm1;
    gmtime_r(&t, &tm1);
    char str[128];
    sprintf(str, "%s, %02d %s %04d %02d:%02d:%02d GMT", wdaystr[tm1.tm_wday], tm1.tm_mday, monstr[tm1.tm_mon],
            tm1.tm_year+1900, tm1.tm_hour, tm1.tm_min, tm1.tm_sec);
    return string(str);
}

char *datetimestr(char *timestr, time_t t)
{
    struct tm tm1;
    localtime_r(&t, &tm1);
    sprintf(timestr, "%04d-%02d-%02d %02d:%02d:%02d", 1900+tm1.tm_year, tm1.tm_mon+1, tm1.tm_mday, tm1.tm_hour, tm1.tm_min, tm1.tm_sec);
    return timestr;
}

string datetimestring(time_t t)
{
    char timestr[128];
    datetimestr(timestr, t);
    return string(timestr);
}

size_t strtovstr(vector <string> &vstr, const char *str, const char *delim)
{
    char *buf = (char *)malloc(sizeof(char)*(strlen(str)+1));
    if (buf == NULL)
        return 0;
    strcpy(buf, str);
    vstr.clear();
    char *p = strtok(buf, delim);
    while (p) {
        vstr.push_back(string(p));
        p = strtok(NULL, delim);
    }
    free(buf);
    return vstr.size();
}

string vstrtostr(const vector <string> &vstr, const char *delim)
{
    string str;
    for (size_t i = 0; i < vstr.size(); i++) {
        str += ((i==0?"":delim) + vstr[i]);
    }
    return str;
}

time_t time2timestamp(int year, int mon, int day, int hour, int min, int sec)
{
    struct tm tm1;
    time_t t = 0;
    localtime_r(&t, &tm1);
    tm1.tm_year = year - 1900;
    tm1.tm_mon = mon - 1;
    tm1.tm_mday = day;
    tm1.tm_hour = hour;
    tm1.tm_min = min;
    tm1.tm_sec = sec;
    return mktime(&tm1);
}

char *readfile(const char *filename)
{
    struct stat st;
    if (stat(filename, &st) != 0) {
        return NULL;
    }
    char *buf = (char *)malloc(st.st_size + 1);
    FILE *fp = fopen(filename, "rb");
    if (buf && fp && fread(buf, 1, st.st_size, fp) == (size_t)st.st_size) {
        fclose(fp);
        buf[st.st_size] = '\0';
        return buf;
    }
    if (buf) {
        free(buf);
    }
    if (fp) {
        fclose(fp);
    }
    return NULL;
}

