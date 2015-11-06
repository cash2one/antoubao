#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <stdint.h>
#include <iostream>
#include <string>
#include <vector>
#include <map>
#include <sys/types.h>
#include <sys/stat.h>
#include <unistd.h>
#include <arpa/inet.h>

#include "spi_utils.h"

using namespace std;

string filternum(const string &str)
{
    string ret;
    for (size_t i = 0; i < str.size(); i++) {
        if ((str[i] >= '0' && str[i] <= '9')
                || str[i] == '.' || str[i] == '+' || str[i] == '-') {
            ret += str[i];
        }
    }
    return ret;
}

char *timetostring(char *str, const char *format, time_t t)
{
    struct tm tm1;
    localtime_r(&t, &tm1);
    char c[] = {'Y', 'm', 'd', 'H', 'M', 'S'};
    int l[] = {4, 2, 2, 2, 2, 2};
    int v[] = {tm1.tm_year + 1900, tm1.tm_mon + 1, tm1.tm_mday, tm1.tm_hour, tm1.tm_min, tm1.tm_sec};
    char *p = str;
    for (; *format; format++) {
        if (*format == '%') {
            format++;
            if (*format == '%') {
                *p++ = '%';
            }
            else {
                size_t i = 0;
                for (i = 0; i < sizeof(c)/sizeof(c[0]); i++) {
                    if (*format == c[i]) {
                        int tlen = sprintf(p, "%0*d", l[i], v[i]);
                        p += tlen;
                        break;
                    }
                }
                if (i == sizeof(c)/sizeof(c[0])) {
                    *p++ = '%';
                    format--;
                }
            }
        }
        else {
            *p++ = *format;
        }
    }
    *p = '\0';
    return str;
}

time_t stringtotime(const char *str, const char *format)
{
    int v[] = {0, 0, 0, 0, 0, 0};
    char c[] = {'Y', 'm', 'd', 'H', 'M', 'S'};
    for (; *format; format++) {
        if (*format == '%') {
            format++;
            if (*format == '%') {
                if (*str != '%') {
                    return (time_t)-1;
                }
                str++;
            }
            else {
                size_t i = 0;
                for (i = 0; i < sizeof(c)/sizeof(c[0]); i++) {
                    if (*format == c[i]) {
                        v[i] = strtol(str, (char **)&str, 10);
                        break;
                    }
                }
                if (i == sizeof(c)/sizeof(c[0])) {
                    if (*str != '%') {
                        return (time_t) -1;
                    }
                    str++;
                    format--;
                }
            }
        }
        else if (*str == *format) {
            str++;
        }
        else {
            return (time_t)-1;
        }
    }
    struct tm tm1;
    time_t t = 0;
    localtime_r(&t, &tm1);
    tm1.tm_year = v[0] - 1900;
    tm1.tm_mon = v[1] - 1;
    tm1.tm_mday = v[2];
    tm1.tm_hour = v[3];
    tm1.tm_min = v[4];
    tm1.tm_sec = v[5];
    return mktime(&tm1);
}

typedef struct _str_pair {
    char esc_seq[32];
    char seq[32];
} str_pair;

str_pair html_tag[] = {
    {"</p>", "\n\n"},
    {"</p ", "\n\n"},
    {"<br", "\n"},
    {"<div>", "\n"},
    {"<div ", "\n"},
    {"<table>", "\n"},
    {"<table ", "\n"},
    {"<tr>", "\n"},
    {"<tr ", "\n"},
    {"<ol>", "\n"},
    {"<ol ", "\n"},
    {"<ul>", "\n"},
    {"<ul ", "\n"},
    {"<li>", "\n"},
    {"<li ", "\n"},
    {"<dl>", "\n"},
    {"<dl ", "\n"},
    {"<dt>", "\n"},
    {"<dt ", "\n"},
};

