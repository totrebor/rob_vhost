#!/bin/bash




VER="0.0.0.9"

RUNCOMMAND="/root/runcommandwithbash"
GUESTFILE=$(cat /root/guestpath)
LOCKFILE="/root/lock"

checkFiles() {
  if([ "${GUESTFILE}" == "" ]); then
    echo "Guestfile empty"
    exit 100
  fi
  if([ ! -e "${RUNCOMMAND}" ]); then
    echo "Runcommand - ${RUNCOMMAND} - file not found"
    exit 101
  fi
  if([ ! -e "${GUESTFILE}" ]); then
    echo "Guestfile - ${GUESTFILE} - file not found"
    exit 102
  fi
}

checkPar() {
  echo "USERDATA $USERDATA", "USERIDDATA $USERIDDATA", "GROUPIDDATA $GROUPIDDATA", "GROUPDATA $GROUPDATA"
  if([ "${USERDATA}" == "" ]); then
    echo "User data not found"
    exit 200
  fi
  if([ "${USERIDDATA}" == "" ]); then
    echo "User id data not found"
    exit 201
  fi
  if([ "${GROUPIDDATA}" == "" ]); then
    echo "Group id data not found"
    exit 202
  fi
  if([ "${GROUPDATA}" == "" ]); then
    echo "Group data not found"
    exit 203
  fi
}

addUserGuest() {
  echo ADD $1, $2 , $3, $4
  USER=$1
  USERID=$2
  GROUPID=$3
  GROUP=$4
  if([ "${USER}" != "0" ]); then
    EXISTS=$(grep -c ^${USER}: /etc/passwd)
    IDEXISTS=$(id -nu ${USERID} 2>/dev/null)
    GIDEXISTS=$(cat /etc/group | gawk -v FS=: '{print $3}' | grep -c ^${GROUPID})
    GEXISTS=$(grep -c ^${GROUP}: /etc/group)
    if([ "$EXISTS" != "0" ]); then
      echo "User $USER already exists"
      exit 1
    else
      if([ "$IDEXISTS" != "" ]); then
        echo "User id $USERID already exists"
        exit 2
      else
        if([ "$GIDEXISTS" != "0" ]); then
          echo "User gid $GIDEXISTS already exists"
          exit 3
        else
          if([ "$GEXISTS" != "0" ]); then
            echo "Group $GEXISTS already exists"
            exit 4
          else
            groupadd -g $GROUPID "${GROUP}"
            useradd -m -g $GROUPID -s /usr/sbin/nologin -u $USERID "$USER"
          fi
        fi
      fi
    fi
  fi
}



echo "version ${VER}"

checkFiles

USERDATA=($(cat ${GUESTFILE} | gawk -v FS=: '{print $1}'))
USERIDDATA=($(cat ${GUESTFILE} | gawk -v FS=: '{print $3}'))
GROUPIDDATA=($(cat ${GUESTFILE} | gawk -v FS=: '{print $4}'))
GROUPDATA=($(cat ${GUESTFILE} | gawk -v FS=: '{print $5}'))

checkPar

if([ ! -e "${LOCKFILE}" ]); then
  COUNT=$(( ${#USERDATA[@]} ))
  echo "New users ${COUNT}"
  x=0
  while [ $x -lt $COUNT ]
  do
    addUserGuest "${USERDATA[$x]}" "${USERIDDATA[$x]}" "${GROUPIDDATA[$x]}" "${GROUPDATA[$x]}"
    x=$(( $x + 1 ))
  done
fi

touch "${LOCKFILE}"

echo "RUNCOMMAND $@"
cat ${RUNCOMMAND}
echo "START RUNCOMMAND"
( ${RUNCOMMAND} $@ )

##cat /etc/passwd
##cat /etc/group

