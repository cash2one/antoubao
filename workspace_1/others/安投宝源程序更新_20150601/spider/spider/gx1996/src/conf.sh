HOST="http://www.gx1996.com"
INDEXPAGE="${HOST}/defaults/user-invest.action?pageNum="
DETAILPAGE="${HOST}/defaults/toubiao.action?borrowId="
COOKIE=`cat COOKIE`
GETPAGE="wget --no-cookies --header=\"Cookie: ${COOKIE}\" --keep-session-cookie"
