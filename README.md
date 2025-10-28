# Automatic Picture Taking from Video Frames

Takes an input video as well as a few settings you can configure like start or end time, as well as the interval of the picutes, and outputs pictures into a new folder in the same directory as the input video.

Note: This used to use FFMPEG which was faster but so some reason I could not figure out the pictures can out lower quality than the original video. Now it uses OpenCV.

This was a first time I had to make something for a non programmer to use so I learned a lot. My first gui, error handeling, user feadback, installation on other computers, "it works on my machine" types of problems. All 10/10 learning experiances.

## Installation

You can either clone the project which is a far smaller download, but you will need to have python 3 installed. Otherwise you can download one of the released installers.

I used pyinstaller to turn my .py file into an .exe file. InstallForge was used to create the windows installer from the .exe file.

## Features

- get pictures from any video file
- start time, end time, and interval for selecting which frames you want.
- GUI
- process multiple videos at once
- progress "bar"
- saving settings
- error dialogs
- ...and a lot of little things you'll never notice unless they were missing <3
