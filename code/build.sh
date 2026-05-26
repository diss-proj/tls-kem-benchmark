#! /bin/bash
# based on https://github.com/open-quantum-safe/oqs-demos/blob/main/nginx/Dockerfile
rm -rf /opt/*

set -x
BASE_DIR="/opt"
INSTALL_DIR=${BASE_DIR}/nginx
OSSLDIR=${BASE_DIR}/openssl/.openssl
PROCS=4
SIG_ALG="mldsa44"

NGINX_VERSION="1.28.0"
OPENSSL_TAG="openssl-3.4.0"
export CMAKE_PARAMS="-DCMAKE_PREFIX_PATH='$BASE_DIR/liboqs/build/src'"

cd $BASE_DIR
git clone --depth 1 https://github.com/diss-proj/oqs-provider --branch diss-modifications
git clone --depth 1 https://github.com/diss-proj/liboqs --branch modifications
git clone --depth 1 --branch ${OPENSSL_TAG} https://github.com/openssl/openssl.git
wget -q nginx.org/download/nginx-${NGINX_VERSION}.tar.gz
tar -zxf nginx-${NGINX_VERSION}.tar.gz
rm nginx-${NGINX_VERSION}.tar.gz

cd $BASE_DIR/liboqs
mkdir build
cd build

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

export CMAKE_PREFIX_PATH="${BASE_DIR}/liboqs/build/src"
cd $BASE_DIR/nginx-${NGINX_VERSION}
./configure --prefix=${INSTALL_DIR} \
--with-debug --with-http_ssl_module \
--with-openssl=/opt/openssl --without-http_gzip_module && \
make -j"${PROCS}"&& make install

mkdir -p ${OSSLDIR=}/ssl && \
cp /opt/openssl/apps/openssl.cnf ${OSSLDIR}/ssl/ && \
sed -i "s/default = default_sect/default = default_sect\noqsprovider = oqsprovider_sect/g" ${OSSLDIR}/ssl/openssl.cnf && \
sed -i "s/\[default_sect\]/\[default_sect\]\nactivate = 1\n\[oqsprovider_sect\]\nactivate = 1\n/g" ${OSSLDIR}/ssl/openssl.cnf && \
sed -i "s/providers = provider_sect/providers = provider_sect\nssl_conf = ssl_sect\n\n\[ssl_sect\]\nsystem_default = system_default_sect\n\n\[system_default_sect\]\nGroups = \$ENV\:\:DEFAULT_GROUPS\n/g" ${OSSLDIR}/ssl/openssl.cnf && \
sed -i "s/HOME\t\t\t= ./HOME\t\t= .\nDEFAULT_GROUPS\t= ${DEFAULT_GROUPS}/g" ${OSSLDIR}/ssl/openssl.cnf

cd $BASE_DIR/oqs-provider
ln -s "${BASE_DIR}/nginx/include/oqs" "${OSSLDIR}/include" && \
rm -rf build && \
cmake -DCMAKE_BUILD_TYPE=Debug \
-DOPENSSL_ROOT_DIR="${OSSLDIR}" \
-DCMAKE_PREFIX_PATH="${INSTALLDIR}" \
-S . -B build && \
cmake --build build && \
MODULESDIR=$(find "${OSSLDIR}" -name ossl-modules) && \
export MODULESDIR && \
cp build/lib/oqsprovider.so "${MODULESDIR}" && \
mkdir -p "${OSSLDIR}/lib64" && \
ln -s "${OSSLDIR}/lib/ossl-modules" "${OSSLDIR}/lib64" && \
rm -rf "${INSTALL_DIR:?}/lib64"

cd ${INSTALL_DIR}
mkdir -p cacert pki
${BASE_DIR}/openssl/apps/openssl req -x509 -new -newkey "${SIG_ALG}" -keyout CA.key -out cacert/CA.crt -nodes -subj "/CN=oqstest CA" -days 365 -config "${OSSLDIR}/ssl/openssl.cnf"
${BASE_DIR}/openssl/apps/openssl req -new -newkey "${SIG_ALG}" -keyout pki/server.key -out server.csr -nodes -subj "/CN=oqs-nginx" -config "${OSSLDIR}/ssl/openssl.cnf"
${BASE_DIR}/openssl/apps/openssl x509 -req -in server.csr -out pki/server.crt -CA cacert/CA.crt -CAkey CA.key -CAcreateserial -days 365 && \
rm -f "${OSSLDIR}/bin/"*

