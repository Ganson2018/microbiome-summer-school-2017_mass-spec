How to compile:

1) Create a folder that will contain the program and your files to be processed (mass spectra)
2) Put all the source files and your files to be processed into this folder
2) Create a subdirectory in this folder called « buld »
3) Go into this build folder an run a shell (command line console) where build is the default directory
4) Execute « cmake .. » in the command line (this will create a cake project into the build folder 
5) Execute « make » in the command line (this will create an executable calle « main »). You may want to rename this executable to a more descriptive name such as « alignmentPgm » 

How to execute:

1) Suppose the executable is called « main ». Just type «./main » in the command line
2)  When prompt, enter the name of the file containing all the mz values of all your spectra. You must have one line per spectrum and each mz value must be comma-separated (e.g.., a csv file)
3) When prompted enter the window size in relative units (e.g., 4.8e-6 means 4.8 ppm)
4) When finished, the program will write to a file and will indicate the name of that file.
5) The set of all isolated alignment points are in this file

How to use the program for finding all isolated VLM point:

1) Open the the ActiveSequence.cpp file and replace the « //#define VLM » line by « #define VLM » (i.e., uncomment the #define macro)

2) Recompile the program according to the same steps above. The executable is now going to find all the isolated VLM points instead of all isolated alignment points.