@echo off
setlocal

set "SRC=C:\Users\ions\Documents\IonControl\project_dir\QuditLab\config\PulseProgramsPlus"
set "DST=\\senkolab-nas.iqc.uwaterloo.ca\Documents\IonControl_PulsePrograms_Mirror"
set "LOGDIR=%USERPROFILE%\Desktop\robocopy_logs"
set "LOG=%LOGDIR%\QuditLab_PulsePrograms_mirror.log"

if not exist "%LOGDIR%" mkdir "%LOGDIR%"

robocopy "%SRC%" "%DST%" /MIR /Z /R:2 /W:2 /DCOPY:T /TEE /LOG+:"%LOG%"

if %ERRORLEVEL% GEQ 8 exit /b %ERRORLEVEL%
exit /b 0
