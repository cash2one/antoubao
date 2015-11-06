HOST="http://www.pangmao.com"
INDEXPAGE="${HOST}/loan/ajaxQuery.do"
POSTDATA_INDEX="loanType=-1&term=-1&rate=-1&creditLevel=-1&requestPage=\${i}&pageSize=8"
DETAILPAGE1="${HOST}/loan/detail.do?loanApproveId="
DETAILPAGE2="${HOST}/loan/ajaxCreditorRight.do"
POSTDATA2="approveStatusCd=0&loanApproveId=\${ID}"
COOKIE=`cat COOKIE`
#GETPAGE="wget --no-cookies --header=\"Cookie: ${COOKIE}\" --header=\"User-Agent:Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/39.0.2171.95 Safari/537.36\" --keep-session-cookie"
GETPAGE="wget --no-cookies --header=\"Cookie: ${COOKIE}\" --keep-session-cookie"
