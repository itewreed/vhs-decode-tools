# vhs-decode_automation-tools
Tools for the automation of capture preprocessing, decoding and video generating.

# capture-2-flac.sh
This script does bandwith limiting and flac encoding of 16 and 8-Bit RF Video and RF HiFi captures. Bitrate and samplerate can be selected through parameters.
* RF video will be limited to 16MHz, 8 Bit.
* RF HiFi will be limited to 6.5MHz, 8 Bit.

Input file expected for video *.r16 or *.r8 \
Input file expected for HiFi *_hifi.r16 or *_hifi.r8

Just run it with an input and output folder as parameter, optional parameters can be also specified. This script then collects all capture files and creates a bash script **cap2flac.sh** in the output folder, holding all commands ready for converting. Just run that new script and converting begins.

# capture-2-decode.sh
Takes a whole folder of capture files and decodes them using vhs-decode. \
Input-, outputfolder have to be given. Also path and executable of vhs-decode. \
This script then collects all capture files and creates a bash script **cap2decode.sh** in the output folder, holding all commands ready for decoding. Just run that new script and decoding begins.
