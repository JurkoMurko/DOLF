import time
import datetime

start = time.time()

import ffmpeg

project_path = 'C:\\Users\\jurko\\Documents\\Sky_Diving_Video_Project'
video_folder_path = 'Real2'

ttime = 0.5 # Transition Time

jump_index = 4
talking_video_index = [1,2,7]

intro_vid = ffmpeg.input(f'{project_path}\\Assets\\intro2.mp4')
outro_vid = ffmpeg.input(f'{project_path}\\Assets\\outro_good.mp4')

music_1 = ffmpeg.input(f'{project_path}\\Assets\\music_bounce.mp3', stream_loop=-1)
music_2 = ffmpeg.input(f'{project_path}\\Assets\\music_electronic-rock.mp3', stream_loop=-1)
music_3 = ffmpeg.input(f'{project_path}\\Assets\\music_electronic-rock.mp3')

logo_img = ffmpeg.input(f'{project_path}\\Assets\\logo_small2.png')
jump_img = ffmpeg.input(f'{project_path}\\Assets\\graphic_3000.png')

class Vids():
    def __init__(self, path, start, end, previous_end_tstamp) -> None:
        if type(start) == type((0,0)):
            self.start = start[0]*60+start[1]
        else:
            self.start = start
            
        if type(end) == type((0,0)):
            self.end = end[0]*60+end[1]
        else:
            self.end = end
        
        self.path = f'{project_path}\\{video_folder_path}\\{path}'
        
        self.duration = self.end - self.start
        self.tstamp = self.duration + previous_end_tstamp - ttime
        
        self.vid = ffmpeg.input(self.path, ss=self.start, to=self.end)

info = (
    ('GX010752.mp4', 56, 120), # learning 1
    ('GX010752.mp4', 3*60+31, 3*60+51), # learning 2
    ('GX010705.mp4', 167, 177), # takeoff and highfive
    # ('GX010706.MP4', 0, 7), # flying 1
    # ('GX010707.MP4', 0, 15), # flying 2
    ('GX010708.MP4', 0, 9), # before jump
    ('GX010709.MP4', 48, 77), # Jump vid
    ('GX010709.MP4', 121, 126), # after jump in air
    ('GX010709.MP4', 198, 215), # keruje
    ('GX010709.MP4', 60*4+37, 5*60+27) # landing
)
highlight_list = [(3,2,6),(4,4,8),(6,1,5),(7,0,4), (7,34,38)]

total_length = 27
for i in info:
    total_length += i[2]-i[1]
    
for i in highlight_list:
    total_length += i[2]-i[1]
print(f'\n\nTotal Video Length: {total_length//60}:{total_length%60}\n\n')

# init Vid struct
vids = []
for i in range(len(info)):
    if i == 0:
        vids.append(Vids(info[i][0], info[i][1], info[i][2], 0))
    else:
        vids.append(Vids(info[i][0], info[i][1], info[i][2], vids[i-1].tstamp))

#Edit Audio
music_1 = ffmpeg.filter(music_1, 'atrim', end=vids[jump_index-1].tstamp).filter('volume', volume=0.2)
music_2 = ffmpeg.filter(music_2, 'atrim', end=vids[-1].tstamp-vids[jump_index-1].tstamp).filter('volume', volume=0.2)
music = ffmpeg.filter([music_1, music_2], 'concat', n=2, a=1, v=0)

for i in range(len(talking_video_index)):
    music = ffmpeg.filter(music, 'volume', volume=0.2, enable=f'between(t,{vids[talking_video_index[i]-1].tstamp},{vids[talking_video_index[i]].tstamp})') # Unmute Talking
    delayed_audio = ffmpeg.filter(vids[talking_video_index[i]].vid, 'adelay', all=True, delays=f'{int((vids[talking_video_index[i]-1].tstamp)*48000)}S')

    delayed_audio = ffmpeg.filter(delayed_audio, 'aresample', 44100)
    music = ffmpeg.filter([delayed_audio, music], 'amix', inputs=2)

# Highlight Clips 
clip_list = []
clips_duration = 0
for i in highlight_list:
    clip_list.append(ffmpeg.filter(vids[i[0]].vid, 'trim', start=i[1], end=i[2]).filter('setpts', 'PTS-STARTPTS'))
    clips_duration += i[2] - i[1]

highlight_clips = ffmpeg.filter(clip_list, 'concat', n=len(clip_list), a=0 )
highlight_clips = ffmpeg.filter(highlight_clips, 'huesaturation', saturation=-1, colors='b+g+y', strength=100)
music_3 = ffmpeg.filter(music_3, 'atrim', end=clips_duration)

# Crossfade and Concats
i=1
offset = 0
concat_vid = vids[0].vid
while i < len(vids):
    offset += vids[i-1].duration - ttime
    vids[i-1].vid = ffmpeg.filter(vids[i-1].vid, 'tpad', stop = (vids[i].duration-(ttime*i))*30)
    concat_vid = ffmpeg.filter([concat_vid, vids[i].vid], 'xfade', duration=ttime, offset=offset) 
    i +=1

# Overlay logo 
concat_vid = ffmpeg.filter([concat_vid, logo_img], 'overlay', x='W-(w+50)', y=50)
concat_vid = ffmpeg.filter([concat_vid, jump_img], 'overlay', x=30, y=900, enable=f'between(t,{vids[jump_index-1].tstamp},{vids[jump_index-1].tstamp + 6})')

# Highlight Clips 
highlight_list = [(0,2,6),(4,5,9),(6,2,6),(7,8,12)]
clip_list = []
clips_duration = 0
for i in highlight_list:
    clip_list.append(ffmpeg.filter(vids[i[0]].vid, 'trim', start=i[1], end=i[2]).filter('setpts', 'PTS-STARTPTS'))
    clips_duration += i[2] - i[1]
    
highlight_clips = ffmpeg.filter(clip_list, 'concat', n=len(clip_list), a=0 )
highlight_clips = ffmpeg.filter(highlight_clips, 'huesaturation', saturation=-1, colors='b+g+y', strength=100)
music_3 = ffmpeg.filter(music_3, 'atrim', end=clips_duration)

# Joining all the Videos + Audios
vid = ffmpeg.filter([
            intro_vid.video,
            intro_vid.audio,
            concat_vid,
            music,
            outro_vid.video,
            outro_vid.audio,
            highlight_clips,
            music_3],
            'concat', n=4, a=1
            )

# Output & Run
out = ffmpeg.output(vid, 'out\\fix.mp4')
out = out.global_args('-hide_banner')
print(out.get_args())
ffmpeg.run(out, overwrite_output=True)

time_elapsed = time.time() - start
form = datetime.timedelta(seconds=time_elapsed)
print('The Program Took: ', form)
