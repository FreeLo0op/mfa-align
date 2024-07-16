import os
import re
import sys
import random
import argparse
from tqdm import tqdm
import multiprocessing
from collections import defaultdict
from textgrid import TextGrid, IntervalTier
from logger import logger

SM = set(
    ['m','b','g','q','ch','z','l','sh','h','n','s','x','d','c','f','zh','k','r','t','p','j']
    )


def rewrite_textgrid(data):
    for item in data:
        key, contents, pys, ori_tg_path, new_tg_path = item
        try:
            no_write = False
            if os.path.exists(new_tg_path):
                continue
            ori_tg = TextGrid.fromFile(ori_tg_path)
            infos = [[],[],[]]
            tones = []
            count = 0
            for interval in ori_tg.tiers[0]:
                min_t, max_t, text = interval.minTime, interval.maxTime, interval.mark
                #去掉音节里面的伪声母 ‘y’
                #text = re.sub(r'cn_y', 'cn_', text)
                #添加声调  
                if text != '' and re.sub(r'\d+', '', pys[count]) == text:
                    py = pys[count].replace('6','2')
                    infos[0].append((py ,min_t, max_t))
                    infos[2].append((contents[count],min_t,max_t))
                    if 'cn_' in py:
                        tone = py[-1]
                        if tone not in ['1','2','3','4','5']:
                            print(f'{key} tone >= 6')
                            no_write = True
                        tones.append(tone)
                    count += 1
                else:
                    infos[0].append((text,min_t,max_t))
                    infos[2].append((text,min_t,max_t))
            i, count = 0, 0
            #if len(tones) == 0:
            #    tones = ['None' for _ in range(len(contents))]

            while i < len(ori_tg.tiers[1]):
                interval = ori_tg.tiers[1][i]
                min_t, max_t, text = interval.minTime, interval.maxTime, interval.mark
                if text == 'spn':
                    print(f'{key} oov')
                    no_write = True
                #合并儿化音 儿 x er -> xer
                elif text == 'x':
                    interval = ori_tg.tiers[1][i+1]
                    next_text = interval.mark
                    if next_text == 'er':
                        tone = tones[count]
                        text = f'xer{tone}'
                        count += 1
                        max_t = interval.maxTime
                        i += 1
                elif text == '' or text in SM or text.isupper():
                    pass
                #去掉伪声母 ‘y’
                elif text == 'y':
                    interval = ori_tg.tiers[1][i+1]
                    max_t, text = interval.maxTime, interval.mark
                    tone = tones[count]
                    #tone == '2' if tone =='6' else tone
                    text = f'{text}{tone}'
                    count += 1
                    i += 1
                #添加声调至韵母
                else:
                    tone = tones[count]
                    text = f'{text}{tone}'
                    count += 1
                infos[1].append((text,min_t,max_t))
                i += 1
            new_tier_1 = IntervalTier(name='words', minTime=0, maxTime=ori_tg.maxTime)
            new_tier_2 = IntervalTier(name='phones', minTime=0, maxTime=ori_tg.maxTime)
            new_tier_3 = IntervalTier(name='words', minTime=0, maxTime=ori_tg.maxTime)
            tiers = [new_tier_1, new_tier_2, new_tier_3]
            for i in range(3):
                for item in infos[i]:
                    text,min_t,max_t = item
                    tiers[i].add(min_t, max_t, text)
            ori_tg.tiers[0] = new_tier_1
            ori_tg.tiers[1] = new_tier_2
            ori_tg.append(new_tier_3)
            if no_write:
                continue
            ori_tg.write(new_tg_path)
            #print(new_tg_path)
        except Exception as e:
            print(key, e)
            continue
        #    print(contents)
        #    print(pys)
        #    print(tones)
        #    logger.error(f'file {key} not generate tri_tg')
        #    print(e)
        #    break
        #    logger.error('file {} not generate tri_tg : {} \t {}'.format(ori_tg_path, contents, ' '.join([i[0] for i in infos[0]])))

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='')
    parser.add_argument('--num_threads',type=int,default=32)
    parser.add_argument('work_dir', help='full dir path that contains testgrid generate by mfa')
    args = parser.parse_args()

    #data prepare
    MIX_UTTS = 10000
    new_dirs = set()
    data = list()
    new_tg_dict, old_tg_dict = dict(), dict()
    py_dir = os.path.join(args.work_dir, 'split_pys')

    for dirpath, dirnames, filenames in os.walk(os.path.join(args.work_dir, 'tg_res')):
        for filename in filenames:
            key = filename.replace('.TextGrid','')
            old_tg_dict[key] = os.path.join(dirpath, filename)
    
    tg_fo = open(os.path.join(args.work_dir, 'tg.scp'), 'w', encoding='utf8')
    with open(os.path.join(args.work_dir, 'info.list'), 'r', encoding='utf8') as fin:
        for line in fin:
            line = line.strip().split('\t')
            key, name, save = line[0], line[1], line[-1] 
            new_dirs.add(save)
            tg_path = os.path.join(save, f'{key}.TextGrid')
            new_tg_dict[key] = tg_path
            tg_fo.write(f'{tg_path}\n')
    tg_fo.close()
    
    for dir in new_dirs:
        os.makedirs(dir, exist_ok=True)

    for file in os.listdir(py_dir):
        if 'syllable' not in file:
            continue
        file = os.path.join(py_dir, file)
        with open(file, 'r', encoding='utf8') as fin:
            lines = fin.readlines()
            for i in range(0, len(lines), 2):
                key, content = lines[i].strip().split('\t')
                #remove
                content = re.sub(r'#\d+','',content)
                contents = re.findall(r'[a-zA-Z\']+|[\u4e00-\u9fff]',content)
                #contents = content.split()
                pys = lines[i+1].lstrip('\t')
                pys = re.sub(r'[^a-z1-5_ \']', '', pys)
                pys = pys.split() 
                try:
                    data.append((key, contents, pys, old_tg_dict[key], new_tg_dict[key]))
                    #tg_fo.write(f'{new_tg_dict[key]}\n')
                except:
                    continue
                    logger.error(f'------重写textgrid数据准备阶段映射关系缺失 key : {key}')
    
    #rewrite_textgrid(data)

    random.shuffle(data)
    total_iter = (len(data) // MIX_UTTS) if len(data) % MIX_UTTS == 0 else (len(data) // MIX_UTTS) + 1
    partitions = [data[i*MIX_UTTS:(i+1)*MIX_UTTS] for i in range(0, total_iter)]

    with multiprocessing.Pool(processes=args.num_threads) as pool:
        for _ in tqdm(pool.imap_unordered(rewrite_textgrid, partitions), total=len(partitions)):
            pass



