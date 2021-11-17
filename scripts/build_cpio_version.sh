#! /bin/sh

# mkdir ~/ewvCTA
# cd ~/ewvCTA
#  git clone https://gitlab.cern.ch/ewv/CTA.git
# git checkout --track origin/hack_cpio

cd ~/ewvCTA/CTA; git pull
cp ~/ewvCTA/CTA/tapeserver/castor/tape/tapeserver/file/File.cpp    ~/CTA/tapeserver/castor/tape/tapeserver/file/File.cpp
cp ~/ewvCTA/CTA/tapeserver/castor/tape/tapeserver/file/File.hpp    ~/CTA/tapeserver/castor/tape/tapeserver/file/File.hpp

cd ~/CTA-build && cmake ../CTA; make -j 4


