# Transfer


**SUNAPI** **Copyright**



v2.6.3

2023-09-20



© 2023 Hanwha Vision Co., Ltd. All rights reserved.


**Restriction**

Do not copy, distribute, or reproduce any part of

this document without written approval from

Hanwha Vision Co., Ltd.


**Disclaimer**

Hanwha Vision Co., Ltd. has made every effort to

ensure the completeness and accuracy of this

document, but makes no guarantee as to the

information contained herein. All responsibility for

proper and safe use of the information in this

document lies with users. Hanwha Vision Co., Ltd.

may revise or update this document without prior

notice.


**Contact Information**

Hanwha Vision Co., Ltd.

Hanwha Vision 6, Pangyo-ro 319beon-gil, Bundang
gu, Seongnam-si, Gyeonggi-do, 13488, KOREA

[www.hanwhavision.com](https://www.hanwhavision.com)


Hanwha Vision America

500 Frank W. Burr Blvd. Suite 43 Teaneck, NJ 07666

[hanwhavisionamerica.com](https://hanwhavisionamerica.com)


Hanwha Vision Europe

Heriot House, Heriot Road, Chertsey, Surrey, KT16

9DT, United Kingdom

[hanwhavision.eu](https://hanwhavision.eu)


Hanwha Vision Middle East FZE

Jafza View 18, Office 2001-2003, Po Box 263572,

Jebel Ali Free Zone, Dubai, United Arab Emirates

[www.hanwhavision.com/ar](https://www.hanwhavision.com/ar)


## **Table of Contents**

1. Overview . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . 4

1.1. Description . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . 4

2. FTP . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . 5

2.1. Description . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . 5

2.2. Syntax . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . 5

2.3. Parameters . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . 5

2.4. Examples . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . 7

2.4.1. Getting FTP server information . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . 7

2.4.2. Setting the FTP server . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . 8

2.4.3. Setting the FTP server with an encrypted password . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . 8

2.4.4. Checking the connection status of the FTP Server . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . 9

2.4.5. INSTALL SFTP Key (with encrypted keypassphrase) . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . 9

2.4.6. Remove SFTP Key File . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . 10

2.4.7. SFTP set operation . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . 10

3. SMTP . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . 11

3.1. Description . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . 11

3.2. Syntax . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . 11

3.3. Parameters . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . 11

3.4. Examples . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . 12

3.4.1. Getting SMTP server information . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . 13

3.4.2. Setting the SMTP server . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . 14

3.4.3. Setting the SMTP server with encrypted password . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . 14

3.4.4. Checking the connection status of the SMTP Server . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . 14

4. SMTP Users . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . 16

4.1. Description . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . 16

4.2. Syntax . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . 16

4.3. Parameters . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . 16

4.4. Examples . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . 17

4.4.1. Getting the current SMTP user settings . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . 17

4.4.2. Getting the ‘User Index 1’ settings . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . 18

4.4.3. Adding a new SMTP user. . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . 19

4.4.4. Updating the user name . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . 20

4.4.5. Removing the user . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . 20

5. SMTP User Group . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . 21

5.1. Description . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . 21

5.2. Syntax . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . 21


2 Transfer


5.3. Parameters . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . 21

5.4. Examples . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . 21

5.4.1. Getting the current SMTP user group settings . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . 21

5.4.2. Getting the settings of ‘Group 1’ . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . 22

5.4.3. Adding an SMTP user group. . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . 23

5.4.4. Updating the user group name . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . 24

5.4.5. Removing the user group . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . 24

6. Data Server. . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . 25

6.1. Description . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . 25

6.2. Syntax . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . 25

6.3. Parameters . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . 25

6.4. Examples . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . 26

6.4.1. Getting the current data server settings . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . 26

6.4.2. Setting the data server . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . 27

6.4.3. Testing the data server’s settings . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . 27


SUNAPI 3


## **Chapter 1. Overview**
### **1.1. Description**

**transfer.cgi** configures the FTP/SMTP server settings to transfer images or event notification when an

event occurs.


The actual transfer through FTP/SMTP is controlled by the EventAction parameter in **eventrules.cgi** for

camera and smtp submenu eventactions.cgi for NVR when certain events occur such as Alarm Input,

Video Analytics, Video Loss, Network Event, Face Detection, Tampering Detection, Audio Detection,

Tracking and Timer.


The following submenus are used to control the transfer API:


 - **ftp** : Sets the FTP (File Transfer Protocol) configuration for sending images or videos.


 - **smtp** : Sets the SMTP (Simple Mail Transfer Protocol) configuration for sending notification messages.

Images can be attached as email attachments.


 - **smtpusers** : Sets the SMTP mail users.


 - **smtpgroups** : Sets the SMTP mail user groups.


 - **dataserver** : Sets the data server.


4 Transfer


## **Chapter 2. FTP**
### **2.1. Description**

The **ftp** submenu configures the FTP (File Transfer Protocol) server settings.


This chapter applies to network cameras only.
**NOTE**

Attribute to check for Feature Support: " **attributes/transfer/Support/FTP** "


**Access level**

|Action|Camera|
|---|---|
|view|Admin|
|set|Admin|
|test|Admin|


### **2.2. Syntax**

```
 http://<Device IP>/stw-cgi/transfer.cgi?msubmenu=
 ftp &action=<value>[&<parameter>=<value>]

### **2.3. Parameters**

```








|Action|Parameters|Request/<br>Response|Type/<br>Value|Description|
|---|---|---|---|---|
|view||||Reads the FTP settings|
||SFTP.KeyName|RES|<string>|Name of the keyfile, if keyfile is<br>already installed.|
|set|Host|REQ, RES|<string>|Domain name of the FTP server<br>(required)<br>The host is specified in the format of<br><IP Address> or <Host name> e.g.<br>ftp.samsung.com or 192.168.100.1|
||Port|REQ, RES|<int>|FTP port number|
||Username|REQ, RES|<string>|FTP user name|
||Password|REQ, RES|<string>|FTP user password|


SUNAPI 5


|Action|Parameters|Request/<br>Response|Type/<br>Value|Description|
|---|---|---|---|---|
||IsPasswordEncrypted|REQ|<bool>|Returns true if password sent is<br>encrypted.<br>Encrypted password should be sent as<br>a post message.|
||Mode|REQ, RES|<enum><br>Active,<br>Passive|FTP transmission mode|
||Path|REQ, RES|<string>|The path on the FTP server where<br>alarm images are saved.<br>Value must be the relative path.|
||ReportFileType|REQ, RES|<enum><br>Image,<br>VideoClip|The type of file which is sent to the<br>FTP server. When this parameter is<br>not supported, only images are<br>provided if a configured event is<br>triggered.|
||PreEventDuration|REQ, RES|<enum><br>1s, 2s, 3s|Duration of pre-event recording. The<br>unit is second. This parameter is valid<br>when "ReportFileType" is "VideoClip"|
||PostEventDuration|REQ, RES|<enum><br>10s, 15s,<br>20s|Duration of post-event recording. The<br>unit is second. This parameter is valid<br>when "ReportFileType" is "VideoClip"|
||Encryption|REQ, RES|<enum><br>None, SFTP|Option to select Secure FTP or normal<br>FTP|
||SFTP.AuthMode|REQ, RES|<enum><br>Password,<br>KeyFile|When Encryption is set to SFTP, auth<br>mode can be configured. It can be<br>either password based or keyfile<br>based.|
|install|IsPassPhraseEncrypted|REQ|<bool><br>True, False|When installing the key file, if the<br>passphrase is encrypted need to pass<br>this parameter as true.|
|remove|SFTP.KeyName|REQ|<string>|To remove the key file, need to pass<br>the key filename|
|test|status|RES|<string>|Tries to connect to the server with the<br>configured settings and returns the<br>result in the form of a string|


6 Transfer


### **2.4. Examples**

#### **2.4.1. Getting FTP server information**

REQUEST

```
 http://<Device IP>/stw-cgi/transfer.cgi?msubmenu=ftp&action=view

```

TEXT RESPONSE

```
 HTTP/1.0 200 OK
 Content-type: text/plain
 <Body>

 Host=192.168.100.1
 Mode=Active
 Port=22
 Path=/home/test
 Username=test
 Password=

 Host=192.168.100.1
 Mode=Active
 Port=22
 Path=/home/test
 Username=test
 Password=
 ReportFileType=Image
 PreEventDuration=3s
 PostEventDuration=10s
 Encryption=None
 SFTP.AuthMode=Password
 SFTP.KeyName=

```

JSON RESPONSE

```
 HTTP/1.0 200 OK
 Content-type: application/json
 <Body>

```

SUNAPI 7


```
 {
 "Host": "192.168.100.1",
 "Mode": "Active",
 "Port": 22,
 "Path": "/home/test",
 "Username": "test",
 "Password": ""
 }

 {
 "Host": "192.168.100.1",
 "Mode": "Active",
 "Port": 22,
 "Path": "/home/test",
 "Username": "test",
 "Password": "",
 "Encryption": "None",
 "SFTP": {
 "AuthMode": "Password",
 "KeyName": ""
 }
 }

#### **2.4.2. Setting the FTP server**
```

The FTP host, user name, password, mode, and path can be configured as shown in the command below.


REQUEST

```
 http://<Device IP>/stw cgi/transfer.cgi?msubmenu=ftp&action=set&Password=tes&Host=223.255.254.254&P
 ort=4&Username=tes&Mode=Active&Path=test1234

#### **2.4.3. Setting the FTP server with an encrypted password**
```

The FTP host, user name, mode, and path can be configured as shown in the command below. Password

should be encrypted with RSA and RSA_PKCS1_PADDING (Refer to security.cgi for information on

obtaining the RSA key).


Base 64 Encoded data should be sent as a POST message.


8 Transfer


REQUEST

```
 http://<Device IP>/stw cgi/transfer.cgi?msubmenu=ftp&action=set&Host=223.255.254.254&Port=4&Usernam
 e=tes&Mode=Active&Path=test1234&IsPasswordEncrypted=True

#### **2.4.4. Checking the connection status of the FTP Server**
```

REQUEST

```
 http://<Device IP>/stw-cgi/transfer.cgi?msubmenu=ftp&action=test

```

TEXT RESPONSE

```
 HTTP/1.0 200 OK
 Content-type: text/plain
 <Body>

 Status=Success

```

JSON RESPONSE

```
 HTTP/1.0 200 OK
 Content-type: application/json
 <Body>

 {
 "Status": "Success"
 }

#### **2.4.5. INSTALL SFTP Key (with encrypted keypassphrase)**
```

Key Passphrase can be encrypted using the RSA public key and sent in below json. (Refer to security.cgi

and Application programming guide for information on obtaining the RSA key and encrypting the

keypassphrase).


REQUEST

```
 http://<DeviceIP>/stw cgi/transfer.cgi?msubmenu=ftp&action=install&IsPassPhraseEncrypted=True

```

SUNAPI 9


POST BODY

```
 {
 "SFTPKey": {
 "KeyName": "ssss.key",
 "KeyData": "c2RmZHNkZGRkZGRkZGRk...........MTIxMjEyMTIxMjExMg==",
 "KeyPassPhrase": "RdkHuyI65lDT4s5SVy......lhaeXQObvRipEA==""
 }
 }

#### **2.4.6. Remove SFTP Key File**
```

REQUEST

```
 http://<DeviceIP>/stwcgi/transfer.cgi?msubmenu=ftp&action=remove&SFTP.KeyNam
 e=ssss.key

#### **2.4.7. SFTP set operation**
```

Setting the encryption mode and sftp authentication mode.


REQUEST

```
 http://<Device IP>/stw cgi/transfer.cgi?msubmenu=ftp&action=set&Password=tes&Host=223.255.254.254&P
 ort=4&Username=tes&Mode=Active&Path=test1234&Encryption=SFTP&SFTPAuthMode=Ke
 yFile

```

10 Transfer


## **Chapter 3. SMTP**
### **3.1. Description**

The **smtp** submenu configures the SMTP (Simple Mail Transfer Protocol) server settings.


**NOTE** Attribute to check for Feature Support: " **attributes/transfer/Support/SMTP** "


**Access level**

|Action|Camera|NVR|
|---|---|---|
|view|Admin|User|
|set|Admin|User|
|test|Admin|User|


### **3.2. Syntax**

```
 http://<Device IP>/stw-cgi/transfer.cgi?msubmenu=
 smtp &action=<value>[&<parameter>=<value>]

### **3.3. Parameters**

```



















|Action|Parameters|Request/<br>Response|Type/<br>Value|Description|
|---|---|---|---|---|
|view||||Reads the SMTP settings.|
|set|Authentication|REQ, RES|<enum><br>None,<br>SMTP,<br>POPBefore<br>SMTP|SMTP authentication|
||Host|REQ, RES|<string>|Domain name of the SMTP server<br>(Required).<br>The host is specified in the format of<br><IP Address> or <Host name> e.g.<br>smtp.samsung.com or 192.168.100.1,<br>and the max length is 63.|
||Port|REQ, RES|<int>|SMTP port number|
||Encryption|REQ, RES|<enum><br>None, SSL|SMTP encryption type|



SUNAPI 11


|Action|Parameters|Request/<br>Response|Type/<br>Value|Description|
|---|---|---|---|---|
||Username|REQ, RES|<string>|SMTP user name<br>**Username** is only valid if<br>**Authentication** is set as SMTP or<br>POPBeforeSMTP.|
||Password|REQ, RES|<string>|SMTP user password<br>**Password** is only valid if<br>**Authentication** is set as SMTP or<br>POPBeforeSMTP.|
||IsPasswordEncrypted|REQ|<bool>|Returns true if password sent is<br>encrypted.<br>Encrypted password should be sent as<br>a post message.|
||Sender|REQ, RES|<string>|Email address of the sender<br>The sender’s email address is<br>specified in the format of <Email<br>Address>.|
||Recipient|REQ, RES|<string>|Email address of the recipient<br>The recipient’s email address is<br>specified in the format of <Email<br>Address>.<br>Attribute to check max recipients:<br>"**attributes/transfer/Limit/SMTP.Ma**<br>**xRecipients**"<br>**CAMERA ONLY**<br>|
||Subject|REQ, RES|<string>|Email title<br>**CAMERA ONLY**<br>|
||Message|REQ, RES|<string>|Email content<br>**CAMERA ONLY**<br>|
|test|status|RES|<string>|Tries to connect to the server with the<br>configured settings and returns the<br>result in the form of a string.|

### **3.4. Examples**

12 Transfer


#### **3.4.1. Getting SMTP server information**

REQUEST

```
 http://<Device IP>/stw-cgi/transfer.cgi?msubmenu=smtp&action=view

```

TEXT RESPONSE

```
 HTTP/1.0 200 OK
 Content-type: text/plain
 <Body>

 Host=192.168.100.1
 Port=25
 Username=test
 Password=1234
 Authentication=SMTP
 Sender=test.a@samsung.com
 Recipient=test1.a@samsung.com
 Subject=hello
 Message=Test message
 Encryption=None

```

JSON RESPONSE

```
 HTTP/1.0 200 OK
 Content-type: application/json
 <Body>

 {
 "Host": "192.168.100.1",
 "Port": 25,
 "Username": "test",
 "Password": "1234",
 "Authentication": "SMTP",
 "Sender": "test.a@samsung.com",
 "Recipient": "test1.a@samsung.com",
 "Subject": "hello",
 "Message": "Test message",
 "Encryption": "None"

```

SUNAPI 13


```
 }

#### **3.4.2. Setting the SMTP server**
```

The SMTP host, port, user name, password, sender/recipient email addresses, email subject and message

can be configured as shown in the command below.


The **Username** and **Password** parameters can be specified only when SMTP server authentication is set

as SMTP or POPBeforeSMTP.


REQUEST

```
 http://<Device IP>/stw cgi/transfer.cgi?msubmenu=smtp&action=set&Authentication=SMTP&Host=www.hanwh
 asecurity.com&Port=25&Encryption=None&Username=test5678&Password=pw12345&Sen
 der=test@test.com&Recipient=stw@hanwhasecurity.com&Subject=test&Message=test

```

The following request example is for NVR only.


REQUEST

```
 http://<Device IP>/stw cgi/transfer.cgi?msubmenu=smtp&action=set&Authentication=SMTP&Host=192.168.1
 00.1&Port=25&Encryption=None&Username=aaa&Password=4321&Sender=test@test.com

#### **3.4.3. Setting the SMTP server with encrypted password**
```

The SMTP host, port, user name, sender/recipient email addresses, email subject and message can be

configured as shown in the command below. Password should be encrypted with RSA and

RSA_PKCS1_PADDING (Refer to security.cgi for information on obtaining the RSA key).


Base 64 Encoded data should be sent as a POST message.


REQUEST

```
 http://<Device IP>/stw cgi/transfer.cgi?msubmenu=smtp&action=set&Authentication=SMTP&Host=www.hanwh
 asecurity.com&Port=25&Encryption=None&Username=test5678&Sender=test@test.com
 &Recipient=stw@hanwhasecurity.com&Subject=test&Message=test&IsPasswordEncryp
 ted=True

#### **3.4.4. Checking the connection status of the SMTP Server**

```

14 Transfer


REQUEST

```
 http://<Device IP>/stw-cgi/transfer.cgi?msubmenu=smtp&action=test

```

TEXT RESPONSE

```
 HTTP/1.0 200 OK

 Content-type: text/plain

 <Body>

 Status=Success

```

JSON RESPONSE

```
 HTTP/1.0 200 OK

 Content-type: application/json

 <Body>

 {
 "Status": "Success"
 }

```

SUNAPI 15


## **Chapter 4. SMTP Users**
### **4.1. Description**

The **smtpusers** submenu configures the SMTP mail users.


This chapter applies to NVR only.



**NOTE**


**Access level**



Attribute to check for maximum users: " **attributes/security/Limit/MaxSMTPUser** "

Attribute to check for maximum users in group:

" **attributes/security/Limit/MaxSMTPUserPerGroup** "



|Action|NVR|
|---|---|
|view|User|
|add, update|User|
|remove|User|

### **4.2. Syntax**

```
 http://<Device IP>/stw-cgi/transfer.cgi?msubmenu=
 smtpusers &action=<value>[&<parameter>=<value>]

### **4.3. Parameters**

```








|Action|Parameters|Request/<br>Response|Type/<br>Value|Description|
|---|---|---|---|---|
|view|UserIndex|REQ|<int>|User index number|
||GroupID|REQ|<string>|Group ID|
|add, update|UserIndex|REQ, RES|<int>|User index number|
||GroupID|REQ, RES|<string>|Group ID|
||UserName|REQ, RES|<string>|User name|
||Recipient|REQ, RES|<string>|Email address of the recipient.<br>The recipient’s email address is<br>specified in the format of <Email<br>Address>.|
|remove|UserIndex|REQ|<int>|User index number|


16 Transfer


### **4.4. Examples**

#### **4.4.1. Getting the current SMTP user settings**

REQUEST

```
 http://<Device IP>/stw-cgi/transfer.cgi?msubmenu=smtpusers&action=view

```

TEXT RESPONSE

```
 HTTP/1.0 200 OK
 Content-type: text/plain
 <Body>

 GroupID=Group 1
 UserIndex=1
 UserName=Recipient 1
 Recipient=t1@samsung.com
 GroupID=Group 1
 UserIndex=2
 UserName=s12
 Recipient=s2@hanwhasecurity.com
 GroupID=Group 1
 UserIndex=3
 UserName=s3
 Recipient=s12@s12.com

```

JSON RESPONSE

```
 HTTP/1.0 200 OK
 Content-type: application/json
 <Body>

 {
 "SMTPUsers": [
 {
 "GroupID": "Group 1",
 "UserIndex": 1,
 "UserName": "Recipient 1",
 "Recipient": "t1@samsung.com"
 },

```

SUNAPI 17


```
 {
 "GroupID": "Group 1",
 "UserIndex": 2,
 "UserName": "s12",
 "Recipient": "s2@hanwhasecurity.com"
 },
 {
 "GroupID": "Group 1",
 "UserIndex": 3,
 "UserName": "s3",
 "Recipient": "s12@hanwhasecurity.com"
 }
 ]
 }

#### **4.4.2. Getting the ‘User Index 1’ settings**
```

REQUEST

```
 http://<Device IP>/stw cgi/transfer.cgi?msubmenu=smtpusers&action=view&UserIndex=1

```

TEXT RESPONSE

```
 HTTP/1.0 200 OK
 Content-type: text/plain
 <Body>

 GroupID=Group 1
 UserIndex=1
 UserName=Recipient 1
 Recipient=t1@samsung.com

```

JSON RESPONSE

```
 HTTP/1.0 200 OK
 Content-type: application/json
 <Body>

 {

```

18 Transfer


```
 "SMTPUsers": [
 {
 "GroupID": "Group 1",
 "UserIndex": 1,
 "UserName": "Recipient 1",
 "Recipient": "t1@samsung.com"
 }
 ]
 }

#### **4.4.3. Adding a new SMTP user**
```

REQUEST

```
 http://<Device IP>/stw cgi/transfer.cgi?msubmenu=smtpusers&action=add&GroupID=Group2&UserName=s12&R
 ecipient=s12@s12

```

CAMERA RESPONSE

```
 HTTP/1.0 200 OK
 Content-type: text/plain
 <Body>

 OK
 UserIndex=13

```

The following response example is for NVR only.


NVR RESPONSE

```
 HTTP/1.0 200 OK
 Content-type: text/plain
 <Body>

 OK

```

JSON RESPONSE

```
 HTTP/1.0 200 OK
 Content-type: application/json

```

SUNAPI 19


```
 <Body>

 {
 "Response": "Success"
 }

#### **4.4.4. Updating the user name**
```

REQUEST

```
 http://<Device IP>/stw cgi/transfer.cgi?msubmenu=smtpusers&action=update&UserIndex=13&UserName=t13

#### **4.4.5. Removing the user**
```

REQUEST

```
 http://<Device IP>/stw cgi/transfer.cgi?msubmenu=smtpusers&action=remove&UserIndex=7

```

20 Transfer


## **Chapter 5. SMTP User Group**
### **5.1. Description**

The **smtpgroups** submenu configures the SMTP mail user groups.


This chapter applies to NVR only.
**NOTE**

Attribute to check for maximum groups: " **attributes/security/Limit/MaxSMTPGroup** "


**Access level**

|Action|NVR|
|---|---|
|view|User|
|add, update|User|
|remove|User|


### **5.2. Syntax**

```
 http://<Device IP>/stw-cgi/transfer.cgi?msubmenu=
 smtpgroups &action=<value>[&<parameter>=<value>]

### **5.3. Parameters**

```








|Action|Parameters|Request/<br>Response|Type/<br>Value|Description|
|---|---|---|---|---|
|view|GroupID|REQ|<string>|User group ID|
|add, update|GroupID|REQ, RES|<string>|User group ID|
||GroupName|REQ, RES|<string>|Group name|
|remove|GroupID|REQ|<string>|User group ID|

### **5.4. Examples**

#### **5.4.1. Getting the current SMTP user group settings**

REQUEST

```
 http://<Device IP>/stw-cgi/transfer.cgi?msubmenu=smtpgroups&action=view

```

TEXT RESPONSE

```
 HTTP/1.0 200 OK

```

SUNAPI 21


```
 Content-type: text/plain
 <Body>

 GroupID=Group 1
 GroupName=Group 1
 GroupID=Group2
 GroupName=Group2
 GroupID=Group1
 GroupName=Group1
 GroupID=Group 3
 GroupName=Group 3

```

JSON RESPONSE

```
 HTTP/1.0 200 OK
 Content-type: application/json
 <Body>

 {
 "SMTPGroups": [
 {
 "GroupID": "Group 1",
 "GroupName": "Group 01"
 },
 {
 "GroupID": "Group2",
 "GroupName": "Group2"
 },
 {
 "GroupID": "Group 3",
 "GroupName": "Group 3"
 }
 ]
 }

#### **5.4.2. Getting the settings of ‘Group 1’**
```

REQUEST

```
 http://<Device IP>/stw
```

22 Transfer


```
 cgi/transfer.cgi?msubmenu=smtpgroups&action=view&GroupID=Group 1

```

TEXT RESPONSE

```
 HTTP/1.0 200 OK
 Content-type: text/plain
 <Body>

 GroupID=Group 1
 GroupName=Group 1

```

JSON RESPONSE

```
 HTTP/1.0 200 OK
 Content-type: application/json
 <Body>

 {
 "SMTPGroups": [
 {
 "GroupID": "Group 1",
 "GroupName": "Group 1"
 }
 ]
 }

#### **5.4.3. Adding an SMTP user group**
```

When adding a group with only **GroupName**, NVR creates a group whose **GroupID** is the same as

**GroupName** . If you want to create it separately, send a command with both **GroupID** and **GroupName** .


REQUEST

```
 http://<Device IP>/stw cgi/transfer.cgi?msubmenu=smtpgroups&action=add&GroupName=Group3

```

REQUEST

```
 http://<Device IP>/stw cgi/transfer.cgi?msubmenu=smtpgroups&action=add&GroupID=TestGroup&GroupName=

```

SUNAPI 23


```
 Group3

#### **5.4.4. Updating the user group name**
```

REQUEST

```
 http://<Device IP>/stw cgi/transfer.cgi?msubmenu=smtpgroups&action=update&GroupID=Group3&GroupName=
 Group3

#### **5.4.5. Removing the user group**
```

REQUEST

```
 http://<Device IP>/stw cgi/transfer.cgi?msubmenu=smtpgroups&action=remove&GroupID=Group3

```

24 Transfer


## **Chapter 6. Data Server**
### **6.1. Description**

The **dataserver** submenu configures the data server.


**NOTE** This chapter applies to the camera only.


**Access level**

|Action|Camera|
|---|---|
|view|Admin|
|set|Admin|
|test|Admin|


### **6.2. Syntax**

```
 http://<Device IP>/stw-cgi/transfer.cgi?msubmenu=
 dataserver &action=<value>[&<parameter>=<value>]

### **6.3. Parameters**

```








|Action|Parameters|Request/<br>Response|Type/<br>Value|Description|
|---|---|---|---|---|
|view||||Reads data server settings|
|set|Enable|REQ, RES|<bool>|Value that shows if the data server is<br>in active status or not|
||IPv4Address|REQ, RES|<string>|IPv4 address of the data server|
||Port|REQ, RES|<int>|Data server port number|
||Username|REQ, RES|<string>|Data server user name|
||Password|REQ, RES|<string>|Data server user password|
||IsPasswordEncrypted|REQ, RES|<bool>|Returns true if password sent is<br>encrypted.<br>Encrypted password should be sent as<br>a post message.|
||StoreName|REQ, RES|<string>|Description of data server<br>Up to 20 characters allowed.|


SUNAPI 25


|Action|Parameters|Request/<br>Response|Type/<br>Value|Description|
|---|---|---|---|---|
|test|ConnectionState|RES|<enum><br>Failed,<br>Connecting,<br>Success|Representing value that shows if the<br>data server is connected or not|

### **6.4. Examples**

#### **6.4.1. Getting the current data server settings**

REQUEST




```
 http://<Device IP>/stw-cgi/transfer.cgi?msubmenu=dataserver&action=view

```

TEXT RESPONSE

```
 HTTP/1.0 200 OK
 Content-type: text/plain
 <Body>

 Enable=False
 IPv4Address=192.168.1.1
 Port=3434
 UserName=admin
 Password=
 StoreName=testServer

```

JSON RESPONSE

```
 HTTP/1.0 200 OK
 Content-type: application/json
 <Body>

 {
 "Enable": false,
 "IPv4Address": "192.168.1.1",
 "Port": 3434,
 "UserName": "admin",
 "Password": "",
 "StoreName": "testServer"

```

26 Transfer


```
 }

#### **6.4.2. Setting the data server**
```

REQUEST

```
 http://<Device IP>/stw cgi/transfer.cgi?msubmenu=dataserver&action=set&Enable=True&IPv4Address=192.
 168.1.1&Port=3434&UserName=admin&Password=password&StoreName=testServer

```

TEXT RESPONSE

```
 HTTP/1.0 200 OK
 Content-type: text/plain
 <Body>

 OK

```

JSON RESPONSE

```
 HTTP/1.0 200 OK
 Content-type: application/json
 <Body>

 {
 "Status": "Success"
 }

#### **6.4.3. Testing the data server’s settings**
```

REQUEST

```
 http://<Device IP>/stw-cgi/transfer.cgi?msubmenu=dataserver&action=test

```

TEXT RESPONSE

```
 HTTP/1.0 200 OK
 Content-type: text/plain
 <Body>

```

SUNAPI 27


```
 ConnectionState=Connecting

```

JSON RESPONSE

```
 HTTP/1.0 200 OK
 Content-type: application/json
 <Body>

 {
 "ConnectionState": "Connecting"
 }

```

28 Transfer


