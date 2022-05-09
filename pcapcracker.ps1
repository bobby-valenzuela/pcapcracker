Write-Output "Checking for necessary files..."


###### Run checks first (Guard clauses)

# Check for pcap files
if ( -not ( Test-Path .\pcaps ) -or -not ( Test-Path .\pcaps\*.pcap ) ){

    Write-Output "Pcap files not found. Please pcap files to 'pcaps/'"
    Exit

}

# Check for wordlist
if ( -not ( Test-Path .\wordlist.txt ) ){

    Write-Output "Wordlist not found. Please add a wordlist named 'wordlist.txt'"
    Exit

}

Write-Output "Necessary files found.`n"

$additional_flags = $false

if ( "$($args[0])" -eq 'turbo') {
    
    $additional_flags = $true
    Write-Output "Running in high-performace mode.`n`n"
}
elseif ( "$($args[0])" -eq '--show' -or "$($args[0])" -eq 'show' ) {
    Write-Output "==== Successfull cracks ====`n"
    Get-Content .\successfull_cracks.txt    
    Write-Output "`n"
    Exit
}
elseif ( "$($args[0])" -ne '' ) {
    
    Write-Output "`n'$($args[0])' is not a recognized argument. Running in normal mode. To run in high-performance mode use 'turbo' flag.`n`n"

}

###### Action the download/installaiton of dependencies

Write-Output "Checking for dependencies...`n"

# Download 7Zip module
Install-PackageProvider -Name NuGet -MinimumVersion 2.8.5.201 -Force > $null 2>&1
Install-Module 7Zip4PowerShell -Scope CurrentUser -Force > $null 2>&1

# Check for hashcat dir
if ( -not ( Test-Path .\hashcat-5.1.0 ) ){
    
    Write-Output "Downloading hashcat..."
    
    # Download Hashcat and Extract
    Invoke-WebRequest https://hashcat.net/files/hashcat-5.1.0.7z -O hashcat.7z
    Expand-7Zip -ArchiveFileName .\hashcat.7z -TargetPath .\
    Remove-Item hashcat.7z
    
    Write-Output "Hashcat Downloaded."
}

# Check for hashcat utils dir
if ( -not ( Test-Path .\hashcat-utils-1.9 ) ){
    
    Write-Output "Downloading hashcat utilities..."
    
    # Download Hashcat Utils and Extract
    Invoke-WebRequest https://github.com/hashcat/hashcat-utils/releases/download/v1.9/hashcat-utils-1.9.7z -O hashcat-utils.7z
    Expand-7Zip -ArchiveFileName .\hashcat-utils.7z -TargetPath .\
    Remove-Item hashcat-utils.7z
    
    Write-Output "Hashcat Utilities Downloaded."
}

# Convert pcap files to hccapx
Write-Output "Converting pcap files..."

Get-ChildItem ".\pcaps" -Filter *.pcap | 
Foreach-Object {
    
    $updated_name="$_".Replace(".pcap",".hccapx") 
    $conversion_result = & .\hashcat-utils-1.9\bin\cap2hccapx.exe .\pcaps\"$_" .\pcaps\$updated_name
    
    # If no handshakes acquired from this pcap, remove converted file and log
    if ($conversion_result -like '*Written 0 WPA*') { 
        Write-Output "$_" >> conversion_failed.txt
        Remove-Item .\pcaps\$updated_name
    }else{
        Write-Output "$_" >> conversion_successfull.txt
    }
    
    
}

# Concat files
cmd.exe /c copy /b .\pcaps\*.hccapx .\multi_2500.hccapx

# Run hccapx against hashcat
Set-Location .\hashcat-5.1.0
if ( $additional_flags ){
    .\hashcat64.exe -m 2500 ..\multi_2500.hccapx ..\wordlist.txt -w 3 --hwmon-temp-abort=100
}
else{
    .\hashcat64.exe -m 2500 ..\multi_2500.hccapx ..\wordlist.txt 
}

# Remove hccapx files
Remove-Item ..\multi_2500.hccapx
Get-ChildItem -Path ..\pcaps\ -File -Filter *.hccapx | Remove-Item -Force

# Cleanup files from past run
if ( Test-Path ..\successfull_cracks.txt  ){
    Remove-Item ..\successfull_cracks.txt
}
if ( Test-Path ..\conversion_successfull.txt  ){
    Remove-Item ..\conversion_successfull.txt
}
if ( Test-Path ..\conversion_failed.txt  ){
    Remove-Item ..\conversion_failed.txt
}

$count_cracked = ((Get-Content '.\hashcat.potfile') | Measure-Object -Line).Lines 
Write-Output "`n$count_cracked handshakes cracked. View your 'successfull_cracks.txt' file for a full list.`n";Set-Location ..\

if ( $count_cracked > 0 ) {
    ( Get-Content .\hashcat-5.1.0\hashcat.potfile ) > .\hashcat-5.1.0\successfull_cracks.txt
    
}

