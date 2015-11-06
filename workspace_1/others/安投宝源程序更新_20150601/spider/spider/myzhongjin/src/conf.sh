HOST="http://mobile.myzhongjin.com"
INDEXPAGE="${HOST}/Loan/AjaxPageOfLoan?PageSize=20"
DETAILPAGE="${HOST}/Loan/Details/"
COOKIE=`cat COOKIE`
GETPAGE="wget --no-cookies --header=\"Cookie: ${COOKIE}\" --keep-session-cookie"
