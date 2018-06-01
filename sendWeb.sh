#!/bin/bash

tar -czvf send.tar.gz website/
scp send.tar.gz pi@192.168.0.95:~/Web
rm send.tar.gz

