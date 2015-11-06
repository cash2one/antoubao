HOST="https://www.kexindai.com"
INDEXPAGE="${HOST}/Function/AjaxFunc.ashx?act=getloanlistbypage&pagesize=8&page="
DETAILPAGE="${HOST}/loan-"
COOKIE=`cat COOKIE`  
GETPAGE="wget --no-cookies --header=\"Cookie: ${COOKIE}\" --keep-session-cookie"
