SetFilterMTMode("QTGMC", 2)
FFmpegSource2("/folder/video.mkv", vtrack=-1,  cache=True, cachefile="", fpsnum=-1, fpsden=1, threads=-1, timecodes="", seekmode=1, overwrite=False, width=-1, height=-1, resizer="BICUBIC", colorspace="", rffmode=0, adjustdelay=-1, varprefix="")

### If input are images instead of video
# Change fps accordingly to your region, PAL=25, NTSC=29.97, end=framenumber of last frame
#ImageSeq_ImageReader(file="/folder/%08d.png", start=0, end=100, fps=25, use_devil=false, info=false)
# Rec601 as we have sdtv colorspace. HD would be Rec701 (At least for EU) interlaced=false as the fields are stacked on top of each other instead of being weaved together
#ConvertToYUV444(interlaced=false, matrix="Rec601")

### Weave stacked fields together, optional tweak each field
# order is TFF. For BFF OddField variable might be swapped with EvenField variable and AssumeBFF() instead of AssumeTFF()
# The Tweak option can be enabled by omiting the space and the #
# Tweaks are sometimes necessary as odd and even fields from a VHS machine might vary in quality, brightness and color
OddField = Crop(0, 0, 0, -288, align=False) #.Tweak(hue=0.0, sat=1.00, bright=0, cont=1.00, coring=True, sse=False, startHue=0, endHue=360, maxSat=150, minSat=0, interp=16) # Usually Field 0, 2, 4, n  as we count from 0 and not 1
EvenField = Crop(0, 288, 0, 0, align=False) #.Tweak(hue=0.0, sat=1.00, bright=0, cont=1.00, coring=True, sse=False, startHue=0, endHue=360, maxSat=150, minSat=0, interp=16) # Usually Field 1, 3, 5, n as we count from 0 and not 1
Interleave(OddField,EvenField)
AssumeFieldBased()
AssumeTFF()

Weave()

### Deinterlace with QTGMC
# FPSDivisor=2 is recommended if source is PAL and film based (usually upseed from 24fps to 25fps in PAL)
# I did not see any quality loss by doing so. It even looked better and more stable, from my experience.
QTGMC(Preset="Placebo", SourceMatch=3, Lossless=2, Sharpness=0.4, EdiThreads=6) # Empfehlung Phelissimo #, FPSDivisor=2
# Enable Multithreading
# For 6-core, 12-threads, change accordingly for your CPU setup
Prefetch(threads=12)

### crop and resize, to make it "HD"
# Crop (+right,+top,-left,-bottom)
Crop(0, 0, -12, 0, align=False)
Spline36Resize(1440, 1080, src_left=0.0, src_top=0.0, src_width=0.0, src_height=0.0)
