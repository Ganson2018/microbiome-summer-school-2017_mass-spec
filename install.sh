#Script to install and compile the c++ tools for alignment in the tutorial
#author = Francis Brochu
#Microbiome Summer School 2017

conda create -n ms python=3.5 anaconda

source activate ms

cd example/tutorial_code/cpp_extensions

mkdir test_build

cd test_build

cmake ..

make
