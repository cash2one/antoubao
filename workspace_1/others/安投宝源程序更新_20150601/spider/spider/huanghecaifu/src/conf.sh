HOST='https://www.huanghecaifu.com'
INDEXPAGE="${HOST}/invest/index"
DETAILPAGE="${HOST}/invest/a"

COOKIE=`cat COOKIE`
GETPAGE="wget --no-cookies --header=\"Cookie: ${COOKIE}\" --keep-session-cookie"

