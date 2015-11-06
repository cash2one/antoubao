CC=g++
INCLUDES=-I../../common/json/include -I../../common/spi_utils -I../../common/utils
CFLAGS=-O2

parse:
	mkdir -p prod/
	$(CC) -o prod/parse \
		src/parse.cpp ../../common/spi_utils/spi_utils.cpp ../../common/utils/utils.cpp \
		../../common/json/src/json_writer.cpp ../../common/json/src/json_reader.cpp ../../common/json/src/json_value.cpp \
		$(LIBS) $(INCLUDES) $(CFLAGS)
	cp src/conf.sh prod/
	cp src/getindex.sh prod/
	cp src/getpage.sh prod/
	cp src/apage.sh prod/
	cp src/spider_main.sh prod/
	cp src/README prod/
.PHONY: parse

clean:
	rm -rf prod/
.PHONY: clean

