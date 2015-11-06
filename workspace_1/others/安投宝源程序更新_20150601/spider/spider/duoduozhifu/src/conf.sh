HOST="http://www.duoduozhifu.com"
INDEXPAGE="${HOST}/Data/borrow/queryList.do?currentPage="
DETAILPAGE1="${HOST}/Page/Invest/detail/borrowDetail.do?borrowId="
DETAILPAGE2="${HOST}/Data/borrow/queryInvest.do?borrowId=\${ID}&currentPage="
COOKIE=`cat COOKIE`
#GETPAGE="wget --no-cookies --header=\"Cookie: ${COOKIE}\" --header=\"User-Agent:Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/39.0.2171.95 Safari/537.36\" --keep-session-cookie"
GETPAGE="wget --no-cookies --header=\"Cookie: ${COOKIE}\"  --keep-session-cookie"
