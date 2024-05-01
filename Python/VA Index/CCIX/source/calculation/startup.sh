#!/bin/sh
BASEDIR="$( cd "$( dirname "$0" )" && pwd )"
mkdir "${BASEDIR}"/data/ "${BASEDIR}"/log/ 2>/dev/null >/dev/null
cd "${BASEDIR}"

python3 btc_index_tick.py >> ./log/calc_btc.log 2>> ./log/calc_btc.err &