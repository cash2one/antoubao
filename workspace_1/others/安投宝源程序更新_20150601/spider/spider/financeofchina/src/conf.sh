HOST='http://www.financeofchina.com'
LOANTYPE=("Loan" "tasteloan")
INDEXPAGE='${HOST}/${LTYPE}/Index?money=0-0&term=0-0&type=0&pageIndex='
DETAILPAGE='${HOST}/${LTYPE}/Details/'
INVESTORPAGE='${HOST}/${LTYPE}/LoanInfo?LoanId='

COOKIE=`cat COOKIE`
GETPAGE="wget --no-cookies --header=\"Cookie: ${COOKIE}\" --keep-session-cookie"

