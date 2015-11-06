HOST='http://www.itouzi.com'
INDEXPAGE="${HOST}/dinvest/ajax/list?page="
DETAILPAGE="${HOST}/dinvest/"
INVESTORPAGE="${HOST}/dinvest/ajax/getInvestLog"
COOKIE=`cat COOKIE`
GETPAGE="wget --header=\"Cookie: ${COOKIE}\""
