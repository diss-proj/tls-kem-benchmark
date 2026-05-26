#! /bin/bash
# based on https://github.com/open-quantum-safe/oqs-demos/blob/main/nginx/Dockerfile
rm -rf /opt/*

set -x
BASE_DIR="/opt"
INSTALL_DIR=${BASE_DIR}/nginx
OSSLDIR=${BASE_DIR}/openssl/.openssl
OPENSSL_PATH=${BASE_DIR}/openssl
HTTPD_PATH=${BASE_DIR}/httpd
PROCS=4
SIG_ALG="mldsa65"
DEFAULT_GROUPS="mlkem768"

APR_VERSION=1.7.6
APRU_VERSION=1.6.3
HTTPD_VERSION=2.4.63

NGINX_VERSION="1.28.0"
OPENSSL_TAG="openssl-3.4.0"
export CMAKE_PARAMS="-DCMAKE_PREFIX_PATH='$BASE_DIR/liboqs/build/src'"

# dependencies
sudo apt install build-base linux-headers libtool automake autoconf \
cmake ninja make git wget libpcre2-dev libexpat-dev

cd $BASE_DIR
git clone --depth 1 https://github.com/diss-proj/oqs-provider --branch diss-modifications
git clone --depth 1 https://github.com/diss-proj/liboqs --branch modifications
git clone --depth 1 --branch ${OPENSSL_TAG} https://github.com/openssl/openssl.git
wget ${APR_MIRROR}/apr/apr-${APR_VERSION}.tar.gz && tar xzvf apr-${APR_VERSION}.tar.gz
wget ${APR_MIRROR}/apr/apr-util-${APRU_VERSION}.tar.gz && tar xzvf apr-util-${APRU_VERSION}.tar.gz
wget --trust-server-names "https://archive.apache.org/dist/httpd/httpd-${HTTPD_VERSION}.tar.gz" && tar -zxvf \
httpd-${HTTPD_VERSION}.tar.gz;
tar -zxf nginx-${NGINX_VERSION}.tar.gz
rm nginx-${NGINX_VERSION}.tar.gz

#build openssl
cd $BASE_DIR/ossl-src
LDFLAGS="-Wl,-rpath -Wl,${OPENSSL_PATH}/lib64" ./config no-shared --prefix="${OPENSSL_PATH}" && \
make -j"$(nproc)" && make install_sw install_ssldirs && \
if [ -d "${OPENSSL_PATH}/lib64" ]; then ln -s "${OPENSSL_PATH}/lib64" "${OPENSSL_PATH}/lib"; fi && \
if [ -d "${OPENSSL_PATH}/lib" ]; then ln -s "${OPENSSL_PATH}/lib" "${OPENSSL_PATH}/lib64"; fi

cd $BASE_DIR/liboqs
mkdir build
cd build

# build liboqs
cmake cmake -GNinja -DOQS_ENABLE_KEM_HQC=ON -DOQS_DIST_BUILD=OFF -DOQS_OPT_TARGET=generic \
-DOQS_USE_ADX_INSTRUCTIONS=OFF \
-DOQS_USE_AES_INSTRUCTIONS=OFF \
-DOQS_USE_AVX_INSTRUCTIONS=OFF \
-DOQS_USE_AVX2_INSTRUCTIONS=OFF \
-DOQS_USE_AVX512_INSTRUCTIONS=OFF \
-DOQS_USE_BMI1_INSTRUCTIONS=OFF \
-DOQS_USE_BMI2_INSTRUCTIONS=OFF \
-DOQS_USE_PCLMULQDQ_INSTRUCTIONS=OFF \
-DOQS_USE_VPCLMULQDQ_INSTRUCTIONS=OFF \
-DOQS_USE_POPCNT_INSTRUCTIONS=OFF \
-DOQS_USE_SSE_INSTRUCTIONS=OFF \
-DOQS_USE_SSE2_INSTRUCTIONS=OFF \
-DOQS_USE_SSE3_INSTRUCTIONS=OFF \
-DOQS_USE_ARM_AES_INSTRUCTIONS=OFF \
-DOQS_USE_ARM_SHA2_INSTRUCTIONs=OFF \
-DOQS_USE_ARM_SHA3_INSTRUCTIONS=OFF \
-DOQS_USE_ARM_NEON_INSTRUCTIONS=OFF \
-DOQS_USE_OPENSSL=OFF \
..
ninja -j"${PROCS}" && ninja install

cd ${BASE_DIR}/oqs-provider

# build oqs-provider
cmake -DOPENSSL_ROOT_DIR="${OPENSSL_PATH}" -DCMAKE_PREFIX_PATH="${OPENSSL_PATH}" -S . -B build && \
cmake --build build && \
MODULESDIR="$(find "${OPENSSL_PATH}" -name ossl-modules)" && \
cp build/lib/oqsprovider.so "${MODULESDIR}/oqsprovider.so" && \
sed -i "s/default = default_sect/default = default_sect\noqsprovider = oqsprovider_sect/g" ${OPENSSL_PATH}/
ssl/openssl.cnf && \
sed -i "s/\[default_sect\]/\[default_sect\]\nactivate = 1\n\[oqsprovider_sect\]\nactivate = 1\n/g" ${OPENSSL_PATH}/ssl/openssl.cnf && \
sed -i "s/providers = provider_sect/providers = provider_sect\nssl_conf = ssl_sect\n\n\[ssl_sect\]\nsystem_default = system_default_sect\n\n\[system_default_sect\]\nGroups = \$ENV\:\:DEFAULT_GROUPS\n/g" ${OPENSSL_PATH} /ssl/openssl.cnf && \
sed -i "s/HOME\t\t\t= ./HOME\t\t= .\nDEFAULT_GROUPS\t= ${DEFAULT_GROUPS}/g" ${OPENSSL_PATH}/ssl/openssl.cnf

# build httpd
cd $BASE_DIR
sed -i "s/\$RM \"\$cfgfile\"/\$RM -f \"\$cfgfile\"/g" "apr-${APR_VERSION}/configure" && \
 ./apr-${APR_VERSION}/configure && make -j"$(nproc)" && make install


cd ${BASE_DIR}/apr-util-${APRU_VERSION}
./configure x86_64-pc-linux-gnu --with-crypto --with-openssl="${OPENSSL_PATH}" --with-apr="/usr/local/apr" && \
    make -j"$(nproc)" && make install


cd /opt/httpd-${HTTPD_VERSION}
./configure --prefix="${HTTPD_PATH}" \
                    --enable-debugger-mode \
                    --enable-ssl --with-ssl="${OPENSSL_PATH}" \
                    --enable-ssl-staticlib-deps \
                    --enable-mods-static=ssl && \
    make -j"$(nproc)" && make install;

export OPENSSL_CNF=${OPENSSL_PATH}/ssl/openssl.cnf
export OPENSSL_CONF=${OPENSSL_PATH}/ssl/openssl.cnf

cd ${HTTPD_PATH}

# generate keys
set -x && \
    mkdir pki && \
    mkdir cacert && \
    ${OPENSSL_PATH}/bin/openssl req -x509 -new -newkey ${SIG_ALG} -keyout cacert/CA.key -out cacert/CA.crt -nodes -subj "/CN=oqstest CA" -days 365 -config ${OPENSSL_CNF} && \
    ${OPENSSL_PATH}/bin/openssl req -new -newkey ${SIG_ALG} -keyout pki/server.key -out pki/server.csr -nodes -subj "/CN=oqs-httpd" -config ${OPENSSL_CNF} && \
    ${OPENSSL_PATH}/bin/openssl x509 -req -in pki/server.csr -out pki/server.crt -CA cacert/CA.crt -CAkey cacert/CA.key -CAcreateserial -days 365

# symbolic link for ossl libraries
ln -s ${OPENSSL_PATH}/lib64 ${OPENSSL_PATH}/lib

# copy HTTP config files
cp ./httpd-conf/* ${HTTPD_PATH}/httpd-conf/
