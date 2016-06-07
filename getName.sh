while read line; do
    VAR= "$line\n" | cut -d' ' -f9 | sed 's/\/employee\///'
    #echo "$line\n" | cut -d'/' -f3
    TEMP=$(curl http://10.0.0.125:6000/employee/$VAR)
    echo $VAR $TEMP
done < $1
