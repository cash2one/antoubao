HOST='http://www.xuridai.com'
INDEXPAGE1="${HOST}/investment.aspx?aid=1"
INDEXPAGE9="${HOST}/investment.aspx?aid=9"
DETAILPAGE="${HOST}/investment-details"
GETPAGE="wget --no-cookies --header=\"Cookie: `cat COOKIE`;\" --keep-session-cookie"
POSTDATA="__VIEWSTATE=`cat VIEWSTATE`&__VIEWSTATEGENERATOR=AB9D14B6&__EVENTTARGET=PageManage&DropBorrowerPurpose1=0&cityname=&cityid=&DropProvince=0&DropCity=0&DropBorrowerPurpose11=0&DropBorrowerPurpose9=0&PageManage_input=1&__EVENTARGUMENT="

