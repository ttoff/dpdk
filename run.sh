#!/bin/bash

TITLE="Toontown Realms Data Pack Development Kit"
echo -e '\033k'$TITLE'\033\\'

# Usage: ./run.sh <path-to-panda-wheel>
#
# Since Panda3D SDK distributions for unix-like systems does not include
# a copy of Python, we search for the system python by default instead.
#
# For instructions on how to build a wheel for Panda, see:
# https://github.com/panda3d/panda3d#linux

if [ -z "$SYSTEM_PYTHON" ];
then
	echo "Setting SYSTEM_PYTHON variable to default ..."
	export SYSTEM_PYTHON=/usr/bin/python
fi
echo "Using system python located at $SYSTEM_PYTHON"

if [ ! -f /bin/python ];
then
	echo "!! Could not find system python at $SYSTEM_PYTHON !!" >>/dev/stderr
	echo "!! Make sure your SYSTEM_PYTHON env var is set correct in run.sh !!" >>/dev/stderr
	read -t 1 -p "" # pause
	exit 1 # exit w/ err
fi

if [ -z "$PYTHON_PATH" ];
then
	$SYSTEM_PYTHON -m venv .venv
	export PYTHON_PATH="$(pwd)/.venv"
fi

source $PYTHON_PATH/bin/activate
python -m pip install --upgrade pip

if [ -z "$1" ];
then
  # If argument given, expect path to wheel and install.
	python -m pip install -U $1
fi

python -m pip install -v -r requirements.txt
python -m src.base.DPDKBase

read -t 1 -p "" # pause
