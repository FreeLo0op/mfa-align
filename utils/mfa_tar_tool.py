import os
import io
import sys
import json
import argparse
import multiprocessing
import tarfile
from textgrid import TextGrid, IntervalTier
from tqdm import tqdm
import random    
from logger import logger

def get_key(file_path):
    key = file_path.strip().split('/')[-1]
    key = key.split('.')[0]
    return key

def write_tar_file(input_datas):
    '''
    input_datas shape and content
    partitions = [(data[i*part_len:(i+1)*part_len], 
                   os.path.join(args.shards_dir, '{}_{:09d}.tar'.format(args.prefix, i)),
                   shufix, i, args.num_threads) for i in range(0, end)]
    '''
    data_list, tar_file, index, total = input_datas
    with tarfile.open(tar_file, 'w') as tar:
        for item in data_list:
            try:
                if len(item) == 3:
                    key, txt, wav = item
                elif len(item) == 4:
                    key, txt, wav, tg = item
                else:
                    continue

                wav_file = wav.strip().split('/')[-1]
                with open(wav, 'rb') as audio_file:
                    audio_data = audio_file.read()
                with io.BytesIO() as f:
                    f.write(audio_data)
                    f.seek(0)
                    data = f.read()
                wav_data = io.BytesIO(data)
                wav_info = tarfile.TarInfo(wav_file)
                wav_info.size = len(data)
                tar.addfile(wav_info, wav_data)
                
                txt_file = key + '.txt'
                txt = txt.encode('utf8')
                txt_data = io.BytesIO(txt)
                txt_info = tarfile.TarInfo(txt_file)
                txt_info.size = len(txt)
                tar.addfile(txt_info, txt_data)
        
                if len(item) == 4:
                    tg_times = []
                    tg_in = TextGrid.fromFile(tg) 
                    for interval in tg_in.tiers[2]:
                        min_t, max_t, text = str(interval.minTime), str(interval.maxTime), interval.mark
                        if text != '':
                            tg_times.append([min_t, max_t])
                    tg_file = tg.strip().split('/')[-1]
                    #tg_file = key + '.TextGrid'
                    tg_bytes = '\n'.join([','.join(item) for item in tg_times]).encode('utf8')
                    tg_data = io.BytesIO(tg_bytes)
                    tg_info = tarfile.TarInfo(tg_file)
                    tg_info.size = len(tg_bytes)
                    tar.addfile(tg_info, tg_data)
            except:
                continue
            '''
            tar.add(tg, arcname=key+'.TextGrid')
            with open(tg, 'rb') as tg_file:
                tg_data = tg_file.read()
            tg_file = key + '.TextGrid'
            tg_data_io = io.BytesIO(tg)
            tg_info = tarfile.TarInfo(tg)
            tg_info.size = 0
            tar.addfile(tg_info)
            '''        

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='')
    parser.add_argument('--num_threads',type=int,default=20)
    parser.add_argument('--prefix',default='shards',help='prefix of shards tar file')
    parser.add_argument('work_dir', help='full wav path file')
    #parser.add_argument('info_list', help='full wav path file')
    #parser.add_argument('wav_file', help='full wav path file')
    #parser.add_argument('text_file', help='ori text file')
    #parser.add_argument('tg_file', help='full tg path file')
    #parser.add_argument('shards_dir', help='output shards dir')
    parser.add_argument('if_tar', type=int ,help='if need to tar set 1 slse 0')
    args = parser.parse_args()
    tg_file = os.path.join(args.work_dir, 'tg.scp')
    info_list = os.path.join(args.work_dir, 'info.list')
    shards_dir = os.path.join(args.work_dir, 'tars')
    
    data = []
    tg_table = {}
    with open(tg_file, 'r', encoding='utf8') as fin:
        for line in fin:
            key = get_key(line)
            tg_table[key] = line.strip()
    logger.info('Total number of tg files : {}'.format(len(tg_table.keys())))
    
    with open(info_list, 'r', encoding='utf8') as fin:
        for line in fin:
            try:
                key, name, wav, txt, save = line.strip().split('\t')
                tg_scp = tg_table[key]
                if not os.path.exists(tg_scp):
                    continue
                data.append((name, txt, wav, tg_table.get(key)))
            except:
                pass
    logger.info('Total number of data : {}'.format(len(data)))

    random.shuffle(data)
    if args.if_tar:
        shards_list = []
        os.makedirs(shards_dir, exist_ok=True)

        pool = multiprocessing.Pool(processes=args.num_threads)
        part_len = 10000
        end = (len(data) // part_len) + 1

        partitions = [(data[i*part_len:(i+1)*part_len], 
                    os.path.join(shards_dir, '{}_{:09d}.tar'.format(args.prefix, i)),
                    i, args.num_threads) for i in range(0, end)]

        for result in tqdm(pool.imap_unordered(write_tar_file, partitions), total=len(partitions)):
            shards_list.append(result)
        pool.close()
        pool.join()

    '''
    partitions = [data[i*part_len:(i+1)*part_len] for i in range(0, end)]

    for i, partition in enumerate(partitions):
        tar_file = os.path.join(args.shards_dir,
                                '{}_{:09d}.tar'.format(args.prefix, i))
        shards_list.append(tar_file)
        pool.apply_async(
            write_tar_file,
            (partition, tar_file, shufix, i, args.num_threads)
            )
    pool.close()
    pool.join()
    '''
    #with open(args.shards_list, 'w', encoding='utf8') as fo:
    #    for name in shards_list:
    #        fo.write(name+'\n')

    with open(os.path.join(args.work_dir, 'data.list'), 'w', encoding='utf8') as fo:
        json_data = list()
        for item in data:
            try:
                name, txt, wav, tg = item
                data_dict = {
                    "key": name,
                    "wav": wav,
                    "txt": txt,
                    "textgrid": tg
                }
                tmp = json.dumps(data_dict, ensure_ascii=False)
                json_data.append(str(tmp))
            except:
                continue
        fo.write('\n'.join(json_data))

