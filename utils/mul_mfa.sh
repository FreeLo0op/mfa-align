#!/bin/bash

# 多线程脚本运行mfa
input=$1  #map.list
# 默认对齐模型 
# 20帧帧移
#mfa_model='../models/cn_en_align_2k_20_model'
# 10帧帧移
mfa_model='../models/cn_en_align_2k_10_model'
if [ -n "$2" ]; then
    mfa_model=$2
fi

SEND_THREAD_NUM=4
start_time=$(date +%s)
tmp_fifofile="/tmp/$$.fifo"
mkfifo "$tmp_fifofile"
exec 6<>"$tmp_fifofile"

for ((i=0;i<$SEND_THREAD_NUM;i++))
do
    echo
done >&6

while read -r line;
do
    read -u6
    {
        echo "Start align $line"
        #模型字典和模型的路径根据自己保存的目录做修改
        mfa align --num_jobs 8 --clean $line "${input}/mfa.dict" $mfa_model "${input}/tg_res"
        echo >&6
    }&
done < "${input}/map.list"

wait
exec 6>&- 
rm "$tmp_fifofile"

end_time=$(date +%s) 
duration=$((end_time - start_time)) # 计算持续时间
echo "MFA Duration: $duration s."

exit 0