#while true
#do
    rm log.csv
    python main.py
    cat log.csv > prev_log.csv
    sleep 10
#done
