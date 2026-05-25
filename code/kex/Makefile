ROOT=$(shell dirname $(shell pwd))/../..
OPENSSL_DIR=$(ROOT)/_build/oqs-provider/openssl

OPENSSL_INCLUDE=$(OPENSSL_DIR)/include
OPENSSL=$(OPENSSL_DIR)/apps/openssl

#OQS_INCLUDE=$(OPENSSL_DIR)/oqs/include
#OQS_LIB=$(OPENSSL_DIR)/oqs/lib

s_timer.o: s_timer.c
	$(CC) -g -Wall -Wextra -Werror -Wpedantic -I$(OPENSSL_INCLUDE)  $< -L$(OPENSSL_DIR)  -lssl -lcrypto -ldl -lpthread  -o $@
