@echo off
:top
title Toontown Realms Data Pack Development Kit

set PANDA_PATH=C:/Panda3D-1.10.13-x64

echo Using Panda3D installation located at %PANDA_PATH%

IF NOT EXIST %PANDA_PATH%/python/python.exe (
	echo !! Could not find ./python/python.exe in %PANDA_PATH%. !!
	echo !! Make sure your PANDA_PATH variable is set correct in run.cmd !!
	pause
	exit
)

%PANDA_PATH%/python/python.exe -m pip install -r requirements.txt
%PANDA_PATH%/python/python.exe -m src.base.DPDKBase


pause