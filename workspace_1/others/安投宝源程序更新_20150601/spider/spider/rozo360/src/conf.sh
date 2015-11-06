HOST='http://www.rozo360.com'
INDEXPAGE="${HOST}/invest/index.html?status=1&page="
DETAILPAGE="${HOST}/invest/detail.html?borrowid="
BRECPAGE="${HOST}/detailTenderForJson.html?"
COOKIE=`cat COOKIE`
GETPAGE="wget --no-cookies --header=\"Cookie: ${COOKIE}\" --keep-session-cookie"
