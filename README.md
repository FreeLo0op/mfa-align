# Montreal Forced Aligner
Using the MFA for Chinese-English alignment tasks, the model is trained on a dataset comprising 2000 hours of data, with approximately 300 hours of English data and about 1700 hours of Chinese data. The frame shift for MFCC feature extraction has been modified to 20.

## 1、脚本中需要替换的部分
1.mul_g2p.sh
    脚本中g2p使用的conda环境可换成自己的创建的conda环境或者继续沿用脚本中默认指定的环境  

    脚本中g2p_hwl.py脚本的路径替换成从git上的tal_frontend项目，clone到自己的服务器下绝对路径，或者继续沿用脚本中默认指定的脚本  

## 2、Start
```bash
git clone https://git.100tal.com/xpad_audio/tal_align.git
```
## 3、Installation
    Install mfa by following steps
```bash
cd tal_align
conda env create -n mfa_tal -f environment.yml
conda activate mfa_tal
pip install -e .[dev]
```

## 4、对齐数据准备
### 音频
文本文件 两列 第一列为key 第二列为音频绝对路径 分隔符：制表符或空格  
### 文本
文本文件 两列 第一列为key 第二列为文本 分隔符：制表符或空格  
### 数据准备脚本
准备好的数据作为后续对齐run.sh脚本的第一个参数  
```py
cd tal_align/utils
python datafile_pre.py text.map wav.map save_dir  

##输出：在save_dir目录下生成 data.json 的文件作为对齐脚本的输入。同时对齐的结果也会保存在改目录下的 tri_tgs 目录中。 save_dir输入为绝对路径
```

## 5、Run Demo
```bash
cd tal_align/utils
bash run.sh ../run_test/data/data.json /path/to/your/direction/tal_align/run_test/tmp
```
or
```bash
bash run.sh ../run_test/data/data.json /path/to/your/direction/tal_align/run_test/tmp -if_tar 1 -g2p_model pypinyin -lang mix -mfa_model ../models/cn_en_align_2k_10_model
```
    run.sh 输入参数解释  
        $1 是需要准备对齐的数据格式参照该文档，详细字段解释参考知音文档或第4步  
        https://yach-doc-shimo.zhiyinlou.com/docs/e1Az4MQag2sedJqW/ <Align任务说明文档>  
        $2 是保存中间文件的目录，输入绝对路径  
        -if_tar 最终结果是否需要打包成tar，如果需要输入1 不需要输入0，默认不生成tar  
        -g2p_model g2p模型参数,可选参数：  
            pypinyin ：使用pypinyin生成拼音 效率：3.6mins/10w  
            g2pW_gpu ：以gpu方式运行g2pW模型生成拼音 效率：12mins/10w  
            g2pW_cpu ：以cpu方式运行g2pW模型生成拼音 效率：60mins/10w  
            默认参数:g2pW_cpu  
        -lang 指定文本语言类型，如果能确定文本为纯英文或者纯中文可避免g2p误判文本类型  
        -mfa_model 对齐模  
            cn_en_align_2k_10_model 10帧帧移中英混模型  
            cn_en_align_2k_20_model 20帧帧移中英混模型 新版本，增加xpad2数据训练  

    输出：  
        1、textgrid会保存在data.json文件里指定的save字段路径下
        2、data.list和tar都会保存在 参数$2 下
	注：若没有提前激活mfa_tal环境要么每次任务前手动激活，要么在mul_mfa.sh脚本最前面重新source一下自己的环境激活mfa_tal

## 训练任务允许
将utils/run_platform.sh内的命令复制到训练平台的shell命令中即可  
注意修改参数

## g2p
见[git tal_frontend](https://git.100tal.com/xpad_audio/tal_frontend)