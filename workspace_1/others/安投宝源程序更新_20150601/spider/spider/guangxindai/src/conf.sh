HOST='https://www.guangxindai.com'
INDEXPAGE="${HOST}/ajax/borrowes/invest/0.21351276501081884?borrowType=5&useType=999&repaymentType=999&timeType=999&awardType=999&cityType=999&pageCount=10&pageIndex="
INDEXPAGE1="${HOST}/ajax/borrowes/invest/0.46258395118638873?borrowType=1&useType=999&repaymentType=999&timeType=999&awardType=999&cityType=999&pageCount=10&pageIndex="
DETAILPAGE="${HOST}/borrows/index/"
#INVESTORPAGE="${HOST}/invest/getrecord/id/"
COOKIE=`cat COOKIE`
GETPAGE="wget --header=\"Cookie: ${COOKIE}\""
