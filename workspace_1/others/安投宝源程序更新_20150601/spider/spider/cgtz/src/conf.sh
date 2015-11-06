HOST="https://www.cgtz.com"
LOANTYPE=("gyl","cgl","zbl")
INDEXPAGE="${HOST}/projects/t/\${LOANTYPE[\${t}]}/s//page/"
DETAILPAGE1="${HOST}/detail/"
DETAILPAGE2="${HOST}/ajax/TransactionQuery?id=\${BID}&page="
#COOKIE=`cat COOKIE`
#GETPAGE="wget --no-cookies --header=\"Cookie: ${COOKIE}\" --header=\"User-Agent:Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/39.0.2171.95 Safari/537.36\" --keep-session-cookie"
#GETPAGE="wget --no-cookies --header=\"Cookie: ${COOKIE}\" --keep-session-cookie"
GETPAGE="wget --header=\"X-Requested-With:XMLHttpRequest\""
