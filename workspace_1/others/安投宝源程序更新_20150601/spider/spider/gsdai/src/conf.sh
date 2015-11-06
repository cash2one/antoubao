HOST='http://www.gsdai.com/'
INDEXPAGE="${HOST}/borrow/blist.html?sftype=0&saccount=0&sapr=0&slimit=0&per_page="
DETAILPAGE="${HOST}/borrow/obj"
PHPSESSID=`cat PHPSESSID`
GETPAGE="wget --no-cookies --header=\"Cookie: PHPSESSID=${PHPSESSID}; IESESSION=alive;\" --keep-session-cookie --no-check-certificate"

