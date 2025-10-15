import os
import argparse
import json


# Infos
# Creates a bash script containing all the processing steps for each rfcapture in a folder
# To build in a pause in the bash script use: read -n1 -r -p "Press any key to continue..." key

def loadConfig(jsonconfig: str):
    #script_dir = os.path.dirname(os.path.abspath(__file__)) + "/"
    if os.path.isfile(jsonconfig):
        with open(jsonconfig, 'r') as file:
            data = json.load(file)
            if data:
                print("\n")                    
            else:
                print("Abort!")
                exit(2)
    else:
        print("Could not find any config file, Abort!")
        exit(2)

    return data

# Function audioalign wrapper
def wrap_alignaudio(aal_sw: str,aal_source: str,aal_dest: str,aal_bps: int,aal_channels: int,aal_rate_hz_in: int, aal_rate_hz_out: int, aal_suffix: str):
    aalstring = (
        "  sox -D \\\n"
        "  \"{}\" \\\n  -t raw -b {} -c {} -L -e unsigned-integer - \\\n".format(aal_source,aal_bps,aal_channels) +
        "  | mono \"{}\" stream-align \\\n".format(aal_sw) +
        "  --sample-size-bytes $(( {} / 8 * {} )) --stream-sample-rate-hz {} \\\n".format(aal_bps,aal_channels,aal_rate_hz_in) +
        "  --json \"{}.tbc.json\" | sox -D \\\n".format(aal_dest) +
        " -t raw -r {} -b {} -c {} -L -e unsigned-integer - \\\n".format(aal_rate_hz_in,aal_bps,aal_channels)
    )
    if aal_rate_hz_out == False:
        aalstring += "  \"{}{}.flac\" remix 1 2\n\n".format(aal_dest,aal_suffix)
    else:
        aalstring += "  \"{}{}.flac\" rate {} remix 1 2\n\n".format(aal_dest,aal_suffix,aal_rate_hz_out)
    
    return aalstring

# Function teletext decode
def wrap_ttxdecode(muxvideo: str):
    ttxstring = (
        "  # Teletext recovery\n"
        "  teletext deconvolve \\\n"
    )
    ttxstring += (
            "  -c tbc -f vhs \\\n"
    )
    ttxstring += (
        "  {}.tbc > \\\n".format(muxvideo) +
        "  {}.t42 \n".format(muxvideo) +
        "  teletext squash \\\n"
        "  {}.t42 > \\\n".format(muxvideo) +
        "  {}_sqsh.t42 \n".format(muxvideo)
    )
    return ttxstring

# Function Mux wrapper
def wrap_muxing(muxtool: str, muxvideo: str, muxaudio: str, muxaudio2: str):
    muxstring = "  {} \\\n  \"{}.tbc\"".format(muxtool,muxvideo)
    if muxaudio != False and muxaudio2 != False:
        muxstring += " \\\n"
        muxstring += "  --audio-track \"{}\" \\\n".format(muxaudio)
        muxstring += "  --audio-track \"{}\" \n\n".format(muxaudio2)
    elif muxaudio != False:
        muxstring += " \\\n"
        muxstring += "  --audio-track \"{}\" \n\n".format(muxaudio)

    return muxstring

# Function secam decoder wrapper
def wrap_secamdecode(s_decoder: str, s_workdir: str, s_decfile: str):
    decstring = (
        "# Decoding SECAM color into {}_i0.bin file\n".format(s_decfile) + 
        "# if color is pink, manually rerun this part activating --invert-crcb 1\n"
        "{} \\\n --inputdir {}/ --videofile {} --outputdir /home/workhorse/Videos/\n".format(s_decoder,s_workdir,s_decfile)
    )
    return decstring

# Function file operations
def cleanup(cu_muxvideo: str,cu_backupdir: str):
    cupstring = (
        "  if [ -f \"{}.mkv\" ]; then\n".format(cu_muxvideo) +
        "    actualsize=$(wc -c <\"{}.mkv\")\n".format(cu_muxvideo) +
        "    if [ $actualsize -ge 124000000 ]; then\n"
        "      echo size of videofile is over 124000000 bytes, deleteing tbcs\n"
        "      rm {}.tbc\n".format(cu_muxvideo) +
        "      rm {}_chroma.tbc\n".format(cu_muxvideo) +
        "      rm {}.log\n".format(cu_muxvideo) +
        #"        if [ -f \"{}.wav\" ]; then\n".format(cu_muxvideo) + 
        #"            rm {}.wav\n".format(cu_muxvideo) + 
        #"        fi\n"
        ""
    )
    if os.path.isdir(cu_backupdir + "/json/"):
        cupstring += (
            "        mv {}.tbc.json {}/json/\n".format(cu_muxvideo,cu_backupdir)
        )
    cupstring += (
        "    fi\n"
        "  fi\n"
    )
    return cupstring

