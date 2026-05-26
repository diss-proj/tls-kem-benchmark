#!/bin/bash
set -ex

ROOT="$(dirname $(pwd))"
PROJECT_ROOT=${ROOT}/../../
echo $ROOT

OPENSSL=/opt/openssl/bin/openssl
OPENSSL_CNF=/opt/openssl/ssl/openssl.cnf
OPENSSL_MODULES=/opt/openssl/lib/ossl-modules

NGINX_APP=/opt/nginx/sbin/nginx
NGINX_CONF_DIR=/opt/nginx/conf

HTTPD_APP=/opt/httpd/bin/apachectl

##########################
# Build s_timer
##########################
make s_timer.o

##########################
# Setup network namespaces
##########################
${ROOT}/setup_ns.sh

######################
# Generate MLDSA certs
######################
# MLDSA 44
#openssl req -x509 -new -newkey mldsa44 -keyout \
#${NGINX_CONF_DIR}/mldsa44.key -out ${NGINX_CONF_DIR}/mldsa44.crt -nodes -subj "/CN=oqstest" \
#-days 365 -config ${OPENSSL_CNF}
#openssl req -x509 -new -newkey mldsa44 -keyout ${NGINX_CONF_DIR}/mldsa44_CA.key -out ${NGINX_CONF_DIR}/mldsa44_CA.crt -nodes -subj "/CN=test CA" -days 365 -config ${OPENSSL_CNF}
#openssl genpkey -algorithm mldsa44 -out ${NGINX_CONF_DIR}/mldsa44_srv.key
#openssl req -new -newkey mldsa44 -keyout ${NGINX_CONF_DIR}/mldsa44_srv.key -out ${NGINX_CONF_DIR}/mldsa44_srv.csr -nodes -subj "/CN=test server" -config ${OPENSSL_CNF}
#openssl x509 -req -in ${NGINX_CONF_DIR}/mldsa44_srv.csr -out ${NGINX_CONF_DIR}/mldsa44_srv.crt -CA ${NGINX_CONF_DIR}/mldsa44_CA.crt -CAkey ${NGINX_CONF_DIR}/mldsa44_CA.key -CAcreateserial -days 365

# MLDSA 65
#openssl req -x509 -new -newkey mldsa65 -keyout \
#${NGINX_CONF_DIR}/mldsa65.key -out ${NGINX_CONF_DIR}/mldsa65.crt -nodes -subj "/CN=oqstest" \
#-days 365 -config ${OPENSSL_CNF}

# MLDSA 87
#openssl req -x509 -new -newkey mldsa87 -keyout \
#${NGINX_CONF_DIR}/mldsa87.key -out ${NGINX_CONF_DIR}/mldsa87.crt -nodes -subj "/CN=oqstest" \
#-days 365 -config ${OPENSSL_CNF}

#${OPENSSL} ecparam -out prime256v1.pem -name prime256v1


# generate CA key and cert
#${OPENSSL} req -x509 -new -newkey ec:prime256v1.pem -keyout ${NGINX_CONF_DIR}/CA.key -out ${NGINX_CONF_DIR}/CA.crt -nodes -subj "/CN=OQS test ecdsap256 CA" -days 365 -config ${OPENSSL_CNF}

# generate server CSR
#${OPENSSL} req -new -newkey ec:prime256v1.pem -keyout ${NGINX_CONF_DIR}/server.key -out ${NGINX_CONF_DIR}/server.csr -nodes -subj "/CN=oqstest CA ecdsap256" -config ${OPENSSL_CNF}

# generate server cert
#${OPENSSL} x509 -req -in ${NGINX_CONF_DIR}/server.csr -out ${NGINX_CONF_DIR}/server.crt -CA ${NGINX_CONF_DIR}/CA.crt -CAkey ${NGINX_CONF_DIR}/CA.key -CAcreateserial -days 365

##########################
# Start nginx
##########################
#cp nginx.conf ${NGINX_CONF_DIR}/nginx.conf
# export OPENSSL_MODULES=/lib; \
ip netns exec srv_ns bash -c "export OPENSSL_CONF=/opt/openssl/ssl/openssl.cnf; \
${HTTPD_APP};"
