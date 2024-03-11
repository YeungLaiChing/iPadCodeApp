cd /home/tester/workspace/iPadCodeApp/Python/MV/

nohup python3 mv_calc.py >> ./log/calculation.log 2>> ./log/calculation.err.log &

sleep 3

nohup python3 mv_calc_fix_int.py >> ./log/calcfix.log 2>> calcfix.err.log &

sleep 3

nohup python3 mv_capture.py >> ./log/capture.log 2>> ./log/capture.err.log &

sleep 3

nohup python3 mv_trigger.py >> ./log/trigger.log 2>> ./log/trigger.err.log &


