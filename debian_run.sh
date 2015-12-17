#!/bin/bash
# for debian8 (this must a bug..)
BASEDIR=/home/evilmaster/project/mdview

LD_PRELOAD=/usr/lib/x86_64-linux-gnu/libwx_gtk2u_webview-3.0.so.0.2.0 python $BASEDIR/mdview.py "$1"
