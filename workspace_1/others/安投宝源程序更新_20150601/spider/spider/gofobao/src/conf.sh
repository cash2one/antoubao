HOST='http://www.gofobao.com'
INDEXPAGE="${HOST}/index.php?user&q=code/borrow/show_bid_list&keywords=&type=tender&page="
DETAILPAGE="${HOST}/invest/a"
INVESTORPAGE="${HOST}/index.php?user&q=code/borrow/get_tenderlist&limit=all&rnd=0.5771025426220149&borrow_id="
COOKIE=`cat COOKIE`
GETPAGE="wget --header=\"Cookie: ${COOKIE}\""
