#! /bin/sh

mkdir ~/ewvCTA
cd ~/ewvCTA
git clone https://gitlab.cern.ch/ewv/CTA.git
cd ~/ewvCTA/CTA; git checkout --track origin/hack_cpio

cd ~/ewvCTA/CTA; git pull
cp ~/ewvCTA/CTA/migration/gRPC/CMakeLists.txt    ~/CTA/migration/gRPC/CMakeLists.txt
cp ~/ewvCTA/CTA/migration/gRPC/EosImportFilesCSV.cpp    ~/CTA/migration/gRPC/EosImportFilesCSV.cpp
cp ~/ewvCTA/CTA/migration/gRPC/EosImportFiles.cpp    ~/CTA/migration/gRPC/EosImportFiles.cpp
cp ~/ewvCTA/CTA/migration/gRPC/EosImportFiles.hpp    ~/CTA/migration/gRPC/EosImportFiles.hpp
cp ~/ewvCTA/CTA/migration/gRPC/GrpcClient.cpp ~/CTA/migration/gRPC/GrpcClient.cpp

cd ~/CTA-build && cmake ../CTA; make -j 4


