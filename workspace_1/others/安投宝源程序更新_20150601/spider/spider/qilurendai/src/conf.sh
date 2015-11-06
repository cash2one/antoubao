HOST='http://www.qilurendai.com'
INDEXPAGE="${HOST}/invest/index"
DETAILPAGE="${HOST}/invest/a"
#INVESTORPAGE="${HOST}/invest/getrecord/id/"
COOKIE=`cat COOKIE`
GETPAGE="wget --header=\"Cookie: ${COOKIE}\""
