HOST='https://www.chenghuitong.net'
INDEXPAGE="${HOST}/borrow/default-index.html?page="
DETAILPAGE="${HOST}/borrow/default-info-id-"
#INVESTORPAGE="${HOST}/Loan/LoanInfo?LoanId="

COOKIE=`cat COOKIE`
GETPAGE="wget --no-cookies --header=\"Cookie: ${COOKIE}\" --keep-session-cookie"

