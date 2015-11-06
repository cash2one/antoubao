HOST="http://www.moneydai.com"
INDEXPAGE="${HOST}/Touzi/index/p/"
DETAILPAGE1="${HOST}/Touzi/detail/oid/"
DETAILPAGE2="${HOST}/Touzi/page.html"
POSTDATA="page=\${i}&oid=\${ID}"
#COOKIE=`cat COOKIE`
#GETPAGE="wget --no-cookies --header=\"Cookie: ${COOKIE}\" --header=\"User-Agent:Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/39.0.2171.95 Safari/537.36\" --keep-session-cookie"
#GETPAGE="wget --no-cookies --header=\"Cookie: ${COOKIE}\" --keep-session-cookie"
GETPAGE="wget"
