import os
import sys
import json
from random import shuffle

if __name__ == '__main__':
    text_file = sys.argv[1]
    wav_file = sys.argv[2]
    save_dir  = sys.argv[3]

    save_file = r'{}/data.json'.format(save_dir)
    total_num = 1
    keys = set()
    wav_dic, txt_dic = dict(), dict()

    with open(text_file, 'r', encoding='utf8') as fin:
        for line in fin:
            line = line.strip()
            key, content = None, None
            for sep in ['\t', ' ']:
                if sep in line:
                    key, content = line.split(sep, maxsplit=1)
                    break
            if key is not None and content is not None:
                txt_dic[key] = content
        
    with open(wav_file, 'r', encoding='utf8') as fin:
        for line in fin:
            line = line.strip()
            for sep in ['\t', ' ']:
                if sep in line:
                    key, content = line.split(sep, maxsplit=1)
                    break
            if key is not None and content is not None:
                wav_dic[key] = content

    keys = list(txt_dic.keys())
    shuffle(keys)

    #for i in range(1, total_num+1):
    with open(save_file, 'w', encoding='utf8') as fo:
        json_data = []
        for key in keys:
            try:
                wav = wav_dic[key]
                txt = txt_dic[key]
                syllable = ''
                save = r'{}/tri_tgs'.format(save_dir)
                data_dict = {
                    "key": key,
                    "wav": wav,
                    "txt": txt,
                    "syllable": syllable,
                    "save": save
                }
                tmp = json.dumps(data_dict, ensure_ascii=False)
                json_data.append(str(tmp))
            except:
                continue
        fo.write('\n'.join(json_data))