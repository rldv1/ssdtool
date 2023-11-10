# ssdtool
- **Uses advanced scientific technology Govnocode(R) Ultra**
- Simple utility to rough disk test
- Its does not format selected disk. it can use the remaining disk space

## HowTo
- Download a ssdtool
- Install psutil via `pip3 install psutil`
- Run via `python3 ssdtool.py`

## HowIt
Its pretty simple
- Creating `ssdtool` file in select partition
- Count of blocks is writed at the beginning of this file (first 4 bytes)
- It writes blocks of 4kb each
- Each block contains a checksum of 16 bytes
