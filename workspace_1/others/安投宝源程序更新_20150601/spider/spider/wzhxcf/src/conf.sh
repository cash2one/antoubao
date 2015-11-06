HOST="http://www.wzhxcf.com"
INDEXPAGE="${HOST}/invest.aspx?page="
DETAILPAGE="${HOST}/jkxq.aspx?id="
DETAILPAGE1="${HOST}/biaojs.aspx?id=\${ID}&act=tbjl"
COOKIE=`cat COOKIE`
GETPAGE="wget --no-cookies --header=\"Cookie: ${COOKIE}\" --keep-session-cookie"
