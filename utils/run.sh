#!/bin/bash -i

# 从0开始准备mfa数据
# 每次任务都为需要对齐的数据集创建一个新的 空目录(datainfo_dir) 并将其 “绝对路径” 作为脚本输入$2

# 检查是否至少有两个参数
if [ $# -lt 2 ]; then
  echo "使用方法: $0 data_json datainfo_dir [选项]"
  exit 1
fi
# 处理必须的参数
data_json=$1
datainfo_dir=$2
# 移除已处理的参数
shift 2

# 初始化可选变量
if_tar='0'
g2p_model='pypinyin'
lang='mix'
mfa_model='../models/cn_en_align_2k_20_model'

# 解析剩余的命令行参数
while [[ $# -gt 0 ]]; do
    case $1 in
        -mfa_model)
        mfa_model="$2"
        shift
        shift
        ;;
        -if_tar)
        if_tar="$2"
        shift # 移除 '-if_tar'
        shift # 移除对应的值
        ;;
        -g2p_model)
        g2p_model="$2"
        shift # 移除 '-g2p_model'
        shift # 移除对应的值
        ;;
        -lang)
        lang="$2"
        shift # 移除 '-lang'
        shift # 移除对应的值
        ;;
        *)    # 未知选项
        echo "未知选项: $1"
        exit 1
        ;;
    esac
done

# 若缓存目录存在且非空则清空，否则创建一个新的目录
if [[ -d $datainfo_dir ]]; then
    rm -rf "$datainfo_dir"/*
else
    mkdir -p "$datainfo_dir"
fi


# 输出对齐信息
echo "对齐数据：$data_json， 语种：$lang， 保存路径：$datainfo_dir， g2p模型：$g2p_model， mfa模型：$mfa_model， 结果是否打包成tar：$if_tar"

text="${datainfo_dir}/text"
pydir="${datainfo_dir}/split_pys"
mkdir -p $pydir

python align_data_check.py $data_json $datainfo_dir

# text文件存在且大小不为0 走g2p
if [ -f $text ] && [ -s $text ]; then
    bash mul_g2p.sh $text $datainfo_dir $g2p_model
fi

python g2p_py_rewrite.py $datainfo_dir

bash mul_mfa.sh $datainfo_dir $mfa_model

python textgrid_rewrite.py $datainfo_dir

python mfa_tar_tool.py "${datainfo_dir}" $if_tar
