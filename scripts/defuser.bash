echo "Generating the codes for step [1-5]"
python "$1" >| codes.txt
echo "---"
cat codes.txt
echo "---"

echo "Generating the combinations for step 6"
python "$1" codes >| temp.txt

while IFS= read -r line; do
    printf "Trying combination: $line\r"
    ret=""
    ret=$(echo $line | ./bomb codes.txt | grep "BOOM")
    if [[ -z "$ret" ]]; then 
	    printf "\ndefused\n"
	    echo "$line" >> codes.txt
	    exit 0
    fi
done < temp.txt
