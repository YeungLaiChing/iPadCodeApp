#!/bin/sh
BASEDIR="$( cd "$( dirname "$0" )" && pwd )"
mkdir "${BASEDIR}"/data/ "${BASEDIR}"/log/ 2>/dev/null >/dev/null
cd "${BASEDIR}"

python3 bitstamp.py >> ./log/bitstamp.log 2>> ./log/bitstamp.err &
python3 coinbase.py >> ./log/coinbase.log 2>> ./log/coinbase.err &
python3 itbit.py >> ./log/itbit.log 2>> ./log/itbit.err &
python3 kraken.py >> ./log/kraken.log 2>> ./log/kraken.err &
python3 lmax.py >> ./log/lmax.log 2>> ./log/lmax.err &

python3 consol.py bitstamp >> ./log/consol.bitstamp.log 2>> ./log/consol.bitstamp.err &
python3 consol.py coinbase >> ./log/consol.coinbase.log 2>> ./log/consol.coinbase.err &
python3 consol.py itbit >> ./log/consol.itbit.log 2>> ./log/consol.itbit.err &
python3 consol.py kraken >> ./log/consol.kraken.log 2>> ./log/consol.kraken.err &
python3 consol.py lmax >> ./log/consol.lmax.log 2>> ./log/consol.lmax.err &

python3 dump_topic.py duplicated_data_channel >> ./log/Z.duplicate.log 2>> ./log/Z.duplicate.err &
