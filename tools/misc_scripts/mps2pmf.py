#!/usr/bin/env python
import os, binascii, subprocess, re, sys

def get_mps_size(filename):
    mps_size = hex(os.path.getsize(filename))[2:].rjust(8,"0")
    return mps_size

def get_video_dimension(filename):
    result = subprocess.Popen(["ffprobe", filename],
        stdout = subprocess.PIPE, stderr = subprocess.STDOUT)
    for x in result.stdout.readlines():
        if "Stream" in x:
            dimension = re.search(' (\d+?x\d+?) ', x)
            if dimension:
                height = dimension.group(1).split("x")[0]
                width = dimension.group(1).split("x")[1]
            else:
                print("Failed to get video dimensions.")
                sys.exit()
    return height, width

def get_video_length(filename):
    result = subprocess.Popen(["ffprobe", filename],
        stdout = subprocess.PIPE, stderr = subprocess.STDOUT)
    for x in result.stdout.readlines():
        if "Duration" in x:
            video_length = x.split(" ")[3][:-1].split(":")
            hour = int(video_length[0])*60*60*100
            mins = int(video_length[1])*60*100
            secs = int(video_length[2].split(".")[0])*100
            centisec = int(video_length[2].split(".")[1])
            duration = hour+mins+secs+centisec
            video_dur = hex(int((int(duration)*10800000)/10000))[2:].rjust(8,"0")
    return video_dur

def build_pmf_header(mps_size, video_dur, dev_hook_fix, pmf_type):
    pmf_id = "50534D46" ## PSMF
    pmf_ver = "3030"+binascii.hexlify(str(pmf_type)) ## 0014
    pmf_size = "00000800" ## 2048 bytes from start of header
    mps_size = mps_size
    unk1 = "0000"
    tick_freq = "00015F90" ## 90k something
    mux_rate = "000061A8" ## Equal to program_mux_rate in mps pack_header
    if pmf_type == 12:
        table_size = "0000004E"  ## Size of the mapping table from 0x54
        unk2 = "0201000000340000"
        dh_video_dur = "00696F75"
        unk3 = "0001000000220002E00021EF"+unk1*4+"1E110000BD002004"+unk1*5+"0202"
    elif pmf_type == 14:
        table_size = "0000003E"
        unk2 = "0101000000240000"
        dh_video_dur = "0005F49C"
        if dev_hook_fix == 1:
            unk3_byte = "16"
        else:
            unk3_byte = "14"
        unk3 = "0001000000120001E00020"+unk3_byte+unk1*4+"09050000"
    if dev_hook_fix == 1:
        video_dur = dh_video_dur
    else:
        video_dur = video_dur

    ## PMF Header Ordering ##
    pmf_buffer = pmf_id+pmf_ver+pmf_size+mps_size+unk1*32+table_size+unk1+tick_freq+unk1+video_dur+mux_rate+tick_freq+unk2+tick_freq+unk1+video_dur+unk3
    return pmf_buffer
    
f = []
filelist=[]
dev_hook_fix = 0
for item in os.listdir(os.getcwd()):
    f.append(item)
for item in f:
    if item[-4:] == '.mps':
        filelist.append(item)
for files in filelist:
    with open(files, "rb") as f:
        print(files)
        mps_size = get_mps_size(files)
        video_height, video_width = get_video_dimension(files)
        if video_height == "144" and video_width == "80":
            pmf_type = 14
        else:
            pmf_type = 12
        video_dur = get_video_length(files)
        pmf_header = build_pmf_header(mps_size, video_dur, dev_hook_fix, pmf_type).ljust(4096,"0")
        pmf_file = open(files[:-4]+".pmf", "wb")
        pmf_file.write(binascii.unhexlify(pmf_header)+f.read())
