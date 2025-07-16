print('Start Imports')
from moviepy.editor import VideoFileClip, AudioFileClip, ImageClip, CompositeVideoClip, CompositeAudioClip, concatenate_videoclips
print('Done Importing Libraries\nStart Loading Video Files\n')

def red_effect(image):
    return image[:,:,[0,1,1]]

folder_path = r'C:\Users\jurko\Documents\Sky_Diving_Video_Project'
unedited_vidio_path = f'{folder_path}\Videos30fps\\'
assets_path = fr'{folder_path}\assets'
music_bounce_path = fr'{assets_path}\music_bounce.mp3'
music_rock_path = fr'{assets_path}\music_electronic-rock.mp3'
logo_path = fr'{assets_path}\logo.png'
graphic_jump_path = fr'{assets_path}\graphic_3000.png'

intro_path = fr'{assets_path}\intro2.mp4'
outro_path = fr'{assets_path}\compact_outro30fps1080p.mp4'

intro_clip = VideoFileClip(intro_path)
outro_clip = VideoFileClip(outro_path)

bounce_audio = AudioFileClip(music_bounce_path)
rock_audio = AudioFileClip(music_rock_path)


jump_clip = VideoFileClip(unedited_vidio_path + 'GX010350.MP4')
training_clip = VideoFileClip(unedited_vidio_path + 'GX010346.MP4')
going_up_clip = VideoFileClip(unedited_vidio_path + 'GX010345.MP4')
landing_clip = VideoFileClip(unedited_vidio_path + 'GX010725.MP4')
# unedited_clip_list = [VideoFileClip(unedited_vidio_path + vid) for vid in os.listdir(unedited_vidio_path)]


print('Done Loading Video Files\nStart Edit')


time_line_list = [  going_up_clip.subclip(0,12),
                    training_clip.subclip(0,10),
                    training_clip.subclip(20,30), 
                    jump_clip.subclip(61,100),
                    landing_clip.subclip(69,86),
                    landing_clip.subclip((6,12), (6,31))]

end_clips = concatenate_videoclips([going_up_clip.subclip(10,12), 
                                    jump_clip.subclip(65,68),
                                    landing_clip.subclip(70,73),
                                    landing_clip.subclip((6,18), (6,21))])

end_clips.set_audio(rock_audio)

comp_vid = time_line_list[0]
id = intro_clip.duration
i = 1
transition_time = 0.5
while i < len(time_line_list):
    if time_line_list[i].filename == jump_clip.filename:
        jump_time = comp_vid.duration

    comp_vid = CompositeVideoClip([comp_vid, time_line_list[i]
                                   .set_start(comp_vid.duration - (transition_time*(1+i)))
                                   .crossfadein(transition_time)])
    i +=1

# graphic_logo = ImageClip(logo_path, duration=(comp_vid.duration)).resize(.3)
# graphic_jump = ImageClip(graphic_jump_path, duration=5).resize(.5)
# comp_vid = CompositeVideoClip([comp_vid, graphic_logo.set_position((2480,60))])
# comp_vid = CompositeVideoClip([comp_vid, graphic_jump.set_position((100,1200)).set_start(jump_time)])

compo = CompositeAudioClip([bounce_audio.set_end(jump_time),
                            rock_audio.set_start(jump_time).set_end(comp_vid.duration)])
comp_vid = comp_vid.set_audio(compo)

final_clip = concatenate_videoclips([intro_clip, comp_vid, outro_clip])
final_clip = CompositeVideoClip([final_clip, end_clips.fl_image(red_effect).set_start(comp_vid.duration)])


print('Done Edit\nStart Save/Preview')
# final_clip.resize(.25).preview(fps=30, fullscreen=False) 
# jump_clip.resize(.3).preview(fps=30, fullscreen=False) 
final_clip.write_videofile(f"{folder_path}\\fullTest2.mp4")