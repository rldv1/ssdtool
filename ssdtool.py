import os, random, time, zlib
try: import psutil
except ImportError:
    print("Please run pip3 install psutil"); exit(1)
iter_speed = [0, 0, 0]


# im want use async/multithreading which mostly complicates a code, but i remembered for crc32 and random.getrandbits which is much faster than md5 and urandom
# urandom as turned out works very slowly on a lot of calls

stoh = lambda a, b: '\n'.join([
    f"{b+i:04X} | {' '.join([a.upper()[j:j+2] for j in range(i, i+32*2, 2)])}"
    for i in range(0, len(a.upper().replace(' ', '')), 32*2)
])

def scan_disk(disk_path, mode=0):
    global iter_speed #bruh
    bstat = [0, 0]
    block_size = 4096 - 4
    bad_blocks_file = open("report.txt", "w")


    ranges_bad = []
    with open(disk_path + "/ssdtool", "rb") as t:
        blocks = int.from_bytes(t.read(4), "big")
        if int((os.stat(disk_path + "/ssdtool").st_size - 4)/4096) != blocks:
            if input("'ssdtool' file header seems is corrupted, try to fix it? (Y/n) > ").lower() == "y":
                blocks = int((os.stat(disk_path + "/ssdtool").st_size - 4)/4096)
                print(f"Fixed... ({blocks})\n")
        
        
        
        
        for _ in range(blocks):
            payload = t.read(block_size)
            checksum = int.from_bytes(t.read(4), "big")
            payload_ch = zlib.crc32(payload)
            
            iter_speed[1] += len(payload) + 4
            bstat[int(payload_ch != checksum)] += 1
            
            if payload_ch != checksum:
                i = int((_/blocks)*100 / 2)
                ranges_bad.append(range((i*2)-1, i*2))
                if bstat[1] <= 512: bad_blocks_file.write("\n[!] BAD BLOCK at #{}\nPayload/Declared hash: {}/{}\nPayload content:\n{}\n\n".format(_, payload_ch, checksum, stoh(payload.hex(), b=int(_*4096))))
            
            
            
            if time.time() - iter_speed[0] > 1: 
                iter_speed = [time.time(), 0, iter_speed[1]]
            if _ % 128 == 0: 
                print(f"\x1b[A\r{round((_/blocks)*100, 2)}% #{_}, BAD: {bstat[1]}, OK: {bstat[0]}, {round(iter_speed[2]/1024/1024, 2)}mb/s  ", end="\r", flush=1)
                print("\n[{}]".format("".join(("!" if range((i*2)-1, i*2) in ranges_bad else "+") if (_/blocks)*100 > i*2 else " " for i in range(50))), end="\r", flush=1)
    print(f"\nAll is OK" if bstat[1] == 0 else f"\nCorrupted blocks ({bstat[1]})! Back up your data immediately")
                
                

    

def write_random_blocks(disk_path, blocks=0, mode=0):
    global iter_speed #bruh
    
    block_size = 4096 - 4  # 4 KB
    
    
    
    print("Writing {} blocks to device ({}GB)".format(blocks, round((blocks*4096) / 1024 / 1024 / 1024, 2)))

    with open(disk_path + "/ssdtool", 'wb') as f:
        f.write(blocks.to_bytes(4, "big"))
        for _ in range(blocks):
            random_data = random.getrandbits(block_size*8).to_bytes(block_size, byteorder='big')
            f.write(random_data + zlib.crc32(random_data).to_bytes(4, "big")); f.flush()
            iter_speed[1] += block_size
            

            if time.time() - iter_speed[0] > 0.1:
                iter_speed = [time.time(), 0, iter_speed[1]*10]
                print(f"{round((_/blocks)*100, 1)}% Block #{_} on {round(iter_speed[2]/1024/1024, 2)}mb/s  ", end="\r", flush=1)


def main():
    if input("Write here? (~/ssdtool) (Y/n) > ").lower() == "n":
        try:
            disks = psutil.disk_partitions() #also can return None or throw a exception (when running, for example on termux), so need to consider this....
        except: disks = None
    
        if not disks:
            print("Try run as sudo, please.")
            return
    
        print("Avaliable partitions:\n")
        for i, disk in enumerate(disks):
            print(f"{i+1}. {disk.mountpoint} ({disk.device}, {disk.fstype.upper()})")
    
        selected_disk = disks[int(input("\nSelect partition: ")) - 1].mountpoint
    else:
        if not os.path.exists("ssdtool"): os.mkdir("ssdtool")
        selected_disk = "ssdtool"
    try:
        
        print("Searching for /ssdtool...")
        test_file = selected_disk + "/ssdtool"
        if os.path.exists(test_file):
            with open(test_file, "rb") as t: blocks = int.from_bytes(t.read(4), "big")
            print("There is {} blocks written here...".format(blocks))
            
            if input("Read all of them? (Y/n) > ").lower() == "y":
                print("\n")
                scan_disk(selected_disk)
                return
        
        if input("Read/Write (Y/n) > ").lower() == "y":
            scan_disk(selected_disk)
        else:
            print("Is {}mb free on selected partition".format(int(psutil.disk_usage(selected_disk).free/1024/1024)))
            sz = input("MB to be tested? (or ENTER to all free space): ")
            write_random_blocks(selected_disk, blocks=int(psutil.disk_usage(selected_disk).free / 4096)-1 if not sz else int((int(sz)*1024*1024)/4092))
            print("\nAll is OK. Now you can read all of them or do it later (i advice exactly that)..")
    except ValueError:
        return

if __name__ == "__main__":
    main()
    input()
