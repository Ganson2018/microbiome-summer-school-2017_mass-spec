#Script to install and compile the c++ tools for alignment in the tutorial
#author = Francis Brochu
#Microbiome Summer School 2017


cd example/tutorial_code/cpp_extensions

mkdir test_build

cd test_build

cmake ..

make
