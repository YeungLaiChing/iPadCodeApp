#!/bin/sh
BASEDIR="$( cd "$( dirname "$0" )" && pwd )"
mkdir "${BASEDIR}"/data/ "${BASEDIR}"/redis-cache/ "${BASEDIR}"/dynamodb-data/ 2>/dev/null >/dev/null
cd "${BASEDIR}"

docker build -t vaindex-base:latest .
