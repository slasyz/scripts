#!/bin/bash

disk_usage=$(df -h | grep '/dev/sda1 ' | awk '{print $5}' | sed 's/%//')

if (( disk_usage < 75 )); then    # bash arithmetic comparison
  echo "vdsalert.sh: disk usage is ${disk_usage}% - below threshold, ok, calling URL"
  if ! curl $(cat "$(dirname "$0")/url.txt") > /dev/null 2>&1; then
    echo "vdsalert.sh: curl failed"
  fi
else
  echo "vdsalert.sh: disk usage is ${disk_usage}% - above threshold, not ok, will trigger alert"
fi
