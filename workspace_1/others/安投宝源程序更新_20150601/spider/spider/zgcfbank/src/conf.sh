HOST="http://www.zgcfbank.com"
INDEXPAGE="${HOST}/tinvest/index.html?p="
DETAILPAGE1="${HOST}/tinvest/"
DETAILPAGE2="${HOST}/tinvest/investRecord?borrow_id=\${ID}&p="
#COOKIE=`cat COOKIE`
#GETPAGE="wget --no-cookies --header=\"Cookie: ${COOKIE}\" --header=\"User-Agent:Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/39.0.2171.95 Safari/537.36\" --keep-session-cookie"
#GETPAGE="wget --no-cookies --header=\"Cookie: ${COOKIE}\" --keep-session-cookie"
GETPAGE="wget"
