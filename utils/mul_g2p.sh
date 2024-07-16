#!/bin/bash

## map & dir
map_path=$1 #需要标注syllable的文本文件
datainfo_dir=$2 #保存中间文件的目录
g2p_model='pypinyin'
lang='mix'
if [ -n "$3" ]; then
    g2p_model=$3
fi
num_parts=1 #默认多进程数量

#conda环境 根据需求自行替换
source /mnt/cfs/SPEECH/hupeng/tools/others_env/hp_env.sh
conda activate py310

cd $datainfo_dir
pydir="${datainfo_dir}/split_pys"

# 检查并创建目录
if [ ! -d "$pydir" ]; then
    mkdir -p "$pydir"
    echo "Directory $pydir created."
fi

# 检查文件是否存在
if [ ! -f "$map_path" ]; then
    echo "Error: File '$map_path' not found!"
    exit 1
fi

# 计算每个部分应该包含的行数
total_lines=$(wc -l < "$map_path")
lines_per_part=$((total_lines / num_parts))
[ $((total_lines % num_parts)) -ne 0 ] && ((lines_per_part++)) # 
shuffled_file="${datainfo_dir}/shuffled_"
shuf "$map_path" > "$shuffled_file"

# 分割文件
split -l "$lines_per_part" "$shuffled_file" part_text_

# 清理临时打乱的文件
rm "$shuffled_file"

echo "g2p task begin ......"

for part_file in part_text_*; do  
    #python /mnt/cfs/SPEECH/hupeng/git_loc_workspace/tal_frontend/g2p_hwl.py $part_file --g2p_model $g2p_model --lang $lang &
    python /mnt/cfs/SPEECH/hupeng/git_loc_workspace/tal_frontend/g2p_mfa.py $part_file &
done

# 等待所有后台进程完成
wait
echo "g2p task End ......"
mv *_en_oov.dict $pydir
mv *_syllable $pydir
rm part_text_*
cd -
conda deactivate
