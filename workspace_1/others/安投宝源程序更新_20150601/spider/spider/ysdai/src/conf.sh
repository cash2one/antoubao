HOST="http://www.ysdai.cc"
INDEXPAGE="${HOST}/invest.aspx?borrow_status=2"
POSTDATA_INDEX="ctl00$ContentPlaceHolder1$gridView$ctl11$txtNewPageIndex:\${i}"
DETAILPAGE="${HOST}/invest_detail.aspx?id="
#COOKIE=`cat COOKIE`
#GETPAGE="wget --no-cookies --header=\"Cookie: ${COOKIE}\" --keep-session-cookie"
GETPAGE="wget"
