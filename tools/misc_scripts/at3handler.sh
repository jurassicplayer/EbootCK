AT3TOOL=$(winepath -w $HOME'/PSP_Tools/at3tool/at3tool.exe')
function convert(){
    echo '### Converting' "$FILENAME.wav" 'to AT3 ###'
    if [[ $FILENAME == *"_encoded"* ]]; then
        OUT="$FILEDIR"\\"${FILENAME::-8}".at3
    else
        OUT="$FILEDIR"\\"$FILENAME".at3
    fi
    wine "$AT3TOOL" -br 64 -wholeloop -e "$FILEDIR"\\"$FILENAME".wav $OUT
}
function encode(){
    echo '### Converting' "$(basename $FILE)" 'to correct codec/frequency ###'
    ffmpeg -loglevel warning -i $FILE -c:a pcm_s16le -vn -ar 44100 $(dirname "$FILE")/"$FILENAME"_encoded.wav
    FILENAME="$FILENAME"_encoded
}
function decode(){
    OUT="$FILEDIR"\\"$FILENAME"_decoded.wav
    echo '### Converting' "$FILE" 'to WAV ###'
    wine "$AT3TOOL" -repeat 1 -d $(winepath -w $FILE) $OUT
}

for FILE in $@; do
    if [ -d $FILE ]; then
        echo "I can't convert folders."
    else
        FILEDIR=$(winepath -w $(dirname "$FILE"))
        FILENAME=$(basename "$FILE" .${FILE#*.})
        if [[ ${FILE#*.} == "at3" ]]; then
            decode
        else
            case ${FILE#*.} in
                #audio formats
                aac)
                    encode
                    ;;
                ac3)
                    encode
                    ;;
                amr)
                    encode
                    ;;
                flac)
                    encode
                    ;;
                mp2)
                    encode
                    ;;
                mp3)
                    encode
                    ;;
                ogg)
                    encode
                    ;;
                wav)
                    PROBE=$(ffprobe "$FILE" 2>&1 | tail -n 1)
                    if ! [[ $PROBE == *"pcm_s16le"* ]] && [[ $PROBE == *"44100 Hz"* ]]; then
                        encode
                    fi
                    ;;
                wma)
                    encode
                    ;;
                #video formats
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
                wmv)
                    encode
                    ;;
                3gp)
                    encode
                    ;;
                *)
                    echo $"Usage at3handler.sh <video/audio_file>"
                    echo "Filenames cannot have spaces."
                    read -p 'At3 conversion failed!'
                    exit 1
            esac
            wait
            convert
            wait
            read -p 'Completed at3 conversion!'
        fi
    fi
done;
