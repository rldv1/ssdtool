import os, hashlib, random, time
try: import psutil
except ImportError:
    print("Please run pip3 install psutil"); return
iter_speed = [time.time(), 0, 0]

def scan_disk(disk_path):
    bstat = [0, 0]
    block_size = 4096 - 16

    with open(disk_path + "/ssdtool", "rb") as t:
        blocks = int.from_bytes(t.read(4), "big")
        
        for _ in range(blocks):
            payload = t.read(block_size)
            checksum = t.read(16)
            payload_ch = hashlib.md5(payload).digest()
            
            iter_speed[1] += 4096
            if payload_ch != checksum:
                print("\n[!] BAD BLOCK AT {}\n1nd: {}\n2nd: {}\n\n".format(_, payload_ch, checksum))
                bstat[0] += 1
            else: bstat[1] += 1
            
            if time.time() - iter_speed[0] > 1:
                iter_speed[0] = time.time()
                iter_speed[2] = iter_speed[1]
                iter_speed[1] = 0
            print(f"{round((_/blocks)*100, 1)}% #{_}, BAD: {bstat[0]}, OK: {bstat[1]}, {round(iter_speed[2]/1024/1024, 2)}mb/s", end="\r", flush=1)
    print(f"\nAll is OK" if bstat[0] == 0 else f"\nCorrupted blocks! ({bstat[0]})")
                
                

    

def write_random_blocks(disk_path, blocks=0):
    block_size = 4096 - 16  # 4 KB
    

    with open(disk_path + "/ssdtool", 'wb', 0) as f:
        f.write(blocks.to_bytes(4, "big"))
        print("Writing {} blocks to device ({}GB)".format(blocks, round((blocks*4096) / 1024 / 1024 / 1024, 2)))
        
        for _ in range(blocks):
            random_data = os.urandom(block_size)
            random_data += hashlib.md5(random_data).digest()
            f.write(random_data)
            
            iter_speed[1] += len(random_data)
            
                
            if _ % 256 == 0:
                if time.time() - iter_speed[0] > 1:
                    iter_speed[0] = time.time()
                    iter_speed[2] = iter_speed[1]
                    iter_speed[1] = 0
                print(f"{round((_/blocks)*100, 1)}% Block #{_} on {round(iter_speed[2]/1024/1024, 2)}mb/s", end="\r", flush=1)

def main():
    disks = psutil.disk_partitions()

    if not disks:
        print("Try run as sudo, please.")
        return

    print("Avaliable partitions: \n")
    for i, disk in enumerate(disks):
        print(f"{i+1}. {disk.mountpoint} ({disk.device}, {disk.fstype.upper()})")

    choice = input("\nSelect partition: ")
    try:
        choice = int(choice)
        if 1 <= choice <= len(disks):
            selected_disk = disks[choice - 1].mountpoint
            
            print("Searching for /ssdtool...")
            test_file = selected_disk + "/ssdtool"
            if os.path.exists(test_file):
                with open(test_file, "rb") as t:
                    blocks = int.from_bytes(t.read(4), "big")
                if os.stat(test_file).st_size - 4 == blocks * 4096:
                    print(f"There is {blocks} blocks written here, all is confirmed...")
                    
                    if input("Read all of them? (Y/n) > ").lower() == "y":
                        scan_disk(selected_disk)
                        return
                else:
                    print("There is exist 'ssdtool' file but seems is corrupted, write it from scratch :/")
            
            if input("Read/Write (Y/n) > ").lower() == "y":
                scan_disk(selected_disk)
            else:
                print("Is {}MBytes free on selected partition".format(int(psutil.disk_usage(selected_disk).free/1024/1024)))
                sz = input("Enter a int of MEGABYTES to be tested (or ENTER to all free space): ")
                write_random_blocks(selected_disk, blocks=int(psutil.disk_usage(selected_disk).free / 4096)-1 if len(sz) == 0 else int((int(sz)*1024*1024)/4096))
                print("\nAll is OK. Now you can read all of them or do it later (i advice exactly that)..")
    except ValueError:
        return

if __name__ == "__main__":
    main()
