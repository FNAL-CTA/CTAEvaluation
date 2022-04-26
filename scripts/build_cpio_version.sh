#! /bin/sh

cd ~/CTA

git remote add ewv https://ewv@gitlab.cern.ch/ewv/CTA.git
git fetch --all
git checkout ewv/FNAL_cpio_old

cd ~/CTA-build && cmake ../CTA; make -j 4

exit;



mkdir ~/ewvCTA
cd ~/ewvCTA
git clone https://gitlab.cern.ch/ewv/CTA.git
cd ~/ewvCTA/CTA; git checkout --track origin/fnal_cpio

cd ~/ewvCTA/CTA; git pull
cp ~/ewvCTA/CTA/tapeserver/castor/tape/tapeserver/file/File.cpp    ~/CTA/tapeserver/castor/tape/tapeserver/file/File.cpp
cp ~/ewvCTA/CTA/tapeserver/castor/tape/tapeserver/file/File.hpp    ~/CTA/tapeserver/castor/tape/tapeserver/file/File.hpp
cp ~/ewvCTA/CTA/tapeserver/castor/tape/tapeserver/file/OSMFile.cpp    ~/CTA/tapeserver/castor/tape/tapeserver/file/OSMFile.cpp
cp ~/ewvCTA/CTA/tapeserver/castor/tape/tapeserver/file/OSMFile.hpp    ~/CTA/tapeserver/castor/tape/tapeserver/file/OSMFile.hpp
cp ~/ewvCTA/CTA/tapeserver/castor/tape/tapeserver/file/OSMBasicLabelTest.cpp    ~/CTA/tapeserver/castor/tape/tapeserver/file/OSMBasicLabelTest.cpp
cp ~/ewvCTA/CTA/tapeserver/castor/tape/tapeserver/file/OSMToolCPIO.cpp    ~/CTA/tapeserver/castor/tape/tapeserver/file/OSMToolCPIO.cpp
cp ~/ewvCTA/CTA/tapeserver/castor/tape/tapeserver/file/OSMXDR.cpp    ~/CTA/tapeserver/castor/tape/tapeserver/file/OSMXDR.cpp
cp ~/ewvCTA/CTA/tapeserver/readtp/ReadtpCmd.cpp    ~/CTA/tapeserver/readtp/ReadtpCmd.cpp
cp ~/ewvCTA/CTA/tapeserver/readtp/ReadtpCmd.hpp    ~/CTA/tapeserver/readtp/ReadtpCmd.hpp
#cp ~/ewvCTA/CTA/tapeserver/castor/tape/tapeserver/daemon/TapeReadTask.hpp    ~/CTA/tapeserver/castor/tape/tapeserver/daemon/TapeReadTask.hpp

cp ~/ewvCTA/CTA/migration/gRPC/CMakeLists.txt    ~/CTA/migration/gRPC/CMakeLists.txt
cp ~/ewvCTA/CTA/migration/gRPC/EosImportFilesCSV.cpp    ~/CTA/migration/gRPC/EosImportFilesCSV.cpp
cp ~/ewvCTA/CTA/migration/gRPC/EosImportFiles.cpp    ~/CTA/migration/gRPC/EosImportFiles.cpp
cp ~/ewvCTA/CTA/migration/gRPC/EosImportFiles.hpp    ~/CTA/migration/gRPC/EosImportFiles.hpp
# cp ~/ewvCTA/CTA/migration/gRPC/GrpcClient.cpp ~/CTA/migration/gRPC/GrpcClient.cpp

cd ~/CTA-build && cmake ../CTA; make -j 4
