HOST="http://www.bangyoudai.com"
INDEXPAGE="${HOST}/deals/p-"
DETAILPAGE="${HOST}/deal/id-"
COOKIE=`cat COOKIE`
GETPAGE="wget --no-cookies --header=\"Cookie: ${COOKIE}\" --keep-session-cookie"
