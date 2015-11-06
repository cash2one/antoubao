HOST="http://www.yueyuedai.com"
INDEXPAGE="${HOST}/Investment/List.aspx?page="
DETAILPAGE="${HOST}/Investment/Record.aspx?Item="
#JSESSIONID=`cat JSESSIONID`
#GETPAGE="wget --no-cookies --header=\"Cookie: JSESSIONID=${JSESSIONID}; IESESSION=alive;\" --keep-session-cookie"
COOKIE=`cat COOKIE`
GETPAGE="wget --no-cookies --header=\"Cookie: ${COOKIE}\" --keep-session-cookie"
