#ifndef _ATB_JSON_UTILS_H
#define _ATB_JSON_UTILS_H

#include <stdlib.h>
#include <string>
#include "json/value.h"
#include "json/reader.h"
#include "json/writer.h"
#include "utils.h"

using namespace std;
using namespace Json;

//json reader & writer
inline string jsontostring(const Value &json)
{
    FastWriter writer;
    return writer.write(json);
}
inline Value stringtojson(const char *buf, size_t len)
{
    Reader reader;
    Value json(objectValue);
    if (!reader.parse(buf, buf+len, json)) {
        json.clear();
    }
    return json;
}
inline Value stringtojson(const string &str)
{
    Reader reader;
    Value json(objectValue);
    if (!reader.parse(str, json)) {
        json.clear();
    }
    return json;
}

inline bool has_object_member(const Value &json, const char *field)
{
    return json.isObject() && json.isMember(field) && json[field].isObject();
}

inline bool has_array_member(const Value &json, const char *field)
{
    return json.isObject() && json.isMember(field) && json[field].isArray();
}

inline bool has_int_member(const Value &json, const char *field)
{
    return json.isObject() && json.isMember(field) && json[field].isInt();
}

inline bool has_string_member(const Value &json, const char *field)
{
    return json.isObject() && json.isMember(field) && json[field].isString();
}

inline bool has_double_member(const Value &json, const char *field)
{
    return json.isObject() && json.isMember(field) && json[field].isDouble();
}

inline bool get_int_member2(const Value &json, const char *field, int &i)
{
    if (has_int_member(json, field)) {
        i = json[field].asInt();
        return true;
    }
    return false;
}

inline bool get_string_member(const Value &json, const char *field, string &s)
{
    if (has_string_member(json, field)) {
        s = json[field].asString();
        return true;
    }
    return false;
}

inline bool get_double_member2(const Value &json, const char *field, double &d)
{
    if (has_double_member(json, field)) {
        d = json[field].asDouble();
        return true;
    }
    return false;
}

inline bool get_strlonglong_member(const Value &json, const char *field, long long &ll)
{
    long long llt;
    int succ;
    if (has_string_member(json, field)) {
        llt = s_atoll(json[field].asString().c_str(), &succ);
        if (succ) {
            ll = llt;
            return true;
        }
    }
    return false;
}

inline bool get_strint_member(const Value &json, const char *field, int &i)
{
    long long llt;
    if (get_strlonglong_member(json, field, llt)) {
        i = (int)llt;
        return true;
    }
    return false;
}

inline bool get_strdouble_member(const Value &json, const char *field, double &d)
{
    double dt;
    int succ;
    if (has_string_member(json, field)) {
        dt = s_atod(json[field].asString().c_str(), &succ);
        if (succ) {
            d = dt;
            return true;
        }
    }
    return false;
}

inline bool get_int_member(const Value &json, const char *field, int &i)
{
    return get_int_member2(json, field, i)
        || get_strint_member(json, field, i);
}

inline bool get_double_member(const Value &json, const char *field, double &d)
{
    if (get_double_member2(json, field, d) || get_strdouble_member(json, field, d)) {
        return true;
    }
    else {
        int i;
        if (get_int_member2(json, field, i)) {
            d = i;
            return true;
        }
    }
    return false;
}

#endif

