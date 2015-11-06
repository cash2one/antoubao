HOST='http://www.gxyclub.com'
INDEXPAGE="${HOST}/finance.do?curPage="
DETAILPAGE="${HOST}/financeDetail.do?id="
INVESTORPAGE="${HOST}/getInvestList.do?"
COOKIE=`cat COOKIE`
GETPAGE="wget --header=\"Cookie: ${COOKIE}\""
