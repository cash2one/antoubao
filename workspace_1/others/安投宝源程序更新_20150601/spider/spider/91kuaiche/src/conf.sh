HOST_INDEX="http://inv.91kuaiche.com"
HOST_DETAIL="http://w8.91kuaiche.com"
LOANTYPE=("winning" "popcorn")
INDEXPAGE="${HOST_INDEX}/\${LOANTYPE[\${t}]}/"
DETAILPAGE1="${HOST_DETAIL}/"
DETAILPAGE2="${HOST_DETAIL}/indexinvest.php"
POSTDATA2="projectcode=\${BID}&startnum=\${startnum}" 
COOKIE=`cat COOKIE`
#GETPAGE="wget --no-cookies --header=\"Cookie: ${COOKIE}\" --header=\"User-Agent:Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/39.0.2171.95 Safari/537.36\" --keep-session-cookie"
GETPAGE="wget --no-cookies --header=\"Cookie: ${COOKIE}\"  --keep-session-cookie"
