HOST="http://www.xiaoyoucai.com"
INDEXPAGE="${HOST}/loan/list_0_"
DETAILPAGE1="${HOST}/loanDetail?loanId="
DETAILPAGE2="${HOST}/getLoanInvestors?loanId=\${ID}&page="
DETAILPAGE3="${HOST}/getLoanInvestors?loanId=\${ID}&page=1"
COOKIE=`cat COOKIE`
GETPAGE="wget --no-cookies --header=\"Cookie: ${COOKIE}\" --keep-session-cookie"
