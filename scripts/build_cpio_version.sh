#! /bin/sh

# mkdir ~/ewvCTA
# cd ~/ewvCTA
#  git clone https://gitlab.cern.ch/ewv/CTA.git
# cd ~/ewvCTA/CTA; git checkout --track origin/hack_cpio

cd ~/ewvCTA/CTA; git pull
cp ~/ewvCTA/CTA/tapeserver/castor/tape/tapeserver/file/File.cpp    ~/CTA/tapeserver/castor/tape/tapeserver/file/File.cpp
cp ~/ewvCTA/CTA/tapeserver/castor/tape/tapeserver/file/File.hpp    ~/CTA/tapeserver/castor/tape/tapeserver/file/File.hpp
cp ~/ewvCTA/CTA/tapeserver/castor/tape/tapeserver/daemon/TapeReadTask.hpp    ~/CTA/tapeserver/castor/tape/tapeserver/daemon/TapeReadTask.hpp

cd ~/CTA-build && cmake ../CTA; make -j 4


