# ToDO for autoPic

## Important

- [x] PROGRESS BAR! (feedback that its working)
- [x] multithread
- [x] change defult opening directory when you change directories
- [x] Error messages/handeling (Only works for errors in the main loop not in the take pics thread)
- [x] change Icon in pyqt not just windows shortcut
- [x] editing multiple files
- [x] make for mac
- [x] layout thats not px based
- [x] string error in input field
- [] make it faster (10 videos might take an hour with 2 laptops; or about 1-.5 pictures made per second rn)
- [x] Error messages for errors in the thread (look into Qthread)
- [] mac installer
- [] add unit tests
- [] add logging of errors
- [] make installer smaller
- [] auto check for updates from client side

## TO-DO Later (nice to haves but not needs or priorities a.k.a. ideas that i probably shouldn't act on)

- [x] When you click to change the start time in the GUI it should auto select the whole number in blue.
- [x] make it look pretty
- [x] does making the imports more specific make the final file size smaller?
- [x] settings menu to replace directly editing json file (removed interaction with json settings file)
- [x] consistent var names like _ vs cammelCase
- [x] consistent names outFolderName vs outputFolderName
- [x] working with paths is not organized

## Bugs

- [x] open threads don't close when the program does
- [x] improperly closes program
- [x] 2 videos in the same folder over write eachother
- [x] start time cant be changed to 30 in the gui
- [x] WARNING when you have old files with the same name as what will be generated and run the program they will overwire the old files.
- [x] if there is no input file, there is a unhandeled error when you run take pictures
- [x] running take pictures with no input might crash
- [] end time is out of sync
