#!/bin/bash
cat /mnt/cfs/SPEECH/hupeng/tools/others_env/hp_env.sh > ~/.bashrc
source ~/.bashrc
conda activate mfa_tal
cp -r /mnt/cfs/nltk_data ~/
# 或换成从git拉取到本地的项目目录
cd /mnt/cfs/SPEECH/hupeng/git_loc_workspace/tal_align/utils

if_tar='0' # 结果是否打包成tar
tmp_dir=/mnt/to/your/tmp/dir # 保存中间结果的目录，绝对路径
mfa_model=/mnt/cfs/SPEECH/hupeng/git_loc_workspace/tal_align/models/cn_en_align_2k_10_model_3 # 对齐模型 绝对路径
data_json=/mnt/cfs/data.json # 需要对齐的数据

bash run.sh "$data_json" "$tmp_dir" -if_tar 0 -g2p_model pypinyin -lang mix -mfa_model "$mfa_model"