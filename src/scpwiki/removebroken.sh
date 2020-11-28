# git bash script to remove files that end in spaces
# these files aren't normally deletable in windows explorer
# handle this script with care. read through it first so that you know what it does.
find . -type d -print0 | while IFS= read -r -d $'\0' j; do
    pushd `pwd` > /dev/null
    cd $j
    find . -type f -print0 | while IFS= read -r -d $'\0' i; do
        if [[ $i == *" "* ]]; then
            echo removing "$i"
            rm "$i"
        fi
    done
    popd > /dev/null
done