str_pair esc_str[] = {
    {"&amp;", "&"},
    {"&nbsp;", " "},
    {"&lt;", "<"},
    {"&gt;", ">"},
    {"&#92;", "\\"},
    {"&#35;", "#"},
};

inline static string unicode2utf8(uint32_t code)
{
    char buf[] = {
        0x80 | ((code >> 30) & 0x3F),
        0x80 | ((code >> 24) & 0x3F),
        0x80 | ((code >> 18) & 0x3F),
        0x80 | ((code >> 12) & 0x3F),
        0x80 | ((code >> 6) & 0x3F),
        0x80 | (code & 0x3F),
        '\0',
    };
    if (code <= 0x0000007F) {
        buf[5] = (char)code;
        return string(buf + 5);
    }
    else if (code <= 0x000007FF) {
        buf[4] |= 0xC0;
        return string(buf + 4);
    }
    else if (code <= 0x0000FFFF) {
        buf[3] |= 0xE0;
        return string(buf + 3);
    }
    else if (code <= 0x001FFFFF) {
        buf[2] |= 0xF0;
        return string(buf + 2);
    }
    else if (code <= 0x03FFFFFF) {
        buf[1] |= 0xF8;
        return string(buf + 1);
    }
    else if (code <= 0x7FFFFFFF) {
        buf[0] |= 0xFC;
        return string(buf);
    }
    return "?";
}

string dhtml(const string &src)
{
    string dst;
    for (size_t i = 0; i < src.size(); i++) {
        switch (src[i]) {
            case '<':
                {
                    string::size_type n = src.find('>', i);
                    if (n != string::npos) {
                        for (size_t idx = 0; idx < sizeof(html_tag)/sizeof(html_tag[0]); idx++) {
                            if (strncasecmp(src.c_str() + i, html_tag[idx].esc_seq, strlen(html_tag[idx].esc_seq)) == 0) {
                                dst += string(html_tag[idx].seq);
                                break;
                            }
                        }
                        i += (n - i);
                    }
                    else {
                        dst += src[i];
                    }
                }
                break;
            case '&':
                {
                    string::size_type n = src.find(';', i);
                    if (n != string::npos) {
                        if (src[i+1] == '#') {
                            unsigned int ucode = 0;
                            if (sscanf(src.c_str()+i+2, "%u", &ucode) == 1) {
                                dst += unicode2utf8(ucode);
                            }
                            else {
                                dst += "?";
                            }
                        }
                        else {
                            string s = "?";
                            for (size_t idx = 0; idx < sizeof(esc_str)/sizeof(esc_str[0]); idx++) {
                                if (strncasecmp(src.c_str() + i, esc_str[idx].esc_seq, strlen(esc_str[idx].esc_seq)) == 0) {
                                    s = string(esc_str[idx].seq);
                                    break;
                                }
                            }
                            dst += s;
                        }
                        i += (n - i);
                    }
                    else {
                        dst += src[i];
                    }
                }
                break;
            case ' ':
            case '\t':
            case '\r':
            case '\n':
            case '\v':
                if (dst.size() == 0 || dst[dst.size()-1] != ' ') {
                    dst += " ";
                }
                break;
            default:
                dst += src[i];
                break;
        }
    }
    string::size_type h = dst.find_first_not_of(" \t\n\r\v");
    string::size_type e = dst.find_last_not_of(" \t\n\r\v");
    if (h != string::npos && e != string::npos && e >= h) {
        return dst.substr(h, e-h+1);
    }
    return dst;
}

string extracthtml(const string &src, const string &anchor1, const string &anchor2, const string &anchor3, const string &end)
{
    string::size_type idx1 = src.find(anchor1);
    if (idx1 == string::npos) {
        return "";
    }
    string::size_type idx2 = src.find(anchor2, idx1 + anchor1.size());
    if (idx2 == string::npos) {
        return "";
    }
    string::size_type idx3 = src.find(anchor3, idx2 + anchor2.size());
    if (idx3 == string::npos) {
        return "";
    }
    string::size_type idxe = src.find(end, idx3 + anchor3.size());
    if (idxe == string::npos) {
        return "";
    }
    return src.substr(idx3 + anchor3.size(), idxe - idx3 - anchor3.size());
}

