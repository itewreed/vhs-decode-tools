#!/bin/sh
# Take folder with flac files and generate decode script
input=""
output=""
syntax=" --frequency 16.000000 --ct --nld --threads 4 --recheck_phase"
#syntax=" --10cxadc3 -nld --threads 4 --recheck_phase"
extension="flac"
system="--system PAL"
swdecoder=""
decscript="cap2decode.sh"

usage () {
  echo "Usage: $(basename $0) [-d input directory] [-o output directory] [-s decodesoftware]"
  echo
  echo "Options:"
  echo "-d, --indir       Input directory. This option is mandatory."
  echo "-o, --outdir      Output directory. This option is mandatory."
  echo "-s, --software    Path to vhs-decode. This option is mandatory."
  echo "-y, --syntax      Parameters for vhs-decode, default: --frequency 16.000000 --ct --nld --threads 4 --recheck_phase"
  echo "-e, --extension   Extension of the captured files, eg. r8, r16, flac. Defaults to flac."
  echo "-c, --system      Videosystem, either PAL, PALM, NTSC, NTSCJ, MESECAM. Defaults to PAL"
  echo ""
  echo "Example: $(basename $0) -d /home/captures/ -o /home/tbc/ -s /home/git/vhs-decode/vhs-decode -c NTSC"
}

while [ "$1" != "" ]; do
  case $1 in
    -d | --indir )
      shift
      input=$1
      ;;
    -o | --outdir )
      shift
      output=$1
      ;;
    -s | --software )
      shift
      swdecoder=$1
      ;;    
    -y | --syntax )
      shift
      syntax=$1
      ;;
	-e | --extension )
	  shift
      extension=$1
      ;; 
    -c | --system )
      shift
      system="--system "$1
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

if [ "$output" = "" ]; then
  echo "Please specify an output"
  usage
  exit 1
fi

if [ ! -f $output$decscript ]; then
  echo "No previous shell script for processing found, creating one in $output called $decscript"
  echo "Commands will be added to the file, but not deleted. So do regular checks for old entries!"
  touch -f $output$decscript
  echo "#!/bin/bash" > $output$decscript
  chmod 0755 $output$decscript
  echo "File is located in: "$output$decscript
fi

if [ "$swdecoder" = "" ]; then
  echo "Please specify a vhs-decode version, e.g. /home/user/git/vhs-decode/vhs-decode"
  usage
  exit 1
fi

echo "Input directory: $input"
echo "Output directory: $output"
echo "File extension is: $extension"
echo "VHS Decode Version: $swdecoder"



for file in `ls $input`
do
  fextension=${file##*.}
  if [ "$fextension" = "$extension" ]; then
    s=${file##*.}
    input_stripped=${file%.$extension}
    echo "Adding file to queue in script"
    echo "# Video" >> $output$decscript
    echo $swdecoder $input$file $output$input_stripped $system$syntax >> $output$decscript
  fi
done
