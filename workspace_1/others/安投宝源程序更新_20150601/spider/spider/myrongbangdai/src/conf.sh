HOST="http://www.myrongbangdai.com"
INDEXPAGE="${HOST}/Credit/CreditList?PageIndex="
DETAILPAGE1="${HOST}/Credit/Project/"
DETAILPAGE2="${HOST}/Credit/ProjectInfo"
POSTDATA2="CreditId=\${ID}"
COOKIE=`cat COOKIE`
#GETPAGE="wget --no-cookies --header=\"Cookie: ${COOKIE}\" --header=\"User-Agent:Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/39.0.2171.95 Safari/537.36\" --keep-session-cookie"
GETPAGE="wget --no-cookies --header=\"Cookie: ${COOKIE}\" --keep-session-cookie"
