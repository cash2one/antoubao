HOST='http://www.zibenzaixian.com'
INDEXPAGE="${HOST}/jd/want_invest/forwardInvest/all.jd?orderType=&currentPage="
DETAILPAGE="${HOST}/borrow/forwardBorrowDetail.jd?borrowId="
#INVESTORPAGE="${HOST}/invest/getrecord/id/"
COOKIE=`cat COOKIE`
GETPAGE="wget --header=\"Cookie: ${COOKIE}\""
