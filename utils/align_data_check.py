import os
import re
import sys
import json
import shutil
from tqdm import tqdm
from collections import defaultdict
from logger import logger

'''
检查输入数据并转化成后续任务需要的格式，因为目前g2p还没有定版，所以不读取syllable字段。
'''

def data_load(json_flie, info_file, py_file, text_file):
    count = 0
    key_set = set()
    with open(json_flie, 'r', encoding='utf8') as fin:
        for line in fin:
            try:
                data = json.loads(line)
                name, wav, txt, syllable, save = data['key'], data['wav'], data['txt'], data['syllable'], data['save']
            except json.JSONDecodeError:
                logger.error(f'Error: JSON 解析错误 {line.strip()}')
            
            # 检测是否有空文本
            if txt == '':
                logger.info(f'{name} : null text')
                continue
            
            # 检查name是否重复，如果重复则通过加填充9位数前缀的方式重命名
            if name not in key_set:
                key_set.add(name)
                key = name
            else:
                key = f'{count:09d}_{name}'
                logger.info(f'duplicate key : {name}, rename it to {key}')

            info_file.write(f'{key}\t{name}\t{wav}\t{txt}\t{save}\n')
            if not syllable:
                text_file.write(f'{key}\t{txt}\n')
            else:
                py_file.write(f'{key}\t{txt}\n\t{syllable}\n')

if __name__ == '__main__':
    input_file = sys.argv[1] #需要对齐的数据的json格式文件
    datainfo_dir = sys.argv[2] #保存中间文件的目录

    info_file = open(os.path.join(datainfo_dir, 'info.list'), 'w', encoding='utf8')
    py_file = open(os.path.join(datainfo_dir,'split_pys','syllable_from_json'), 'w', encoding='utf8')
    text_file = open(os.path.join(datainfo_dir, 'text'), 'w', encoding='utf8')

    data_load(input_file, info_file, py_file, text_file)

    info_file.close()
    py_file.close()
    text_file.close()
    

