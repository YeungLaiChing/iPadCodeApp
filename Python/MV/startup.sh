cd /home/tester/workspace/iPadCodeApp/Python/MV/

nohup python3 mv_calc.py >> ./log/calculation.log 2>> ./log/calculation.err.log &

sleep 3

nohup python3 mv_capture.py >> ./log/capture.log 2>> ./log/capture.err.log &

