#!/usr/bin/python3

import os,sys,subprocess
from re import search as reg

pwd = os.path.dirname(os.path.abspath(__file__))
args = sys.argv

# Arguments

version = 'v2' if 'v2' in args else 'v6' if 'v6' in args else 'v5' 
utils_version = 'v1' 
attack_mode = '-m 22000' if version == 'v6' else '-m 2500' 
turbo_enabled = True

download_link = {
    "hashcat": {
        "v2" : "https://github.com/hashcat/hashcat-legacy/archive/refs/tags/2.00.tar.gz",
        "v5" : "https://hashcat.net/files/hashcat-5.1.0.7z",
        "v6" : "https://hashcat.net/files/hashcat-6.2.5.7z"
    },
    "hashcat_utils":{
        "v1": "https://github.com/hashcat/hashcat-utils/releases/download/v1.9/hashcat-utils-1.9.7z",
        "v2": "...."
    }
}

hashcat_link = download_link["hashcat"][version]
hashcat_utils_link = download_link["hashcat_utils"][utils_version]

# sys.platform --> linux, win32, Darwin
host_os = 'win' if sys.platform == 'win32' else 'lin' 
slash = '\\' if host_os == 'win' else '/'

hide_output = '> $null 2>&1' if host_os == 'win' else '> /dev/null 2>&1' 
# sys.exit()

def psExec(cmd):
    """Useful to be explicit that powershell should execute these commands"""
    completed = subprocess.run(["powershell", "-Command", cmd], capture_output=False)

def psExecSilent(cmd):
    """Save response instead or printing to stdout"""
    completed = subprocess.run(["powershell", "-Command", cmd], capture_output=True)
    return completed

def cleanUp():
    print('Cleaning...')
    runCmd(f'rm -r hashcat* {hide_output}')
    runCmd(f'rm -r failedtoconvert.txt {hide_output}')
    print('Files all cleaned up!')

runCmd =  lambda cm : psExec(cm) if host_os == 'win' else os.system(cm)
runCmdSilent =  lambda cm : psExecSilent(f"{cm}") if host_os == 'win' else os.system(f"{cm} {hide_output}")

# Move to working dir if not in
os.system(f'cd {pwd}')
# First let's make sure our 'pcaps' folder exists
pcaps_folder_exists = os.path.exists(f'pcaps')

# Check if we're just cleaning up
if 'clean' in args:
    cleanUp()
    sys.exit()

if (pcaps_folder_exists == False):

    runCmd(f'mkdir pcaps')
    print('Directory \'pcaps\' is empty. Nothing to convert')

elif not os.listdir(f'{pwd}/pcaps'):
        
    print('Directory \'pcaps\' is empty. Nothing to convert')

