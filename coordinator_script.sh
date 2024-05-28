#!/bin/bash

export PATH=$PATH:/usr/bin:/bin:/usr/sbin:/sbin

echo "$(date): Running coordinator_script.sh" >> /home/samah/Desktop/projectTwo/coordinator_script.log 2>> /home/samah/Desktop/projectTwo/coordinator_script_error.log

switches=$(/usr/bin/mysql -u root -pmysql_native_password-e "USE tempmon; SELECT switch_id, ip_address FROM switches LIMIT 5;" -B -N)

while read -r switch; do
    switch_id=$(echo $switch | awk '{print $1}')
    ip_address=$(echo $switch | awk '{print $2}')
    
   
    task="{\"switch_id\": \"$switch_id\", \"ip_address\": \"$ip_address\"}"
    
    
    /usr/bin/python3 /home/samah/Desktop/projectTwo/collector_script.py "$task   " &
done <<< "$switches"


if ! /usr/bin/pgrep -x "grafana-server" > /dev/null
then
    sudo /usr/bin/systemctl start grafana-server
fi

echo "$(date): Finished running coordinator_script.sh" >> /home/samah/Desktop/projectTwo/coordinator_script.log 2>> /home/samah/Desktop/projectTwo/coordinator_script_error.log
