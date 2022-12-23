# vhs-decode_automation-tools
Tools for the automation of capture preprocessing, decoding and video generating.

# capture-2-flac.sh
This script does bandwith limiting and flac encoding of (16bit) RF Video and RF HiFi captures.
* RF video will be limited to 16MHz, 8 Bit. Input is expected to be 17.89MHz (10cxadc3: tenbit 1, tenxfsc 1)
* RF HiFi will be limited to 6.5MHz, 8 Bit. Input is expected to be 14.32MHz (10cxadc: tenbit 1, tenxfsc 0)

Input file expected for video *.r16
Input file expected for HiFi *_hifi.r16

Just run it with an input and output folder specified. A bash script **cap2flac.sh** will be created in the output folder holding all commands ready for converting. Just run that new script and converting begins.
