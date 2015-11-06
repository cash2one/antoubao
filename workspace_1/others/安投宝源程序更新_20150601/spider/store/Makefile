CC=g++
INCLUDES=-I../common/json/include -I../common/utils -I../common/spi_utils
LIBS=-lmysqlclient
CFLAGS=-O2 -Wno-unused-result

store:
	mkdir -p prod
	$(CC) -o prod/spi_store \
		src/store.cpp ../common/spi_utils/spi_utils.cpp ../common/utils/utils.cpp  \
		../common/json/src/json_writer.cpp ../common/json/src/json_reader.cpp ../common/json/src/json_value.cpp \
		$(LIBS) $(INCLUDES) $(CFLAGS)
.PHONY: store

clean:
	rm -rf prod
.PHONY: clean

