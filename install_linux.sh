#!/bin/bash

current_path=`pwd`
task="*/60 * * * * root (cd $current_path && scrapy crawlall)"
crontab_txt=`cat /etc/crontab`
exist_task=`echo "$crontab_txt" | grep "scrapy_paper"`

install_crontab()
{
    echo "Install the scrapy_paper task..."
    if [ "$exist_task" != "" ];then
        echo "The scrapy_paper task already exists in the /etc/crontab file"
    else
        echo "*/60 * * * * root (cd /root/scrapy_paper && scrapy crawlall)" >> /etc/crontab
        echo "install scrapy_paper task successed."
    fi
}

uninstall_crontab()
{
    echo "Uninstall the scrapy_paper task..."
    sed  -i '/.*scrapy_paper/d' /etc/crontab
}



if [ "$1" = "-i" ];then
	install_crontab
elif [ "$1" = "-u" ];then
	uninstall_crontab
else
	echo "sh install_linux.sh -i     # to install timed crawling tasks"
	echo "sh install_linux.sh -u     # to uninstall timed crawling tasks"
fi