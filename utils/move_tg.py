import os
import sys
import json
import shutil

if __name__ == '__main__':
    data_list = sys.argv[1]
    dir = sys.argv[2]

    move_info = dict()
    with open(data_list, 'r', encoding='utf8') as fin:
        for line in fin:
            data = json.loads(line)
            key, tg = data['key'], data['textgrid']
            target_tg = '/'.join(tg.split('/')[:-1])
            move_info[key] = target_tg

    for file in os.listdir(dir):
        ori_path = move_info[file.replace('.TextGrid','')]
        file = os.path.join(dir, file)
        print(file, ori_path)

        shutil.move(file, ori_path)