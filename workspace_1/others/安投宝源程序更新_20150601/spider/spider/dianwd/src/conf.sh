HOST="http://www.dianwd.com"
LOANTYPE=("?" "&")
INDEXPAGE="${HOST}/invest.html?type=bill\${LOANTYPE[\${t}]}page="
DETAILPAGE1="${HOST}/invest/item"
DETAILPAGE2="${HOST}/invest/item\${ID}?page="
#COOKIE=`cat COOKIE`
#GETPAGE="wget --no-cookies --header=\"Cookie: ${COOKIE}\" --header=\"User-Agent:Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/39.0.2171.95 Safari/537.36\" --keep-session-cookie"
#GETPAGE="wget --no-cookies --header=\"Cookie: ${COOKIE}\" --keep-session-cookie"
GETPAGE="wget"
