import os
import sys
import argparse
import random
from tqdm import tqdm
import multiprocessing
import logging

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)
# 创建一个流处理器，将日志输出到控制台
console_handler = logging.StreamHandler()
console_handler.setLevel(logging.INFO)  # 设置此处理器的日志级别
# 创建一个简单的日志格式器
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
console_handler.setFormatter(formatter)
# 将处理器添加到 logger
logger.addHandler(console_handler)
'''
根据g2p标注后的数据，为mfa对齐做数据准备
输入:
    1、包含如下格式数据的目录，改目录下不要存放其他数据
    数据格式如下（制表符作为分隔符）：
    音频绝对路径    文本
        g2p转写的拼音
        
    /mnt/cfs/SPEECH/data/tts/tal_lessons/splits/segments/3/183493/183493_466.flac	好 了 那 它 就 等 于 四 倍 的 x 一 x 二 加 上 这 俩 同 时 都 有 个 二 提 出 来 二 倍 的 x 一 加 x 二 加 上 一 个 一 那 做 到 这 儿 我 就 发 现 x 一 x 二
	cn_hao cn_le cn_na cn_ta cn_jiou cn_deng cn_v cn_sii cn_bei cn_de en_x cn_i en_x cn_er cn_jia cn_shang cn_zhe cn_lia cn_tong cn_shiii cn_dou cn_iou cn_ge cn_er cn_ti cn_chu cn_lai cn_er cn_bei cn_de en_x cn_i cn_jia en_x cn_er cn_jia cn_shang cn_i cn_ge cn_i cn_na cn_zuo cn_dao cn_zhe cn_xer cn_uo cn_jiou cn_fa cn_xian en_x cn_i en_x cn_er

    2、保存输出文件的目录
输出：
    1、目录 maps 下的文件作为mfa的数据输入  mfa align --clean --num_jobs 8 /path/to/your/directory/maps/a.list mfa_dict mfa_model output_textgrid_dir 
    2、文件 map.list 作为进程脚本mul_mfa.sh数据的输入  bash mul_mfa.sh map.list  output_textgrid_dir
    3、text 包含key和文本的文件 用于转写textgrid
    4、text.scp 包含key和文本路径的文件 用于转写textgrid
    5、wav.scp  包含key和音频路径的文件 用于转写textgrid
'''
def get_key(line):
	line = line.strip().split('/')[-1]
	key = line.split('.')[0]
	return key

def write_txt(data):
    #data.append((key, wav_path, text_scp, py))
    for item in data:
        key, wav_path, text_scp, py = item
        if os.path.exists(text_scp):
            continue
        try:
            with open(text_scp,'w',encoding='utf8') as fo:
                fo.write(py)
        except Exception as e:
            logger.error(f'rewrite failed {key} \t {text_path}: {str(e)}')

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='')
    parser.add_argument('--num_threads',type=int,default=20)
    parser.add_argument('input_dir', help='full dir path that contains txt_mfa files')
    parser.add_argument('output_dir', help='full dir path that save generation files') 
    args = parser.parse_args()
    input_dir = args.input_dir
    output_dir = args.output_dir
    MIX_UTTS = 10000
    TITLE = output_dir.strip().split('/')[-1]
    out_map_file = '{}_map_info_{:05d}.list'
    maps_dir = os.path.join(output_dir,'maps')

    text_dir = os.path.join(output_dir,'separate_texts')
    os.makedirs(text_dir, exist_ok=True)

    wav_scp = open(os.path.join(output_dir,'wav.scp'), 'w', encoding='utf8')
    text_scp = open(os.path.join(output_dir,'text.scp'), 'w', encoding='utf8')
    text = open(os.path.join(output_dir,'text'), 'w', encoding='utf8')

    keys, all_new_dir = set(), set()
    data = list()
    count = 0
    logger.info('------loading data and write files------')
    for file in os.listdir(input_dir):
        file = os.path.join(input_dir, file)
        with open(file, 'r', encoding='utf8') as fin:
            lines = fin.readlines()
            for i in tqdm(range(0, len(lines), 2)):
                wav_path, content = lines[i].strip().split('\t')
                py = lines[i+1].lstrip('\t')
                key = get_key(wav_path)
                if key in keys:
                    key = f'{count:09d}_{key}'
                    count += 1
                keys.add(key)
                relative_path = ('/').join(wav_path.split('/')[-2:-1])
                new_dir = os.path.join(text_dir, relative_path)
                all_new_dir.add(new_dir)
                text_path = os.path.join(new_dir, key + '.txt')

                wav_scp.write(f'{key}\t{wav_path}\n')
                text_scp.write(f'{key}\t{text_path}\n')
                text.write(f'{key}\t{content}\n')
                
                py = lines[i+1].lstrip('\t')
                data.append((key, wav_path, text_path, py))
    wav_scp.close()
    text_scp.close()
    text.close()
    logger.info('------renamed {} files------'.format(count))
    for dir in all_new_dir:
        os.makedirs(dir, exist_ok=True)

    logger.info('------total numbers of data {} ------'.format(len(data)))
    random.shuffle(data)

    total_iter = (len(data) // MIX_UTTS) if len(data) % MIX_UTTS == 0 else (len(data) // MIX_UTTS) + 1
    partitions = [data[i*MIX_UTTS:(i+1)*MIX_UTTS] for i in range(0, total_iter)]
    
    logger.info('------rewrite pys to single file with multiprocessing------')
    with multiprocessing.Pool(processes=args.num_threads) as pool:
        for _ in tqdm(pool.imap_unordered(write_txt, partitions), total=len(partitions)):
            pass
    
    logger.info('------write map list for mfa by multiprocessing------')
    os.makedirs(maps_dir, exist_ok=True)
    with open(os.path.join(output_dir, 'map.list'), 'w', encoding='utf8') as fo1:
        for i in range(total_iter):
            map_path = os.path.join(maps_dir, out_map_file.format(TITLE ,i))
            fo1.write(map_path+'\n')
            with open(map_path, 'w', encoding='utf8') as fo2:
                for item in partitions[i]:
                    key, wav_path, text_scp, py = item
                    fo2.write(key + '\t' + wav_path + '\t' + text_scp + '\n')