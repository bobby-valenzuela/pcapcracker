# pcap-cracker

__What this does__

1. Downloads HashCat (v5) and necessary utilities
2. Runs pcap-to-hccapx converter on all your pcap files.
3. Merges all hccapx files into one master file
4. Runs hashcast 5 against this master file

Clip of this in action [here](https://link.us1.storjshare.io/s/juouchkuithxm5u2idjbv5uv2uqq/clips/pcapcracker_demo.mp4)

__Notes:__
- Uses attack mode "2500" (superceded by 22000 in Hashcat v6 - [see here](https://hashcat.net/forum/thread-10253.html))
- Adds '-w 3 --hwmon-temp-abort=10' flags by default'
- Prints all cracked pcaps to stdout
- Prints failed attempts to stdout (and to it's own file as well)
  - Failed attempts denote a failure to __convert__ to pcap file(s) to hccapx ([see here for more info](https://hashcat.net/cap2hashcat/)).
  - __Per Hashcat__: For best results, avoid tools that strip or modify capture files, such as:
    - airodump-ng (with filter options)
    - besside-ng
    - wpaclean
    - old bettercap versions
    - old pwnagotchi versions
    - tshark (with filter options)
- The wordlist supplied is an extremely small sample wordlist. It's a slice of the original "rockyou" wordlist from Kali linux. A much larger wordlist should be used for best results. [Wordlists for download](https://weakpass.com/wordlist)

## Pre-requisites/Initial Config


- Python 3 to be installed
- 7z to be installed
  - `sudo apt update && sudo apt install --assume-yes p7zip-full`.
- Add your wordlist in working dir (see small sample wordlist provided) and name it 'wordlist.txt'.
- Place your pcap files in the 'pcaps' folder.

### Running the Program:
  - Windows (Powershell): `python .\pcapcracker.py`
  - Linux: `python3 pcapcracker.py`

### Flags/Arguments
- clean: Used to clean up downloaded files
  - `python3 pcapcracker.pl clean`
- turbo (TBD): Will enables a higher performance mode on Hashcat (uses more GPU power/raises temperature threshold before stalling)
  - Used by default. Adds these hashcat flags `-w 3 --hwmon-temp-abort=10`
- v2: Not functional yet. Only use at the moment is to download hashcat-legacy (for nostaliga)
- v6: Not functional yet.  Only use at the moment is to download hashcat v6. Uses different "Attack mode (22000)"


## Troubleshooting


### GPU Driver(s)

Check HashCat GPU Driver Requirements [Hashcat](https://hashcat.net/hashcat/)

__GPU Driver requirements:__
- AMD GPUs on Linux require "RadeonOpenCompute (ROCm)" Software Platform (3.1 or later)
- AMD GPUs on Windows require "AMD Radeon Adrenalin 2020 Edition" (20.2.2 or later)
- Intel CPUs require "OpenCL Runtime for Intel Core and Intel Xeon Processors" (16.1.1 or later)
- NVIDIA GPUs require "NVIDIA Driver" (440.64 or later) and "CUDA Toolkit" (9.0 or later)


Hashcat is pretty good at providing detailed warnings if GPU Driver requirements are not met:
```
 clGetPlatformIDs(): CL_PLATFORM_NOT_FOUND_KHR

# ATTENTION! No OpenCL-compatible, HIP-compatible or CUDA-compatible platform found.

# You are probably missing the OpenCL, CUDA or HIP runtime installation.

 * AMD GPUs on Linux require this driver:
   "AMD ROCm" (4.5 or later)
 * Intel CPUs require this runtime:
   "OpenCL Runtime for Intel Core and Intel Xeon Processors" (16.1.1 or later)
 * NVIDIA GPUs require this runtime and/or driver (both):
   "NVIDIA Driver" (440.64 or later)
   "CUDA Toolkit" (9.0 or later)
```


### ‘cannot execute binary file: Exec format error’ on Ubuntu
- Make sure you are on 64-bit arch
  - https://appuals.com/fix-cannot-execute-binary-file-exec-format-error-ubuntu/
