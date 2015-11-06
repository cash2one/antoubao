HOST='http://www.haijincang.com'
INDEXPAGE="${HOST}/product/loan/querys/"
DETAILPAGE="${HOST}/product/loan/view/"
#INVESTORPAGE="${HOST}/invest/getrecord/id/"
COOKIE=`cat COOKIE`
GETPAGE="wget --header=\"Cookie: ${COOKIE}\""
