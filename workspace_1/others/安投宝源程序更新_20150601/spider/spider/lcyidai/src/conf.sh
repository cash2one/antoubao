HOST="http://www.lcyidai.com:81"
INDEXPAGE="${HOST}/website/borrowInvestMainList.action"
POSTDATA="borrowLoanMain.status=&borrowLoanMain.loantype=&borrowLoanMain.loantitle=&page.size=10&page.total=933&page.current=\${i}"
DETAILPAGE="${HOST}/memberCenterBorrow/borrowLoanMainGet.action?id="
INVESTPAGE="${HOST}/memberCenterBorrow/getBorrowInvestDetail.action"
COOKIE=`cat COOKIE`  
GETPAGE="wget --no-cookies --header=\"Cookie: ${COOKIE}\" --keep-session-cookie"

