HOST='http://www.xueshandai.com'
INDEXPAGE="${HOST}/invest/list?max=5&offset="
INVESTORPAGE='${HOST}/invest/invest-record/${ID}?_=$((`date +%s%N`/1000000))&max=1000'
DETAILPAGE="${HOST}/invest/view/"
HTMLDIR='html'
DATADIR='data'
GETPAGE="wget"

