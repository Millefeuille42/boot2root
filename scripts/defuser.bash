echo "Generating the codes for step [1-5]"
python "$1" >| codes.txt
echo "---"
cat codes.txt
echo "---"

echo "Generating the combinations for step 6"
python "$1" codes >| "$2"

while IFS= read -r line; do
    printf "Trying combination: $line\r"
    ret=""
    ret=$(echo $line | ./bomb a | grep "BOOM")
    if [[ -z "$ret" ]]; then 
	    printf "\ndefused\n"
	    echo "$line" >> codes.txt
    fi
done < "$2"
