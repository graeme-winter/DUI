#!/bin/bash -xe
# setup script to prepare setpath script

# Python script the generates setpath.sh script
# with hard-codded path to runnable tools

# The next line seem to be more POSIX / UNIX-like
# but it brakes my automated << update all >> script
#MY_WD=$(cd $(dirname ${0}); pwd)

#The next line work better when this script is called from external script
MY_WD=$(pwd)

#ccp4-python ${MY_WD}/write_setpath.py ${MY_WD}
dials.python ${MY_WD}/write_setpath.py ${MY_WD}

#temporary skipping

#Attemplting to compile list C++ extension

#cd ${MY_WD}/../idials_GUI/outputs_n_viewers
#dials.python compyling_boost_ext.py

#cd ${MY_WD}
