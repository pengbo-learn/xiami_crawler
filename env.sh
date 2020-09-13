#!/bin/bash
pip install tqdm==4.48.2
pip install selenium==3.141.0
wget https://ftp.mozilla.org/pub/firefox/releases/56.0.2/linux-x86_64/en-US/firefox-56.0.2.tar.bz2 -O driver/firefox.tar.bz2
cd driver && tar jxvf firefox.tar.bz2 && cd ..
cd rpms && yum install parallel-20150522-1.el7.cern.noarch.rpm
