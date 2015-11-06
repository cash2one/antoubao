#ifndef _ATB_CRYPTO_UTILS_H
#define _ATB_CRYPTO_UTILS_H

//-lssl -lcrypto
#include <string>
#include <openssl/sha.h>

using namespace std;

//length(hash) >= SHA256_DIGEST_LENGTH * 2 + 1
int sha256_digest(char *hash, const void *buf, size_t size);

//sha256_digest returns "" on error
inline string sha256_digest(const void *buf, size_t size)
{
    char hash[SHA256_DIGEST_LENGTH * 2 + 1];
    return sha256_digest(hash, buf, size) == 1 ? string(hash) : "";
}
inline string sha256_digest(const string &str) {return sha256_digest(str.c_str(), str.size());}

#endif