string extract(const string &src, const string &anchor1, const string &anchor2, const string &anchor3, const string &end)
{
    string::size_type idx1 = src.find(anchor1);
    if (idx1 == string::npos) {
        return "";
    }
    string::size_type idx2 = src.find(anchor2, idx1 + anchor1.size());
    if (idx2 == string::npos) {
        return "";
    }
    string::size_type idx3 = src.find(anchor3, idx2 + anchor2.size());
    if (idx3 == string::npos) {
        return "";
    }
    string::size_type idxe = src.find(end, idx3 + anchor3.size());
    if (idxe == string::npos) {
        return "";
    }
    return dhtml(src.substr(idx3 + anchor3.size(), idxe - idx3 - anchor3.size()));
}

int savestringmap(const map <string, string> &strmap, const char *filename)
{
    FILE *fp = fopen(filename, "wb");
    if (!fp) {
        return 1;
    }
    uint32_t ver = htonl(1);
    fwrite(&ver, sizeof(uint32_t), 1, fp);
    uint32_t num = htonl((uint32_t)strmap.size());
    fwrite(&num ,sizeof(uint32_t), 1, fp);
    for (map <string, string>::const_iterator iter = strmap.begin(); iter != strmap.end(); iter++) {
        uint32_t len = htonl((uint32_t)iter->first.size());
        fwrite(&len, sizeof(uint32_t), 1, fp);
        fwrite(iter->first.c_str(), sizeof(char), iter->first.size(), fp);
        len = htonl((uint32_t)iter->second.size());
        fwrite(&len , sizeof(uint32_t), 1, fp);
        fwrite(iter->second.c_str(), sizeof(char), iter->second.size(), fp);
    }
    fclose(fp);
    return 0;
}

int loadstringmap(map <string, string> &strmap, const char *filename)
{
    char *buf = readfile(filename);
    if (!buf) {
        return 1;
    }
    char *p = buf;
    uint32_t ver = *((uint32_t *)p);
    ver = ntohl(ver);
    p += sizeof(uint32_t);
    uint32_t num = ntohl(*((uint32_t *)p));
    p += sizeof(uint32_t);
    for (uint32_t i = 0; i < num; i++) {
        uint32_t keylen = ntohl(*((uint32_t *)p));
        p += sizeof(uint32_t);
        string key = string(p, keylen);
        p += keylen;
        uint32_t vlen = ntohl(*((uint32_t *)p));
        p += sizeof(uint32_t);
        string value = string(p, vlen);
        p += vlen;
        strmap[key] = value;
    }
    free(buf);
    return 0;
}

int printstringmap(const map <string, string> &strmap)
{
    for (map <string, string>::const_iterator iter = strmap.begin(); iter != strmap.end(); iter++) {
        cout<<iter->first<<":"<<iter->second<<endl;
    }
    return 0;
}

string strreplace(const string &src, const string &sub, const string &rep, int all)
{
    if (sub == rep) {
        return src;
    }
    string ret = src;
    string::size_type pos = ret.find(sub);
    while (pos != string::npos) {
        ret.replace(pos, sub.size(), rep);
        if (!all) {
            break;
        }
        pos = ret.find(sub);
    }
    return ret;
}

string loanperiod_util(const string &lpstr)
{
    double lp = s_atod(filternum(lpstr).c_str());
    if (lpstr.find("月") != string::npos) {
        lp *= 30.0;
    }
    return doubletostring(lp);
}

string num_util(const string &num)
{
    double d = s_atod(filternum(num).c_str());
    if (num.find("万") != string::npos) {
        d *= 10000.0;
    }
    return doubletostring(d);
}

