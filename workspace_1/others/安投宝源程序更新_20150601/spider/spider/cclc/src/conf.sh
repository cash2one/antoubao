HOST="https://www.cclc.co"
INDEXPAGE="${HOST}/debts?pn="
DETAILPAGE1="${HOST}/debt/"
DETAILPAGE2="${HOST}/debt/getInvest"
POSTDATA="pn=\${i}&s=10&id=\${BID}&_csrf=\${value}"
POSTDATA1="pn=1&s=10&id=\${BID}&_csrf=\${value}"
COOKIE=`cat COOKIE`
#GETPAGE="wget --no-cookies --header=\"Cookie: ${COOKIE}\" --header=\"User-Agent:Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/39.0.2171.95 Safari/537.36\" --keep-session-cookie"
GETPAGE="wget --no-cookies --header=\"Cookie: ${COOKIE}\" --keep-session-cookie"
