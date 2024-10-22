import ffmpeg
from os import listdir
import time
import datetime

start = time.time()

# in_file = ffmpeg.input(folder_path + '\OG_Clips\GX010344.mp4')
# overlay_file = ffmpeg.input(folder_path + 'Assests\logo.png')
video_folder_path = 'Real'
output_folder_path = 'Real2'
try:
    for file in range(1):#listdir(video_folder_path):
        vid = ffmpeg.input(f'{video_folder_path}\\GX010752.mp4').video
        aud = ffmpeg.input(f'{video_folder_path}\\GX010752.mp4').audio
        vid = ffmpeg.filter(vid, 'fps', 30)
        vid = ffmpeg.filter(vid, 'scale', '1920x1080')
        vid = ffmpeg.filter(vid, 'setsar', '1')

        fname = str(file).split('.')[0]
        out = ffmpeg.output(vid, aud, f'{output_folder_path}\\' + 'GX010752' + '.mp4')
        ffmpeg.run(out)
except ffmpeg._run.Error as e:
    print(e)


time_elapsed = time.time() - start
form = datetime.timedelta(seconds=time_elapsed)
print('The Program Took: ', form)


'''
import ffmpeg

path = 'C:\\Users\\jurko\\Documents\\Sky_Diving_Video_Project\\Assets\\intro.mov'
# path = 'C:\\Users\\jurko\\Documents\\Sky_Diving_Video_Project\\Assets\\Compact_Outro.mp4'

vid = ffmpeg.input(path).video
aud = ffmpeg.input(path).audio
vid = ffmpeg.filter(vid, 'fps', 30)
out = ffmpeg.output(vid, aud, 'intro2.mp4')
ffmpeg.run(out)
'''