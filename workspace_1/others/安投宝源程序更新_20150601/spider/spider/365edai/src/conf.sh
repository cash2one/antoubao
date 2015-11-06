HOST="http://www.365edai.cn"
INDEXPAGE="${HOST}/Lend/Cloanlist.aspx?page="
DETAILPAGE="${HOST}/Lend/LoanInfo.aspx?id="
COOKIE=`cat COOKIE`
GETPAGE="wget --no-cookies --header=\"Cookie: ${COOKIE}\" --keep-session-cookie"
