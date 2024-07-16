import os
import sys
import json
import shutil

tgs = sys.argv[1]
data_info = sys.argv[2]
save_dir = sys.argv[3]

table = {}
with open(tgs ,'r', encoding='utf8') as fin:
    for line in fin:
        key = line.strip().split('/')[-1]
        key = key.split('.')[0]
        table[key] = line.strip()

with open(data_info ,'r', encoding='utf8') as fin:
    for line in fin:
        line = json.loads(line)
        key = line['key']
        if table.get(key):
            shutil.copy(line['wav'], save_dir)
            shutil.copy(table[key], save_dir)

#{"key": "1071_8_179648_343", "wav": "/mnt/cfs/SPEECH/data/tts/tal_lessons/spk_select_400/audio_v2/1071/1071_8_179648_343.flac", "txt": "去 忘 记 不 能 去 不 记 得 去 写 这 个 反 面 的 东 西 ok", "textgrid": "/mnt/cfs/SPEECH/data/tts/tal_lessons/spk_select_400/tg_from_new_mfamodel/1071_8_179648_343.TextGrid"}
