HOST="http://www.ppmoney.com"
LOANTYPE=("anwenying" "zhitoubao" "xiaodaibao")
INDEXPAGE="${HOST}/\${LOANTYPE[\${t}]}?age="
DETAILPAGE1="${HOST}/Project/"
DETAILPAGE2="${HOST}/investment/records/\${BID}_\${i}_15"
DETAILPAGE="${HOST}/investment/records/\${BID}_1_15"
DETAILPAGE_MONEY="${HOST}/project/AsyncLoadPrjStatus/\${BID}"
#COOKIE=`cat COOKIE`
#GETPAGE="wget --no-cookies --header=\"Cookie: ${COOKIE}\" --header=\"User-Agent:Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/39.0.2171.95 Safari/537.36\" --keep-session-cookie"
#GETPAGE="wget --no-cookies --header=\"Cookie: ${COOKIE}\" --header=\"Accept-Language:zh-CN,zh;q=0.8,en;q=0.6\" --keep-session-cookie"
GETPAGE="wget"
