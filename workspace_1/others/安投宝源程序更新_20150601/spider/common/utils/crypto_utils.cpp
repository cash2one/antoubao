#include "crypto_utils.h"
#include <openssl/sha.h>

using namespace std;

static const char *crypto_hexcode = "0123456789abcdef";

int sha256_digest(char *hash, const void *buf, size_t size)
{
    unsigned char tmp[SHA256_DIGEST_LENGTH];
    SHA256_CTX sha256ctx;
    if (SHA256_Init(&sha256ctx) != 1
            || SHA256_Update(&sha256ctx, buf, size) != 1
            || SHA256_Final(tmp, &sha256ctx) != 1) {
        return 0;
    }
    for (size_t i = 0; i < SHA256_DIGEST_LENGTH; i++) {
        hash[i*2] = crypto_hexcode[tmp[i] >> 4];
        hash[i*2+1] = crypto_hexcode[tmp[i] & 0x0F];
    }
    hash[SHA256_DIGEST_LENGTH * 2] = '\0';
    return 1;
}

