#Script to install and compile the c++ tools for alignment in the tutorial
#author = Francis Brochu
#Microbiome Summer School 2017

sudo apt-get install python3-pip && \
sudo apt-get install python3-venv && \
python3 -m venv ./ms && \

cd example/tutorial_code/cpp_extensions

mkdir test_build

cd test_build

cmake ..

make
