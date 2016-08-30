#!/bin/bash
for i in {1..1000}
do
   curl --data "people_run=$1&fullname=$2&is_permitted=true&is_input=true&profile=$3&bus=false" http://0.0.0.0:3000/api/records/
   curl --data "people_run=$1&fullname=$2&is_permitted=true&is_input=false&profile=$3&bus=false" http://0.0.0.0:3000/api/records/
   #sleep $(( ( RANDOM % 2 )  + 1 ))
done
