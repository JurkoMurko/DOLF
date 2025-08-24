import ffmpeg

project_path = 'C:\\Users\\jurko\\Documents\\Sky_Diving_Video_Project'
video_folder_path = 'New_Vids3'

ttime = 0.5 # Transition Time

jump_index = 4
talking_video_index = 3

intro_vid = ffmpeg.input(f'{project_path}\\Assets\\intro2.mp4')
outro_vid = ffmpeg.input(f'{project_path}\\Assets\\outro_good.mp4')

music_1 = ffmpeg.input(f'{project_path}\\Assets\\music_bounce.mp3', stream_loop=-1)
music_2 = ffmpeg.input(f'{project_path}\\Assets\\music_electronic-rock.mp3', stream_loop=-1)
music_3 = ffmpeg.input(f'{project_path}\\Assets\\music_electronic-rock.mp3')

logo_img = ffmpeg.input(f'{project_path}\\Assets\\logo_small2.png')
jump_img = ffmpeg.input(f'{project_path}\\Assets\\graphic_3000.png')

class Vids():
    def __init__(self, path, start, end, previous_end_tstamp) -> None:
        self.path = f'{project_path}\\{video_folder_path}\\{path}'
        self.start = start
        self.end = end
        self.duration = end - start
        self.tstamp = self.duration + previous_end_tstamp - ttime
        
        self.vid = ffmpeg.input(self.path, ss=start, to=end)

info = (
    ('GX010344.mp4', 0, 10), # getting on 
    ('GX010345.MP4', 0, 7), # taking off 1
    ('GX010346.MP4', 0, 15), # taking off 2
    # ('GX010348.MP4'),
    ('GX010349.MP4', 0, 9.5), # before jump (ideme na to + handshake)
    ('GX010350.MP4', 60, 93), # Jump vid
    ('GX010350.MP4', 183, 190), 
    ('GX010725.MP4', 69, 87), # external 1
    ('GX010725.MP4', 374, 391), # external landing
)

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

music_1 = ffmpeg.filter(music_1, 'volume', volume=0.3, enable=f'between(t,{vids[talking_video_index-1].tstamp},{vids[talking_video_index].tstamp})') # Unmute Talking
delayed_audio = ffmpeg.filter(vids[3].vid, 'adelay', all=True, delays=f'{int((vids[talking_video_index-1].tstamp)*48000)}S')
delayed_audio = ffmpeg.filter(delayed_audio, 'aresample', 44100)
mixed_audio = ffmpeg.filter([delayed_audio, music_1], 'amix', inputs=2)

edited_music = ffmpeg.filter([mixed_audio, music_2], 'concat', n=2, a=1, v=0)


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
            edited_music,
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
