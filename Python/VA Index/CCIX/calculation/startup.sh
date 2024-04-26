#!/bin/sh
BASEDIR="$( cd "$( dirname "$0" )" && pwd )"
mkdir "${BASEDIR}"/data/ "${BASEDIR}"/log/ 2>/dev/null >/dev/null
cd "${BASEDIR}"

