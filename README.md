# ssdtool
- **Uses advanced scientific technology Govnocode(R) Ultra**
- Simple utility to rough disk test
- Its does not format selected disk. it can use the remaining disk space

## Update (03.12.23)
- Add Windows support (macos also checked)
- Generation speed of random blocks increased to 200-250mb/s
- Now uses CRC32, no more MD5
- Information about bad blocks now avaliable in log file (report.txt) which creates in directory from here script runs
  ![изображение](https://github.com/rldv1/ssdtool/assets/118821863/61dc55d5-843e-46c8-82a7-5f578876f6db)


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
