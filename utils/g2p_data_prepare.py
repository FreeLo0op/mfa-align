import os
import re
import sys

def get_key(line: str):
	line = line.strip().split('/')[-1]
	key = line.split('.')[0]
	return key

def check_split_type(line: str):
    if len(line.strip().split(' ')) == 2:
        return ' '
    elif len(line.strip().split('\t')) == 2:
        return '\t'

if __name__ == '__main__':
    text_path = sys.argv[1] #原始包含所有 文本及其key 的text文件的绝对路径
    wav_path = sys.argv[2] #原始包含所有音频 key和绝对路径 的文件的绝对路径
    output_dir = sys.argv[3] #保存数据输出的目录
    
    wav_fo = open(os.path.join(output_dir,'wav.scp'), 'w', encoding='utf8')
    text_fo = open(os.path.join(output_dir, 'text'), 'w', encoding='utf8')
    data = list()
    text_dict, wav_dict = dict(), dict()
    
    with open(text_path, 'r', encoding='utf8') as fin:
        lines = fin.readlines()
        split_type = check_split_type(lines[0])
        for line in lines:
            if split_type == ' ':
               line = line.strip().split(split_type)
               key = line[0]
               content = ' '.join(line[1:])
            else:
                key, content = line.strip().split(split_type)
            if not text_dict.get(key):
                text_dict[key] = content
            else:
                print('text file duplicate key : {}'.format(key))
                print('text 1 : {}'.format(text_dict[key]))
                print('text 2 : {}'.format(content))
                sys.exit(1)
            contents = re.findall(r'[\u4e00-\u9fa5]|[a-zA-Z]+\'?[a-zA-Z]*', content)
            content = ' '.join(contents)
            
            text_fo.write(f'{key}\t{content.lower()}\n')
    text_fo.close()
    
    with open(wav_path, 'r', encoding='utf8') as fin:
        lines = fin.readlines()
        split_type = check_split_type(lines[0])
        for line in lines:
            key, path = line.strip().split(split_type)
            if not wav_dict.get(key):
                wav_dict[key] = path
            else:
                print('wav file duplicate key : {}'.format(key))
                sys.exit(1)
            wav_fo.write(f'{key}\t{path}\n')
    wav_fo.close()