else:

    def download_hashcat():
        """Downloads zip, extracts, deletes zip, renames folder"""
        
        print(f"Downloading Hashcat {version} and necessary utilities...")
        
        if (version == 'v2'):
            runCmdSilent(f'wget {hashcat_link} -O hashcat.tar.gz')
            runCmdSilent(f'tar -xzf hashcat.tar.gz')
            runCmdSilent(f'rm hashcat.tar.gz')
        else:
            runCmdSilent(f'wget {hashcat_link} -O hashcat.7z')
            runCmdSilent(f'7z x hashcat.7z')
            runCmdSilent(f'rm hashcat.7z')

        runCmdSilent(f'mv hashcat* hashcat')


        if(not os.path.exists(f'.hashcat_info')):
        
            with open('.hashcat_info',mode='w') as f:
                f.write(f'hashcat_version_number_{version}')

    def download_hashcat_utils():
        """Downloads zip, extracts, deletes zip, renames folder"""
        runCmdSilent(f'wget {hashcat_utils_link} -O hashcat-utils.7z')
        runCmdSilent(f'7z x hashcat-utils.7z')
        runCmdSilent(f'rm hashcat-utils.7z')
        runCmdSilent(f'mv hashcat-utils* hashcat_utils')

    def need_to_download_files():
        # See if we've alread downloaded these files already
        

        if (os.path.isfile('.hashcat_info') and os.stat(".hashcat_info").st_size > 0):
            
            with open(".hashcat_info") as f:
        
                content = f.readlines() 
                last_version = content[0].strip() 
                current_version = f"hashcat_version_number_{version}"
                version_match_found = reg(current_version,last_version)

                if (version_match_found != None):
                    print(f"Files for {version} found! Proceeding to next step.")
                    return 0
            
            f.close()

            print(f"Files for {version} not found! Preparing to download...")

            if(os.path.isfile('.hashcat_info')):
                runCmd(f'rm .hashcat_info')
            return 1
        else:
            print(f"Files for {version} not found! Preparing to download...")
            
            if(os.path.isfile('.hashcat_info')):
                runCmd(f'rm .hashcat_info')
            return 1

    need_to_download_files = need_to_download_files()

    # Check for hashcat/hashcat_utils dir - if not download and extract
    no_hashcat_folder_exists = not os.path.exists(f'hashcat') or not os.listdir(f'hashcat')
    no_hashcat_utils_folder_exists = not os.path.exists(f'hashcat_utils') or not os.listdir(f'hashcat_utils')

    if ( no_hashcat_folder_exists or no_hashcat_utils_folder_exists) and need_to_download_files == 0:
            
        need_to_download_files = 1
        
    if( need_to_download_files == 1 ):
        cleanUp()
        download_hashcat()
        download_hashcat_utils()
    else:
        runCmd(f'rm -r failedtoconvert.txt {hide_output}')
        
    # Convert all .cap files
    for file in os.listdir(f'pcaps'):
        
        if file.endswith(".pcap"):

            new_filename =  file.replace('.pcap', '.hccapx')

            # Run Converter Tool
            if(host_os == 'win'):
                convert_out = psExecSilent(f'.\hashcat_utils\\bin\\cap2hccapx.exe .\pcaps\\{file} {new_filename}') 
                std_out = f'{convert_out}'.strip()
            else:
                # Using os.popen() to get save stdout into variable
                reponse = os.popen(f'hashcat_utils/bin/cap2hccapx.bin pcaps/{file} {new_filename}')
                std_out = reponse.read().strip()

            # If unable to convert - add to file
            if('Written 0 WPA' in std_out):
                
                runCmd(f'echo "{file}" >> failedtoconvert.txt; rm {new_filename}')

    # Merge all files
    if(host_os == 'win'):
        convert_exec = psExec(f'cmd.exe /c copy /b *.hccapx multi.hccapx; mv multi.hccapx multi.hccapxtemp; rm *.hccapx; mv multi.hccapxtemp multi.hccapx ;')
    else:
        runCmd(f'cat *.hccapx > multi.hccapx')

    if(turbo_enabled == True):
        additional_flags = '-w 3 --hwmon-temp-abort=100'
    else:
        additional_flags = ''

    # ===== Now call hashcat to do the cracking =====
    if(host_os == 'win'):
        crack_exec = psExec(f'cd .\hashcat\; .\hashcat64.exe -m 2500 ..\multi.hccapx ..\wordlist.txt {additional_flags} ; cd ..\\')
    else:
        runCmd(f'hashcat/hashcat64.bin {attack_mode} multi.hccapx wordlist.txt {additional_flags}')

    # Remove any lingering hccapx files
    runCmd(f'rm *.hccapx')

    # Print contents of potfile
    if (not os.path.isfile(f'hashcat{slash}hashcat.potfile') or os.stat(f"hashcat{slash}hashcat.potfile").st_size == 0):
        print("No cracked pcaps to display :(")
    else:
        # Display cracked pcaps 
        print("\n\n ===== Your cracked pcaps =====")
        runCmd(f'cat hashcat/hashcat.potfile > crackedpcaps.txt')
        runCmd(f'cat hashcat/hashcat.potfile')

    # Print any failed attempts to stdout
    if (os.path.isfile('failedtoconvert.txt') and os.stat("failedtoconvert.txt").st_size > 0):
        
        print("\n\n ===== Failed Attempts =====")

        with open("failedtoconvert.txt") as f:
        
            content = f.readlines()
    
            for i in range(0,len(content)):
                print(content[i].strip())
        
        print("\nDo not clean up the cap / pcap file (e.g. with wpaclean), as this will remove useful and important frames from the dump file.\nDo not use filtering options while collecting WiFi traffic.\n")

    elif(os.stat("failedtoconvert.txt").st_size == 0):
        runCmd('rm failedtoconvert.txt')
    else:
        # Display cracked pcaps 
        print("\n\n ===== Your cracked pcaps =====")
        runCmd(f'cat hashcat/hashcat.potfile > crackedpcaps.txt')
        runCmd(f'cat hashcat/hashcat.potfile')





# WORDLIST MUST BE SAVED HERE AS wordlist.txt
# p7zip to be installed!
    # $ sudo apt update && sudo apt install --assume-yes p7zip-full #Ubuntu and Debian
    # 7z x ~/archive.7z


# cat: multi.hccapx: input file is output file
# hashcat (v6.2.5) starting



# - [ OpenCL Device Types ] -

#   # | Device Type
# ===+=============
#   1 | CPU
#   2 | GPU
#   3 | FPGA, DSP, Co-Processor

# sudo apt install hashcat

# clGetPlatformIDs(): CL_PLATFORM_NOT_FOUND_KHR

# ATTENTION! No OpenCL-compatible, HIP-compatible or CUDA-compatible platform found.

# You are probably missing the OpenCL, CUDA or HIP runtime installation.

# * AMD GPUs on Linux require this driver:
#   "AMD ROCm" (4.5 or later)
# * Intel CPUs require this runtime:
#   "OpenCL Runtime for Intel Core and Intel Xeon Processors" (16.1.1 or later)
# * NVIDIA GPUs require this runtime and/or driver (both):
#   "NVIDIA Driver" (440.64 or later)
#   "CUDA Toolkit" (9.0 or later)

# Started: Mon Mar 14 15:08:42 2022
# Stopped: Mon Mar 14 15:08:42 2022

# https://github.com/intel/compute-runtime/blob/master/opencl/doc/DISTRIBUTIONS.md

# GPU Driver requirements:
    # AMD GPUs on Linux require "RadeonOpenCompute (ROCm)" Software Platform (3.1 or later)
    # AMD GPUs on Windows require "AMD Radeon Adrenalin 2020 Edition" (20.2.2 or later)
    # Intel CPUs require "OpenCL Runtime for Intel Core and Intel Xeon Processors" (16.1.1 or later)
    # NVIDIA GPUs require "NVIDIA Driver" (440.64 or later) and "CUDA Toolkit" (9.0 or later)


# How to Fix ‘cannot execute binary file: Exec format error’ on Ubuntu
    # Make sure you are on 64-bit arch
    # https://appuals.com/fix-cannot-execute-binary-file-exec-format-error-ubuntu/


