HOST='https://www.jiurong.com'
INDEXPAGE="${HOST}/loan/"
DETAILPAGE="${HOST}/loan/loanInfo/id/"
#INVESTORPAGE="${HOST}/invest/getrecord/id/"
COOKIE=`cat COOKIE`
GETPAGE="wget --header=\"Cookie: ${COOKIE}\""