parser = argparse.ArgumentParser(description='Automated vhs-decode of captures to video')

parser.add_argument(
    "--tapespeed",
    type=str.upper,
    dest="tapespeed",
    choices=["SP", "LP", "EP"],
    default="SP",
    help="Tapespeed. LP and EP use different filtering.",
)

parser.add_argument(
    "--config",
    type=str,
    dest="config",
    metavar="Config in JSON format",
    default="None",
    help="Config in JSON format which holds input and output folders and processing patterns and parameters",
)

args = parser.parse_args()
data = loadConfig(args.config)

capturedir = data['directoryPresets'][0]['rfCaptureVideo']
workdir = data['directoryPresets'][0]['decodeOutDir']
audiodir = data['directoryPresets'][0]['captureAudio']
hifidir = data['directoryPresets'][0]['rfCaptureHifi']
tapespeed = args.tapespeed
capturetype = data['directoryPresets'][0]['suffixRfCaptureVideo']
backupdir = data['directoryPresets'][0]['jsonBackupDir']
colorsystem=data['colorSystem']
teletext=data['teletextDecoding'][0]['decodeTeletext']
teletextpattern= data['teletextDecoding'][0]['decodePattern']
script_dir = os.path.dirname(os.path.abspath(__file__)) + "/"

decodeparams = data['decodeParams']
hifidecodeparams = data['hifiDecodeParams']

if colorsystem != "MESECAM" and colorsystem != "SECAM":
    decodeparams += " --recheck_phase"
if tapespeed != "SP":
    print("TEST")
    #decodeparams += " --clamp --tape_format VHSHQ"

decodeparams += " --system " + colorsystem

muxtool = "tbc-video-export"
audioalign = True
audioalign_sw = data['softwarePresets'][0]['audioAlignSoftware']
secamdecoder = "/usr/bin/python3 -u  /home/workhorse/git/secam-tbc-2-yuv/secam2yuv_cli.py"

if not os.path.isdir(capturedir):
    print(capturedir + " is not a valid video input folder")
    exit(2)

if not os.path.isdir(workdir):
    print(workdir + " is not a valid work output folder")
    exit(2)

vhsdecode="vhs-decode"
bashcontent = "#!/bin/bash\n"

print("Capture folder: {}".format(capturedir))
print("Work folder: {}".format(workdir))
print("vhs-decode: {}/vhs-decode".format(vhsdecode))
if os.path.isdir(audiodir):
    print("audio-directory: {}".format(audiodir))
if os.path.isdir(hifidir):
    print("hifi-directory: {}".format(hifidir))
