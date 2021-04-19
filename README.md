# Report-Monitor

[Report-Monitor](https://github.com/zhongsheng-chen/ReportMonitor) 
is a roaming web spider to listen on Information System of Graduate Student Management 
([ISysGSM](https://graduate.buct.edu.cn "北京化工大学研究生信息管理系统")) of 
[Beijing University of Chemical Technology](https://www.buct.edu.cn "北京化工大学"). 


## Why develop it?

Beijing University of Chemical Technology, or BUCT has almost 15300 undergraduate students
and nearly 8100 graduate students, not to mention 2700 continuing-education students 
and 460 foreigner students. It places a strict graduation criteria on graduate students.
One of them is that attending academic reports or conferences no less than 6 for graduate 
students who are perusing their Master degrees and no less than 8 for Ph.D. candidates.
The affairs office for graduate student has always been telling out conference announcements 
with very rare notifications. The students no matter where are currently on campus 
or have been stuck at home by the COVID 19 pandemic is not easy to sign up a conference 
or report event. That is the inspiration of our efforts to develop a tool to 
have a student had a chance to get a quota of attending report events when they are available.

Report-Monitor is not new. It was originally implemented 
by [Satone](https://gitee.com/satone7/report-monitor).
Satone's implementation is vey time-consuming when `auto login` option is used, 
due to low accurate rate of image recognition of validation code. Hence, we develop
a new Report-Monitor with a higher recognition rate. The majority of our efforts was
spending on cropping and denoising images of validation codes. 

## Features

* Reducing time when running with `auto login`, taking 2 or more minutes.
* More reasonable way to cropping images of validation codes.
* More effective preprocess to denoise validation code images.



## Installation



## Acknowledgement
main contributors:

Zishu GAO（高子淑）zsgao@mail.buct.edu.cn for writing up installation tutorial.



##


