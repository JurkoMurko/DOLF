# Automatic Picture Taking from Video Frames

Takes an input video as well as a few settings you can configure like start or end time, as well as the interval of the picutes, and outputs pictures into a new folder in the same directory as the input video.

Note: This used to use FFMPEG which was faster but so some reason I could not figure out the pictures can out lower quality than the original video. Now it uses OpenCV.

This was a first time I had to make something for a non programmer to use so I learned a lot. My first gui, error handeling, user feadback, installation on other computers, "it works on my machine" types of problems. All 10/10 learning experiances.

## Windows and MacOS installer

I don't know how people share python projects where they create an installer on GitHub. So here are the instructions for how to build the project and installer yourself.

I use pyinstaller to create an .exe file. It can be installed with pip.

To use my settings run:

```pyinstall pics.spec```

Your executable will be in the dist folder that is generated.

I used install forge to generate an installer for windows.

Note: I don't remember how I used Install Forge so please google it you smart little cookie