for capturefile in sorted(os.listdir(capturedir)):
    if capturefile.endswith(".{}".format(capturetype)):
        if data['filePattern'][0]['rfCaptureVideo'] in capturefile:
            hifi = False
            audio = False

            print("Adding {} to processing".format(capturefile))
            decoded_file = capturefile.replace(data['filePattern'][0]['rfCaptureVideo'] + "." + capturetype,"")
            audio_file = decoded_file + data['filePattern'][0]['linearCaptureAudio'] + "." + data['directoryPresets'][0]['suffixCaptureAudio']
            hifi_file = decoded_file + data['filePattern'][0]['rfCaptureHifi'] + "." + data['directoryPresets'][0]['suffxRfCaptureHifi']
            muxvideo = "{}/{}".format(workdir,decoded_file + "")
            # Checking for presence of hifi and audio folder and set hifi and audio file
            if os.path.isdir(audiodir):
                audiofile = "{}/{}".format(audiodir,audio_file) 
            if os.path.isdir(hifidir):
                hififile = "{}/{}".format(hifidir,hifi_file)
            # Generating vhs decode string for the capture file
            bashcontent += "if [ ! -f \"{}/{}.job\" ]; then\n".format(workdir,decoded_file) # Check if job is already running or done
            bashcontent += "  touch -f \"{}/{}.job\"\n".format(workdir,decoded_file) # Create a file, that shows, that the job is already running or done
            bashcontent += "  # VHS-decode of capture\n"

            bashcontent += "  {} \\\n  \"{}/{}\" \\\n  \"{}\"  \\\n  {}\n".format(vhsdecode,capturedir,capturefile,muxvideo,decodeparams)
            bashcontent += "\n"
            #bashcontent += "fi\n"
            if teletext == True:
                bashcontent += wrap_ttxdecode(muxvideo)
                bashcontent += "\n"
            else:
                bashcontent += (
                    "  # Saving VBI to new TBC file for later processing\n"
                    "  python3 \"" + script_dir + "tbc-vbicutter.py\" \\\n"
                    "  \"" + muxvideo + ".tbc\" \\\n"
                    "  \"" + muxvideo + "_vbi.tbc\"\n\n"
                )
            # If source is SECAM run the GNURadio graph
            if colorsystem == "MESECAM" or colorsystem == "SECAM":
                bashcontent += wrap_secamdecode(secamdecoder,workdir,decoded_file)
            
            if os.path.isfile(hififile):
                bashcontent += (
                    "  # Decode HiFi Audio\n"
                    "  ffmpeg -i \\\n "
                    "  \"{}\" \\\n".format(hififile) +
                    "  -f s16le -acodec pcm_s16le - | hifi-decode \\\n"
                    "  {}  - \\\n".format(hifidecodeparams) +
                    "  \"{}/hifi/{}_hifi.flac\"\n\n".format(workdir,decoded_file)
                )


            # If given rf audio files exist align audio, else only say that audio exists
            if os.path.isfile(hififile) and audioalign == True:
                bashcontent += "  # Align HiFi audio\n"
                bashcontent += "  if [ -f \"{}/{}_hifi.flac\" ]; then\n".format(workdir,decoded_file)
                bashcontent += wrap_alignaudio(
                    audioalign_sw,
                    workdir + decoded_file + "_hifi.flac",
                    muxvideo,
                    data['audioAligning'][1]['audioBitrates'],
                    data['audioAligning'][1]['audioChannels'],
                    data['audioAligning'][1]['audioSamplerates'],
                    False,
                    "_hifi_al"
                    )
                bashcontent += "  fi\n\n"
                hifi = True
            elif os.path.isfile(hififile) and audioalign == False:
                hifi = True

            if os.path.isfile(audiofile) and audioalign == True:
                bashcontent += "  # Align linear audio\n"
                # software for alignment, audiofile, video to mux with, bits per sample, channels, rate in hz
                bashcontent += wrap_alignaudio(
                    audioalign_sw,
                    audiofile,
                    muxvideo,
                    data['audioAligning'][0]['audioBitrates'],
                    data['audioAligning'][0]['audioChannels'],
                    data['audioAligning'][0]['audioSamplerates'],
                    False,
                    "_a"
                    )
                audio = True
            elif os.path.isfile(audiofile) and audioalign == False:
                audio = True

            if audioalign == True:
                if hifi == True:
                    # Mux with aligned hifi audio
                    bashcontent += "  # Mux video with aligned hifi audio\n"
                    bashcontent += wrap_muxing(muxtool,muxvideo,muxvideo + "_hifi_al.flac",muxvideo + "_a.flac")
                elif audio == True:
                    # Muxing with aligned linear audio
                    bashcontent += "  # Mux video with aligned audio\n"
                    bashcontent += wrap_muxing(muxtool,muxvideo,muxvideo + "_a.flac",False)
                else:
                    # No audio will be muxed, only video will be generated
                    bashcontent += "  # Only generating video\n"
                    bashcontent += wrap_muxing(muxtool,muxvideo,False,False)
            else:
                if hifi == True:
                    # Mux with hifi audio
                    bashcontent += "  # Mux video with hifi audio\n"
                    bashcontent += wrap_muxing(muxtool,muxvideo,workdir + decoded_file + "_hifi.flac",audiofile)
                elif audio == True:
                    # Muxing with linear audio
                    bashcontent += "  # Mux video with audio\n"
                    bashcontent += wrap_muxing(muxtool,muxvideo,audiofile,False)
                else:
                    # No audio will be muxed, only video will be generated
                    bashcontent += "  # Only generating video\n"
                    bashcontent += wrap_muxing(muxtool,muxvideo,False,False)

                    
            if colorsystem != "MESECAM" and colorsystem != "SECAM":
                bashcontent += "  # Deleting tbc files if video was properly generated\n"
                bashcontent += cleanup(muxvideo,backupdir)
            bashcontent += "fi\n\n"

bashout = open(workdir + '/capture2decode_json.sh','w')
bashout.write(bashcontent)
bashout.close()
