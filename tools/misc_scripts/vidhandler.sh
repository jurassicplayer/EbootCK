function encode(){
    echo '### Converting' "$(basename $FILE)" 'to correct codec/format/scale/framerate ###'
    ffmpeg -loglevel warning -i "$FILE" -r 29.97 -an -c:v rawvideo -vf scale=144:80,setsar=1/1,setdar=9/5 $(dirname "$FILE")/"$FILENAME"_reencode.avi
}

for FILE in $@; do
    if [ -d $FILE ]; then
        echo "I can't convert folders."
    else
        FILEDIR=$(dirname "$FILE")
        FILENAME=$(basename "$FILE" ".${FILE#*.}")
        case "${FILE#*.}" in
            avi)
                encode
                ;;
            flv)
                encode
                ;;
            mkv)
                encode
                ;;
            mov)
                encode
                ;;
            mpeg)
                encode
                ;;
            mpg)
                encode
                ;;
            mp4)
                encode
                ;;
            webm)
                encode
                ;;
            wmv)
                encode
                ;;
            3gp)
                encode
                ;;
            *)
                echo $"Usage vidhandler.sh <video_file>"
                echo "Filenames cannot have spaces."
                read -p 'Video conversion failed!'
                exit 1
        esac
        wait
        echo "Virtualdub method may provide videos better optimized for PMFs size-wise."
        echo "The video must be multiplexed in UMDStreamComposer and a pmf header added."
        read -p 'Completed video conversion!'
    fi
done;
