HOST="http://d.com.cn"
INDEXPAGE="${HOST}/lend-0-0-0-"
DETAILPAGE1="${HOST}/lend-"
DETAILPAGE_MONEY="${HOST}/ajaxserver.do?actions=planttrees,loan_\${ID}"
DETAILPAGE2="${HOST}/ajaxserver.do?actions=\${ID}_tender_page_"
#COOKIE=`cat COOKIE`
#GETPAGE="wget --no-cookies --header=\"Cookie: ${COOKIE}\" --header=\"User-Agent:Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/39.0.2171.95 Safari/537.36\" --keep-session-cookie"
#GETPAGE="wget --no-cookies --header=\"Cookie: ${COOKIE}\" --keep-session-cookie"
GETPAGE="wget"
