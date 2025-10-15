# vhs-decode-tools
Tools for the automation of capture preprocessing, decoding and video generating. Also for restoration of captured content

# Automation
## captures-2-video_json.py
Script for automation of vhs-decoding, hifi-decoding, teletext-decoding, audio align, muxing and cleanup  
Dependencies: json config file  
Optional dependencies: rewolfs VhsDecodeAutoAudioAlign, sox, vhs-teletext, tbc-vbicutter.py  

### captures-2-video.json
*audioAlignSoftware:* Link to the audio align software  
*teleTextSoftware:* Name of vhs-teletext. Should simply be teletext  
*soxSoftware:* usually sox  
*rfCaptureVideo:* location of the rf video capture files (folder)  
*captureAudio:* location of the linear audio capture files (folder)  
*rfCaptureHifi:* location of the rf audio capture files (folder)  
*decodeOutDir:* folder where the tbc files will be written  
*jsonBackupDir:* folder where a backup of the tbc json files will be copied to  
*decodeParams:* Command line parameters of vhs-decode  
*hifiDecodeParams:* Command line parameters of hifi-decode  
*colorSystem:* video systems like PAL, NTSC, MESECAM etc.  
*decodeTeletext:* true, or false. If true, vhs-teletext will be used to deconvolve teletext from tbc files. If false, a tbc file, containing only the vbi header, will be written, which can be fed to vhs-teletext (*_vbi.tbc)  
*decodePattern:* pattern installed in vhs-teletext, usually vhs, betamax. See docu of vhs-teletext. Additional patterns can be downloaded from my vhs-teletext-training-files repository  
*audioAligning:* First part is for linear audio config, second part is for hifi audio config  
*filePattern:* Regex style pattern to filter for the correct files in the capture directories  


# Old stuff
## capture-2-flac.sh
This script does bandwith limiting and flac encoding of 16 and 8-Bit RF Video and RF HiFi captures. Bitrate and samplerate can be selected through parameters.
* RF video will be limited to 16MHz, 8 Bit.
* RF HiFi will be limited to 6.5MHz, 8 Bit.

Input file expected for video *.r16 or *.r8 \
Input file expected for HiFi *_hifi.r16 or *_hifi.r8

Just run it with an input and output folder as parameter, optional parameters can be also specified. This script then collects all capture files and creates a bash script **cap2flac.sh** in the output folder, holding all commands ready for converting. Just run that new script and converting begins.

## capture-2-decode.sh
Takes a whole folder of capture files and decodes them using vhs-decode. \
Input-, outputfolder have to be given. Also path and executable of vhs-decode. \
This script then collects all capture files and creates a bash script **cap2decode.sh** in the output folder, holding all commands ready for decoding. Just run that new script and decoding begins.

# Restauration
This is an attempt to restore quality of the captured and decoded content. vhs-decode itself already does a great job in terms of quality, but it can be enhanced further. That is done with the help of AI models I trained on VHS PAL and MESECAM content.
## Workflow
1. Denoise the content. I use neat-video, but other methods might work as well
2. Stack fields on top of each other
3. Use AI magic
4. Unstack, deinterlace, crop and resize the content

### Stacking fields
A ffmpeg command is used in order to unweave and stack the fields on top of each other

```ffmpeg -i input_video.mkv -filter_complex "[0]il=l=d:c=d,split[o][e];[o]crop=iw:ih/2:0:0[odd];[e]crop=iw:ih/2:0:ih/2[even];[odd][even]vstack" -c:v ffv1 -coder 1 -context 1 -g 25 -level 3 -slices 16 -slicecrc 1 -top 1 output_stacked.mkv```
### AI magic
There are two so called Compact models available, 1x_vhs-restore_secam_compact_80k.pth and 1x_vhs-restore_pal_compact_80k.pth. These can be loaded into a software called chaiNNer https://github.com/chaiNNer-org/chaiNNer . Using an iterator node it can iterate through image sequences or through a video. The Compact models are pretty fast. On a RTX3060 5fps can be achieved.
The output is either saved as an image sequence or as video.

### Preprocessing
This can be fed into the stackedfields-2-deinterlace-and-tweak.avs script which reinterlaces,tweaks, deinterlaces, crops and resizes the content.

### Further do, faces
After theses steps an optional face restore can be applied, again by using the chaiNNer tool. It has an option for face restore, which works pretty decent already. The necessary GFPGAN model is linked on the chaiNNer github page
