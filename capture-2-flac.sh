#!/bin/bash
# Take capture folder and Generate flac files 
input=""
output=""
extension="r16"
hifi=""
rfvideofreq=17897727
rfhififreq=14318181

usage () {
  echo "Usage: $(basename $0) [-d input directory] [-e extension]"
  echo
  echo "Options:"
  echo "-d, --directory    Input directory. This option is mandatory."
  echo "-o, --output       Output directory. This option is optional."
  echo "-e, --extension    Extension of the captured files, eg. r8, r16. Defaults to r16."
  echo "-v, --rfvideofreq  Sample rate of the video capture file. Defaults to 17897727."
  echo "-a, --rfhififreq   Sample rate of the HiFi capture file. Defaults to 14318181."
  echo "Sample rates are usually: 28MHz, 8-Bit = 28636000; 35MHz, 8-Bit = 35795000; 14.3MHz, 16-Bit = 14318181; 17.3MHz, 16-Bit = 17897727"
}

while [ "$1" != "" ]; do
  case $1 in
    -d | --directory )
      shift
      input=$1
      ;;
    -e | --extension )
          shift
      extension=$1
      ;; 
    -o | --output )
      shift
      output=$1
      ;;
    -v | --rfvideofreq )
      shift
      rfvideofreq=$1
      ;;
    -a | --rfhififreq )
      shift
      rfhififreq=$1
      ;;
    -h | --help )
      usage
      exit
      ;;
    * )
      usage
      exit 1
  esac
  shift
done

if [ "$input" = "" ]; then
  echo "Please specify an input"
  usage
  exit 1
fi

echo "Using directory: $input"
echo "File extension is: $extension"
if [ "$output" = "" ]; then
  echo "No output directory given, using input directory $input as output directory"
  output=$input
else
  echo "Output directory is $output"
fi

if [ ! -f $output"cap2flac.sh" ]; then
  echo "No previous shell script for processing found, creating one in $output called cap2flac.sh"
  echo "Commands will be added to the file, but not deleted. So do regular checks for old entries!"
  touch -f $output"cap2flac.sh"
  echo "#!/bin/bash" > $output"cap2flac.sh"
  chmod 0755 $output"cap2flac.sh"
  echo $output"cap2flac.sh"
fi

for file in `ls $input`
do
  s=${file##*.}
  input_stripped=${file%.$s}
  if [ "$s" = "$extension" ]; then
    if [ "$s" = "r8" ]; then
      hifi=${file##*_hif}
      if [ "$hifi" = "i.r8" ]; then
        echo "Found rf hifi capture $file"
        echo "Assuming 8 Bit Hifi audio rf at "$rfhififreq"Hz"
        echo "Adding file to queue in script"
        echo "# RF HiFi" >> $output"cap2flac.sh"
        echo "sox -r $rfhififreq -b 8 -c 1 -e unsigned -t raw $input$file -b 8 -r 6500000 -e unsigned -c 1 -t raw "$output$input_stripped"_6-5mhz.u8" >> $output"cap2flac.sh"
        echo "flac -V --best --sample-rate=6500 --sign=unsigned --channels=1 --endian=little --bps=8 --blocksize=65535 --lax -f "$output$input_stripped"_6-5mhz.u8 -o "$output$input_stripped"_6-5mhz.flac" >> $output"cap2flac.sh"
        echo ""
      else
        echo "Found rf video capture $file"
        echo "Assuming 8 Bit video rf at "$rfvideofreq"Hz"
        echo "Adding file to queue in script"
        echo "# RF Video" >> $output"cap2flac.sh"
        echo "sox -r $rfvideofreq -b 8 -c 1 -e unsigned -t raw $input$file -b 8 -r 16000000 -e unsigned -c 1 -t raw "$output$input_stripped"_16mhz.u8 sinc -n 2500 0-7650000"  >> $output"cap2flac.sh"
        echo "flac -V --best --sample-rate=16000 --sign=unsigned --channels=1 --endian=little --bps=8 --blocksize=65535 --lax -f "$output$input_stripped"_16mhz.u8 -o "$output$input_stripped"_16mhz.flac" >> $output"cap2flac.sh"
        echo ""
      fi
    fi
    if [ "$s" = "r16" ]; then
      hifi=${file##*_hif}
      if [ "$hifi" = "i.r16" ]; then
        echo "Found rf hifi capture $file"
        echo "Assuming 16 Bit Hifi audio rf at "$rfhififreq"Hz"
        echo "Adding file to queue in script"
        echo "# RF HiFi" >> $output"cap2flac.sh"
        echo "sox -r $rfhififreq -b 16 -c 1 -e unsigned -t raw $input$file -b 8 -r 6500000 -e unsigned -c 1 -t raw "$output$input_stripped"_6-5mhz.u8" >> $output"cap2flac.sh"
        echo "flac -V --best --sample-rate=6500 --sign=unsigned --channels=1 --endian=little --bps=8 --blocksize=65535 --lax -f "$output$input_stripped"_6-5mhz.u8 -o "$output$input_stripped"_6-5mhz.flac" >> $output"cap2flac.sh"
        echo ""
      else
        echo "Found rf video capture $file"
        echo "Assuming 16 Bit video rf at "$rfvideofreq"Hz"
        echo "Adding file to queue in script"
        echo "# RF Video" >> $output"cap2flac.sh"
        echo "sox -r $rfvideofreq -b 16 -c 1 -e unsigned -t raw $input$file -b 8 -r 16000000 -e unsigned -c 1 -t raw "$output$input_stripped"_16mhz.u8 sinc -n 2500 0-7650000"  >> $output"cap2flac.sh"
        echo "flac -V --best --sample-rate=16000 --sign=unsigned --channels=1 --endian=little --bps=8 --blocksize=65535 --lax -f "$output$input_stripped"_16mhz.u8 -o "$output$input_stripped"_16mhz.flac" >> $output"cap2flac.sh"
        echo ""
      fi
    fi
  fi
done

