@echo off
cls

set current_path=%~dp0
set log_file=%TMP%\scrapy_paper.log

echo "scrapy_paper start time :%DATE% %TIME%" >> %log_file%

IF /I "%1" == "-i" (
    call :InstallSchtasks
)ELSE (
IF /I "%1" == "-r" (
    call :ScrapyAll
)ELSE (
IF /I "%1" == "-u" (
    call :UnInstallSchtasks
)ELSE (
    echo "--help parameter." >> %log_file%
    echo "-i to install auto crawlall."
    echo "-u to uninstall auto crawlall."
    echo "log file: %log_file%"
)
)
)

echo "scrapy_paper end time : %DATE% %TIME%" >> %log_file%
exit /b 0


:InstallSchtasks
    echo "add schtasks scrapy_paper : %~f0" >> %log_file%
    schtasks /create /sc minute /mo 1 /tn "scrapy_paper" /tr "cmd /c %~f0 -r"
    exit /b 0

:UnInstallSchtasks
    echo "delete schtasks scrapy_paper : %~f0" >> %log_file%
    schtasks /delete /tn "scrapy_paper" /F
    exit /b 0

:ScrapyAll
echo "scrapy crawlall  start time: %DATE% %TIME%" >> %log_file%
pushd %current_path%
scrapy crawlall >> %log_file%
echo "scrapy crawlall  end time: %DATE% %TIME%" >> %log_file%
exit /b 0