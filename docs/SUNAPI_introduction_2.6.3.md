# Introduction


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

1. Introduction to SUNAPI . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . 4

1.1. Overview . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . 4

1.2. SUNAPI Command Structure . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . 5

1.2.1. Syntax. . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . 5

1.2.2. Submenus . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . 5

1.2.3. Actions . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . 6

1.3. Response Format . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . 6

1.4. Examples . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . 6

1.4.1. Example of the View Action . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . 6

1.4.2. Example of the Set Action . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . 8

1.4.3. Note on Sample Requests & Responses . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . 10

1.5. Access level . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . 10

1.6. Authentication . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . 10

1.7. Index numbers. . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . 10

1.8. Error codes . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . 10

1.9. Special HTTP Error codes . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . 14

1.10. Style Conventions on SUNAPI Reference . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . 15

1.10.1. Syntax. . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . 15

1.10.2. Parameters . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . 15

1.11. Support . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . 16

2. Revision History . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . 17

2.1. Version 2.6.3 . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . 17

2.2. Version 2.6.2 . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . 20

2.3. Version 2.6.1 . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . 22

2.4. Version 2.6.0 . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . 23

2.5. Version 2.5.9 . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . 24

2.6. Version 2.5.8 . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . 27

2.7. Version 2.5.7 . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . 28

2.8. Version 2.5.6 . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . 31

2.9. Version 2.5.5 . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . 33

2.10. Version 2.5.4 . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . 36

2.11. Version 2.5.3 . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . 38

2.12. Version 2.5.2 . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . 42

2.13. Version 2.5.1 . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . 44

2.14. Version 2.5.0 . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . 47

2.15. Version 2.4.3 . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . 49


2 Introduction


2.16. Version 2.4.2 . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . 50

2.17. Version 2.4.1 . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . 51

2.18. Version 2.4.0 . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . 52

2.19. Version 2.3.2 . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . 54

2.20. Version 2.3.1 . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . 56

2.21. Version 2.3.0 . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . 57

2.22. Version 2.2.1 . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . 59

2.23. Version 2.0.0 . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . 64


SUNAPI 3


## **Chapter 1. Introduction to SUNAPI**
### **1.1. Overview**

The Smart Unified Network API (SUNAPI) provides a single, seamless interface for controlling and

configuring the various products which make up a networked video security system. It can integrate

products such as network cameras, storage devices (NVR and DVR), encoders and central monitoring

software (CMS), including both Hanwha Vision products and products from other third-party vendors.


SUNAPI allows you to access product features by simply entering standard HTTP URLs. The URLs pass

variables to SUNAPI’s CGI, which interfaces with the specific product. This simplified interface system

makes it possible for central monitoring software to access the features of a diverse set of products in a

standardized way. This makes SUNAPI a valuable tool for developers of central monitoring software and

other network video applications.


SUNAPI provides CGIs to perform the following functions:


 - System configuration: system.cgi configures general system settings and performs factory resets to

restore the system. It can also view system logs, event logs and access logs.


 - Network management: network.cgi sets up the network which connects the video security products. It

configures IP, DNS, DDNS and other settings.


 - Security management: security.cgi sets up security features such as RTSP, SSL and IP address filtering

(which allows only authorized addresses to connect). It also sets up systems users and configures their

access permissions.


 - Video streaming: video.cgi requests http retrieval of JPG images or MJPEG stream, and media.cgi

configures profiles, which include video/audio codec settings, audio input/output settings, etc.


4 Introduction


 - Image adjustment: image.cgi configures camera features such as BLC, privacy, white balance,

exposure and OSD.


 - Server settings: transfer.cgi configures the FTP and SMTP server settings for transferring event video

and images.


 - Event monitoring and handling: eventsource.cgi, eventrules.cgi, and eventstatus.cgi manage events

such as motion detection, face detection and tampering.


 - PTZ control: ptzcontrol.cgi and ptzconfig.cgi manage the camera’s pan, tilt and zoom and detail

configuration.


 - Searching stored data: recording.cgi configures recording schedules and related settings. It also

provides an interface to search recorded videos.


 - Open SDK installation: opensdk.cgi installs and manages the Open SDK application.

### **1.2. SUNAPI Command Structure**

SUNAPI commands are HTTP URLs. Each URL specifies the target device’s IP address and the CGI which

provides the command. This is followed by a query string which specifies the command’s submenu, action

and parameters.

#### **1.2.1. Syntax**


The following is an example of a device information request:

```
 http://192.168.0.100/stw-cgi/system.cgi?msubmenu=deviceinfo&action=view

```

The text in the URL command is case-sensitive. For example, if you type **msubmenu=DeviceInfo** instead

of **msubmenu=deviceinfo**, an error message will be generated.


To set a port number, add a colon after the IP address and enter the number in the format of<Device

IP>:<Port Number> as in the example below.

```
 http://192.168.0.100:20/stw-cgi/system.cgi?msubmenu=deviceinfo&action=view

```

**NOTE** For NVR, a channel number is mandatory wherever it is applicable.

#### **1.2.2. Submenus**

Each CGI is divided into submenus which perform specific functions. For example, **system.cgi** has

submenus such as **deviceinfo**, which sets up product information, and **date**, which sets the date. In the


SUNAPI 5


SUNAPI syntax, the submenu is specified in the query string by assigning a value to the ‘msubmenu’

variable. For example, msubmenu=deviceinfo.

#### **1.2.3. Actions**

An action must be specified for each SUNAPI command. SUNAPI offers the following action types:


 - view: Requests the current setting information.

Generally, the **view** action does not take parameters, and returns only response parameters and

values, which are marked as **RES** on the parameter table in the SUNAPI reference document. In some

cases, the view action does take request parameters.


 - set: Specifies new settings with new parameters.


 - control: Controls data settings.


 - update: Updates existing parameters with new values. updates the current data. The **update** and **add**

actions are used instead of the **set** action to add or modify list data such as the user list data or the IP

filtering list data.


 - add: Adds new parameters.


 - install: Installs data.


 - remove: Deletes the existing parameters.

### **1.3. Response Format**

A SUNAPI response is in text format for all the commands, except for the attributes response, which is in

XML format. From SUNAPI version 2.5 onwards two types of response format (Text and JSON) are

supported; by default, the response format will be text and if the request has special header (Accept:

application/json) the response will be in JSON format.

### **1.4. Examples**

Below are Examples for getting and setting information.

#### **1.4.1. Example of the View Action**

To get device information, the following request is used:


REQUEST

```
 http://192.168.0.100/stw-cgi/system.cgi?msubmenu=deviceinfo&action=view

```

ACTUAL REQUEST MESSAGE

For the default request as shown below, the response will be in text format.

```
 GET /stw-cgi/system.cgi?msubmenu=deviceinfo&action=view HTTP/1.1
 User-Agent: xxxxx

```

6 Introduction


```
 Host: 192.168.0.100
 Accept: */*

```

For a request in the format below, the response will be in JSON format from SUNAPI 2.5 onwards.


JSON REQUEST MESSAGE

```
 GET /stw-cgi/system.cgi?msubmenu=deviceinfo&action=view HTTP/1.1
 User-Agent: XXXXXX
 Host: 192.168.0.100
 Accept: application/json

```

The following response will be sent:


TEXT RESPONSE

```
 HTTP/1.0 200 OK
 Content-type: text/plain
 <Body>

 Model=XNF-9010RV
 SerialNumber=ZLNA70GKA0001JZ
 FirmwareVersion=2.01.00_20200721_R201
 BuildDate=2020.07.21
 WebURL=http://www.hanwhavision.com/
 DeviceType=NWC
 ConnectedMACAddress=00:09:18:5B:BD:3A
 ISPVersion=1.00_200721
 BootloaderVersion=ver=U-Boot 2020.07-svn2693 (Jul 21 2020 - 18:09:00
 CGIVersion=2.5.7
 ONVIFVersion=19.12
 DeviceName=Camera
 DeviceLocation=Location
 DeviceDescription=Description
 Memo=Memo
 Language=English
 PasswordStrength=Strong
 OpenSDKVersion=4.00_200702
 FirmwareGroup=XNF-9010RV

```

SUNAPI 7


JSON RESPONSE

```
 {
 "Model": "XNF-9010RV",
 "SerialNumber": "ZLNA70GKA0001JZ",
 "FirmwareVersion": "2.01.00_20200721_R201",
 "BuildDate": "2020.07.21",
 "WebURL": "http://www.hanwhavision.com/",
 "DeviceType": "NWC",
 "ConnectedMACAddress": "00:09:18:5B:BD:3A",
 "ISPVersion": "1.00_200721",
 "BootloaderVersion": "ver=U-Boot 2020.07-svn2693 (Jul 06 2020 - 18:09:00
 ",
 "CGIVersion": "2.5.7",
 "ONVIFVersion": "19.12",
 "DeviceName": "Camera",
 "DeviceLocation": "Location",
 "DeviceDescription": "Description",
 "Memo": "Memo",
 "Language": "English",
 "PasswordStrength": "Strong",
 "OpenSDKVersion": "4.00_200702",
 "FirmwareGroup": "XNF-9010RV"
 }

#### **1.4.2. Example of the Set Action**
```

To set the language to English, the following request should be used:


REQUEST

```
 http://192.168.0.100/stw cgi/system.cgi?msubmenu=deviceinfo&action=set&Language=English

```

The following response is sent:


TEXT RESPONSE

```
 HTTP/1.0 200 OK
 Content-type: text/plain_
 <Body>

```

8 Introduction


```
 OK

```

JSON RESPONSE

```
 HTTP/1.0 200 OK
 Content-type:application/json_
 <Body>

 {
 "Response": "Success"
 }

```

When an error occurs, an error message will be returned, as shown below:


REQUEST

```
 http://192.168.0.100/stw cgi/system.cgi?msubmenu=deviceinfo&action=set&Language=

```

TEXT RESPONSE

```
 HTTP/1.0 200 OK
 Content-type: text/plain_
 <Body>

 NG
 Error Code: 604
 Error Details:
 Invalid Input Value(s)

```

JSON RESPONSE

```
 HTTP/1.0 200 OK
 Content-type:application/json_
 <Body>

 {
 "Response": "Fail",
 "Error": {

```

SUNAPI 9


```
 "Code": 604,
 "Details": "Invalid Input Value(s)"
 }
 }

#### **1.4.3. Note on Sample Requests & Responses**
```

The SUNAPI reference provides code samples in each Chapter. The samples in SUNAPI documentation are

meant for reference only. The returned Data in the samples can differ from the actual data depending on

the product model and its configuration.

### **1.5. Access level**

SUNAPI has 4 types of access for CGI requests, Guests, Users, and Admin, which are based on the SUNAPI

action level.


If a user doesn’t have the permission to perform the particular action, then all the CGI parameters

corresponding to the action will not be accessed. For example, an Access Level specified as "Admin" will

be given only with the admin login, and other user logins will not have access to the corresponding

features.


Access Level is stated in the SUNAPI reference documents.

### **1.6. Authentication**

For Hanwha Vision products, the Digest Authentication is used for secure authentication.

### **1.7. Index numbers**

All index numbers start from **1** in SUNAPI, except channel number, deviceid(POS) and the snmptrap

submenu in network.cgi, which all start from **0** . In this reference document, the hash sign (#) represents

an index number.

### **1.8. Error codes**

When an error occurs during a **set** action command, the following error codes can be returned:


10 Introduction


|Error<br>Code|Define|Response(Text)|Response(JSON)|Description|
|---|---|---|---|---|
|600|Invalid<br>submenu|NG<br>Error Code: 600<br>Error Details:<br>Submenu Not Found|{<br>"Response": "Fail",<br>"Error": {<br>"Code": 600,<br>"Details": "Submenu Not<br>Found"<br>}<br>}|An unsupported menu<br>was requested|
|601|Invalid action|NG<br>Error Code: 601<br>Error Details:<br>Action Not Found|{<br>"Response": "Fail",<br>"Error": {<br>"Code": 601,<br>"Details": "Action Not<br>Found "<br>}<br>}|An unsupported action<br>was requested|
|602|Invalid<br>parameter|NG<br>Error Code: 602<br>Error Details:<br>Invalid Parameter(s)|{<br>"Response": "Fail",<br>"Error": {<br>"Code": 602,<br>"Details": "Invalid<br>Parameter(s) "<br>}<br>}|The parameters don’t<br>match the existing<br>settings in the request.<br>e.g.) When<br>IPv6Type=Auto and the<br>user requests the<br>IPv6Address, an error<br>occurs.|
|603|Missing<br>Required<br>Parameter|NG<br>Error Code: 603<br>Error Details:<br>Missing Required<br>Parameter(s)|{<br>"Response": "Fail",<br>"Error": {<br>"Code": 603,<br>"Details": "Missing<br>Required Parameter(s) "<br>}<br>}|The user request is<br>missing a required<br>parameter.|
|604|Invalid Value|NG<br>Error Code: 604<br>Error Details:<br>Invalid Input Value(s)|{<br>"Response": "Fail",<br>"Error": {<br>"Code": 604,<br>"Details": "Invalid Input<br>Value(s) "<br>}<br>}|The user request has an<br>invalid parameter value.|



SUNAPI 11


|Error<br>Code|Define|Response(Text)|Response(JSON)|Description|
|---|---|---|---|---|
|605|List is full|NG<br>Error Code: 605<br>Error Details:<br>List Full|{<br>"Response": "Fail",<br>"Error": {<br>"Code": 605,<br>"Details": "List Full"<br>}<br>}|The user has attempted<br>to add data to a list that<br>is full.|
|606|Duplicate value|NG<br>Error Code: 606<br>Error Details:<br>Duplicate Value|{<br>"Response": "Fail",<br>"Error": {<br>"Code": 606,<br>"Details": "Duplicate<br>Value"<br>}<br>}|The user has attempted<br>to set a value that is<br>already being used in<br>another field.|
|607|Unknown error|NG<br>Error Code: 607<br>Error Details:<br>Unknown Error|{<br>"Response": "Fail",<br>"Error": {<br>"Code": 607,<br>"Details": "Unknown<br>Error"<br>}<br>}|System-related error|
|608|Feature not<br>implemented<br>OR Not<br>supported|NG<br>Error Code: 608<br>Error Details:<br>Feature(s) Not<br>Implemented OR Not<br>Supported|{<br>"Response": "Fail",<br>"Error": {<br>"Code": 608,<br>"Details": "Feature(s)<br>Not Implemented OR<br>Not Supported"<br>}<br>}|When an unsupported<br>service or feature is<br>requested.|
|609|Not Authorized|NG<br>Error Code: 609<br>Error Details:<br>Not Authorized|{<br>"Response": "Fail",<br>"Error": {<br>"Code": 609,<br>"Details": "Not<br>Authorized"<br>}<br>}|A login error has<br>occurred.|



12 Introduction


|Error<br>Code|Define|Response(Text)|Response(JSON)|Description|
|---|---|---|---|---|
|610|Cannot Access<br>Resource|NG<br>Error Code: 610<br>Error Details:<br>Cannot Access Resource|{<br>"Response": "Fail",<br>"Error": {<br>"Code": 610,<br>"Details": "Cannot<br>Access Resource"<br>}<br>}|The other session is<br>using the resource.|
|611|Invalid File|NG<br>Error Code: 611<br>Error Details:<br>Invalid File|{<br>"Response": "Fail",<br>"Error": {<br>"Code": 611,<br>"Details": "Invalid File"<br>}<br>}|File is invalid.|
|612|Configuration<br>Not Found|NG<br>Error Code: 612<br>Error Details:<br>Configuration Not Found|{<br>"Response": "Fail",<br>"Error": {<br>"Code": 612,<br>"Details": "Configuration<br>Not Found"<br>}<br>}|A configuration is not<br>found.<br>e.g.) for cameras not<br>registered in NVR, there<br>will be no response for<br>camera-related CGI<br>requests|
|613|Cannot Set<br>Simultaneously|NG<br>Error Code: 613<br>Error Details:<br>Tried to set values at<br>once that can’t be set<br>simultaneously|{<br>"Response": "Fail",<br>"Error": {<br>"Code": 613,<br>"Details": "Tried to set<br>values at once that can’t<br>be set simultaneously"<br>}<br>}|When some features are<br>not available to be set at<br>the same time|
|614|Service Not<br>Ready|NG<br>Error Code: 614<br>Error Details:<br>Service not ready|{<br>"Response": "Fail",<br>"Error": {<br>"Code": 614,<br>"Details": "Service not<br>ready"<br>}<br>}|When some features are<br>not ready to service|



SUNAPI 13


|Error<br>Code|Define|Response(Text)|Response(JSON)|Description|
|---|---|---|---|---|
|615|Configuration<br>Cannot Applied|NG<br>Error Code: 615<br>Error Details:<br>The configuration cannot<br>be applied|{<br>"Response": "Fail",<br>"Error": {<br>"Code": 615,<br>"Details": "The<br>configuration cannot be<br>applied"<br>}<br>}|When some<br>configurations cannot be<br>set|
|616|Configuration<br>Incompatible|NG<br>Error Code: 616<br>Error Details:<br>The configuration is not<br>compatible|{<br>"Response": "Fail",<br>"Error": {<br>"Code": 616,<br>"Details": "The<br>configuration is not<br>compatible"<br>}<br>}|When some<br>configurations are not<br>compatible|
|700|Requested<br>parameter is<br>not found|NG<br>Error Code: 700<br>Error Details:<br><Tag Name>: Not Found|{<br>"Response": "Fail",<br>"Error": {<br>"Code": 700,<br>"Details": "<Tag Name>:<br>Not Found "<br>}<br>}|attributes.cgi error<br>The user request<br>contains an unsupported<br>tag|
|701|Error in XML file|NG<br>Error Code: 701<br>Error Details:<br>Invalid XML|{<br>"Response": "Fail",<br>"Error": {<br>"Code": 701,<br>"Details": "Invalid XML"<br>}<br>}|attributes.cgi error<br>The XML format is<br>incorrect|

### **1.9. Special HTTP Error codes**



The following special error codes will be sent when additional password is required or when the device is

locked on 5 successive login attempts with wrong password.


14 Introduction


|Error Code|Status Message|Title|Body|
|---|---|---|---|
|490|Status: 490<br>AccountBlocked|490 - Account Blocked|You have exceeded the<br>maximum number of<br>login attempts, Please try<br>after some time.|
|491|Status: 491<br>AdditionalPasswordRequi<br>red|491 - Additional<br>Password Required|Additional Passwords is<br>required for this action|


### **1.10. Style Conventions on SUNAPI Reference**

The SUNAPI reference document is for developers of central monitoring software (CMS) as well as

developers of applications for viewing, streaming and webcasting video.

#### **1.10.1. Syntax**

Text in the angle brackets is replaceable. In the example below, the text <Device IP> can be replaced with

the actual IP address of the device, such as 192.168.0.100.

```
 http://<Device IP>/stw cgi/system.cgi?msubmenu=<value>&action=<value>&<parameter>=<value>

#### **1.10.2. Parameters**
```

Parameter information is displayed in tables like the one below:












|Action|Parameter|Request/<br>Response|Type/<br>Value|Description|
|---|---|---|---|---|
|view<br>set<br>control|Parameter name|REQ<br>RES|<int><br><float><br><bool><br><string><br><enum><br><csv>|Brief parameter description|




 - The Action column shows the type of action performed on the parameter.


 - The Parameter column shows the name of the parameter.


 - The Request/Response column shows if the parameter is a request parameter (REQ) or a response

parameter (RES).


 - The Type/

Value column shows the value types as well as the allowed values and ranges. Value types are as

follows:


◦<enum> indicates enumeration values.


SUNAPI 15


◦<int> indicates integer values.


◦<float> indicates floating point values


◦<string> indicates string data.


◦<bool> indicates boolean values.


◦<csv> indicates comma-separated values. Set multiple values separated by commas.


 - The Description column offers a brief description of the parameter.

### **1.11. Support**

[Visit http://step.hanwhavision.com for the latest documents and technical support.](http://step.hanwhavision.com)


16 Introduction


## **Chapter 2. Revision History**
### **2.1. Version 2.6.3**

**Date** : 2023-09-11


System

*deviceinfo **WisenetPlatformVersion parameter added * geolocation** Mode enum updated with Off *

registeredsubdevices **Device..Type enum updated Device.** .AudioSourceType parameter added


Security

 - users


◦VideoProfileSettingAccess


◦ImageSettingAccess parameter added


◦VideoSetupAccess parameter added


◦FocusSetupAccess parameter added


◦PlaybackAccess parameter added


◦Check action added with CurrentUserCount and MaxUserCount parameter.


Media

 - speakervolume submenu added


 - backchannelinfo submenu added


 - speakerstatus submenu added


 - networkaudioinput submenu added


Image

 - whiteled submenu added


 - autofocuszone submenu added


 - wiseautofocus submenu added


 - overlay


◦PresetNamePositionX and PresetNamePositionY parameter added


◦QuickZoomAndFocusEnable parameter added


Transfer

 - ftp


◦SFTP support added


Network

 - sipaudiocodec submenu added


EventSources


SUNAPI 17


 - callrequest


◦MicrophoneActivationMode parameter added


 - autotracking


◦LostModeTimer parameter added


◦Redetection parameter added


◦RedectionTimer parameter added


 - boxtemperaturedetection


◦ROI.#.AreaName


◦ROI.#.PolygonCoordinates


◦ROI.#.AreaColor


◦ROI.#.Condition.#.Duration


◦ROI.#.Condition.#.DetectionType


◦ROI.#.Condition.#.ThresholdTemperature


◦ROI.#.Condition.#.TemperatureType


◦ROI.#.Condition.#.Enable


◦EntireAreaAvgTemperatureOverlay


◦EntireAreaMinTemperatureOverlay


◦EntireAreaMaxTemperatureOverlay


◦check action added


 - vehiclecount submenu added


EventRules

 - dynamicrulesoptions


◦EventSource policy enum updated


 - audiooutfiles


◦DeviceID parameter added for install action


◦Name parameter added for remove action


◦Volume parameter added for control action


◦LoopCount parameter added for control action


 - ttsfiles


◦Name parameter added for install action


◦DeviceID parameter added for install action


◦Language parameter added for install action


◦Gender parameter added for install action


◦Pitch parameter added for install action


18 Introduction


◦Speed parameter added for install action


◦DelayBetweenSentence parameter added for install action


◦DelayBetweenComma parameter added for install action


◦Volume parameter added for control action


◦LoopCount parameter added for control action


◦Name parameter added for remove action


PTZControl

 - movestatus submenu added


PTZConfig

 - group


◦Name parameter added


 - tour


◦TourMode


◦EnhancedSequence


◦SequenceType


◦PresetIndex


◦GroupIndex


◦TraceIndex


◦SwingMode


 - trace


◦view action added


◦Trace.#.Enable parameter added


◦Trace.#.Name parameter added


 - autorun


◦AutorunDuringSequence parameter added


 - presetvideoanalysis2


◦DefinedArea.#.RuleName


◦DefinedArea.#.ObjectTypeFilter


◦DefinedArea.#.ObjectTypeFilterDetails


◦Line.#.RuleName


◦Line.#.ObjectTypeFilter


◦Line.#.ObjectTypeFilterDetails


 - presetobjectdetection submenu added


 - ptzsettings


SUNAPI 19


◦QuickZoomEnable parameter added


Recoding

 - vehiclecountsearch submenu added

### **2.2. Version 2.6.2**

**Date** : 2022-01-30


System

 - New device class AMS (Audio Management System) added


 - systemlog


◦MQTTConnection enum value added to Type parameter


◦SSDManagement enum value added to Type parameter


 - deviceinfo


◦DeviceType list extended with NetworkSpeaker and NetworkMic.


◦SpeakerType parameter added


 - registeredsubdevices submenu added


 - speakergroups submenu added


 - ssdstorage submenu added


 - localvms submenu added


Network

 - sipsetup


◦CallStopEnable parameter added


 - sipaccount


◦SIPProxyAddress parameter added


 - sipcall


◦TestCallState parameter added


◦CallRequest parameter added


◦Ringing enum value added to CallState parameter


◦StopCallRequest parameter deprecated (Use CallRequest parameter instead)


 - mqttclient submenu added


Recording

 - eventsearch submenu added


Image

 - imageoptions


20 Introduction


◦OSDType.Title.SupportedLanguages parameter added


 - focus


◦SimplefocusSchedule added


Media

 - videoprofile


◦IsDPMProfile parameter added


 - speakervolume submenu added


Eventsources

 - proximitysensor submenu added


 - dtmf


◦HandoverIndex parameter added


 - mqttpublication, mqttsubscription submenu added


Eventstatus

 - New Events Added


◦ProximitySensor


◦MQTTSubscription


 - eventstatus


◦MQTTSubscription parameter added


Eventrules

 - dynamicrules


◦Rule.#.EventAction.#.MQTTMessageIndex parameter added


◦MQTTPublication enum value added to EventAction.#.Type parameter


◦MQTTSubscription enum value added to EventSource.#.Type parameter


 - dynamicrulesoptions


◦MQTTPublication enum value added to EventSource.#.ActionTypes and

AppEventSource.#.ActionTypes parameter


 - audiooutfiles


◦Name parameter added under control operation


◦SpeakerID parameter added under control operation


◦GroupID parameter adder under control operation


 - ttsfiles submenu added


AI

 - metaattributesearch


SUNAPI 21


◦async search support added


 - ocrsearch


◦async search support added


 - facerecognitionsearch


◦async search support added

### **2.3. Version 2.6.1**

**Date** : 2022-08-01


System

 - powermode submenu added


 - eventlog


◦Supported Type extended with DynamicRule


Media

 - metadatashare submenu added


 - cameradiscovery


◦ANALOG enum value added to Protocol parameter


PTZConfig

 - ptzsettings


◦MountPosition parameter added


Image

 - camera


◦ThermalVariationSensitivity parameter added


 - ptr


◦PanAngle parameter added to view response


◦TiltAngle parameter added to view response


 - privacy


◦AdjustMode parameter added


 - imagealignment


◦AlphaBlendingLevel parameter added


 - imageoptions


◦LCEMode.#.Top parameter added


◦LCEMode.#.Bottom parameter added


◦LCEMode.#.Left parameter added


22 Introduction


◦LCEMode.#.Right parameter added


 - thermalnuc submenu added


 - stereosensorcalibration


◦ZoomScale parameter added to view response


EventRules

 - dynamicrules


◦Rule.#.Status parameter added


◦Rule.#.EventSource.#.Type supported values updated


◦Rule.#.EventSource.#.AppName parameter added


◦Rule.#.EventSource.#.RuleIndexType parameter added


◦Rule.#.EventSource.#.RuleIndex parameter added


◦Rule.#.EventSource.#.Channel parameter added


◦Rule.#.EventSource.#.State parameter added


◦Rule.#.EventAction.#.Type parameter added


◦Rule.#.EventAction.#.AudioClipIndex parameter added


◦Rule.#.EventAction.#.HandoverIndex parameter added


 - dynamicruleoptions submenu added


 - schedulelist


◦Schedule.#.IsFixed parameter added


◦EveryDay Parameter added


◦EveryDay<h> parameter added


◦<dddh>.FromTo parameter added


◦EveryDay<h>.FromTo parameter added


Application programmers guide

 - pw_init cgi statuscheck submenu


◦MaxPasswordLength parameter added


IP Installer

 - RSA Key Response updated to include maximum password length supported

Device Type 0x07: LEDBox newly added

### **2.4. Version 2.6.0**

**Date** : 2022-01-24


System

 - systemimage submenu added.


SUNAPI 23


Network

 - tutk submenu deprecated.


 - p2p submenu added.


 - interface.


◦ICMPEnable parameter added.


Security

 - users


◦Optional current password verification support added.


◦New user authority option for Privacy area access added.


Image

 - multiimageosd


◦New parameters added to support the changing image position.


 - privacy


◦New parameters added to support the reordering mask index.


Media

 - videoinput submenu added.


 - videocodecinfo


◦MinFPS parameter added.


Event

 - ledindicator


◦EnableFlickeringAlarm parameter added


 - eventstatusschema submenu modified.


PTZ

 - exclusiveptzcontrol submenu added.

### **2.5. Version 2.5.9**

**Date** : 2021-08-09


Network

 - Sipsetup submenu added.


 - Nattraversal submenu added.


 - Sipaccount submenu added.


 - Siprecipients submenu added.


 - Sipcall submenu added.


24 Introduction


Security

 - 802Dot1x


◦ClientCertificateInUse parameter added.


◦CACertificateInUse parameter added.


 - ssl


◦Certificate.#.Issuer parameter added.


◦Certificate.#.SerialNumber parameter added.


◦Certificate.#.Signature parameter added.


◦Certificate.#.Thumbprint parameter added.


◦Certificate.#.IsEncrypted parameter added.


◦Certificate.#.Version parameter added.


 - rsa


◦PublicKeyFormat parameter added.


 - Cacertificate submenu added.


Media

 - Wisestream


◦AISupportEnable parameter added.


 - Videoprofile


◦IsEvenNumberFrameRateProfile parameter added.


◦IsVoIPProfile parameter added.


 - Videocodecinfo


◦VoIP profile resolution and bitrate parameters added.


 - Camera


◦SubShutterSpeedRatio parameter added.


◦PreferShutterAISupportEnable parameter added.


 - Imageoptions


◦MaxDISSensorFrameRate parameter added.


 - eqsettings


◦Removed because this submenu has been deprecated.


Transfer

 - ftp


◦ReportyFileType parameter added.


◦PreEventDuration and PostEventDuration parameter added.


SUNAPI 25


Eventrules

 - handover2


◦Action parameter added.


◦Query parameter added.


Eventsources

 - Videoanalysis2


◦DefinedArea.#.ObjectTypeFilterDetails parameter added.


◦Line.#.ObjectTypeFilterDetails parameter added.


 - Heatmap


◦AutoReference parameter added.


◦ManualModeEnable parameter added.


◦ManualReference parameter added.


 - Callrequest submenu added.


 - Dtmf submenu added.


 - Tamperswitch submenu added.


 - Objectdetection


◦ObjectTypeDetails parameter added.


◦HandoverIndex parameter added.


 - Metaimagetransfer


◦ImageQuality parameter added.


 - Socialdistancingviolation submenu added.


 - Indicationpass submenu added.


 - Ledindicator submenu added.


 - Parkingdetection submenu added.


Ptzcontrol

 - Digitalrtz submenu added.


 - Supportedptzactions submenu added.


Opensdk

 - Apps


◦Update action based on AppID added.


 - Metaframeschema submenu added.


 - Metaframecapability submenu added.


26 Introduction


### **2.6. Version 2.5.8**

**Date** : 2021-02-18


System

 - Deviceinfo


◦New Device type "IOBox" added


◦CameraRegistrationMode parameter added for recorder.


 - Geolocation submenu added


 - Clientregister submenu added


Network

 - Onvifdiscovery submenu added


 - Ssl submenu updated for self-signed certificate creation.


 - Camerausers


◦IsInitPasswordSet parameter added to view


Video

 - Slideshow submenu added


Media

 - Videooutput


◦Quadview type is added


 - Videoprofile


◦RTPMulticastType and RTPMulticastAddressIPv6 parameters added for configuring Ipv6 multicast

address to profile.


Image

 - Irled


◦LEDMaxPowerLevel and Zone.#.Level parameter added


 - Imagealignment


◦FovAngle parameter added


 - Imageoptions


◦LensModel.#.SupportLDCMode parameter added


 - Thermalpalettesetting


◦ThermalVariationSensistivity parameter added


 - Focuspreset submenu added


 - Stereosensorcalibration submenu added


 - Blackbodyconfig submenu added


SUNAPI 27


 - Blackbodyconfigoptions submenu added


 - Radiometrysettings submenu added


 - Radiometrysettingsoptions submenu added


Eventsources

 - Thermaldetectionmode submenu added


 - Bodytemperaturedetection submenu added


 - Temperaturemeasurementregion submenu added


 - Maskdetection submenu added


 - Cellmotion submenu added


 - Autotracking


◦ObjectFilterEnable and ObjectTypeFilter parameter added


Eventrules

 - Ioboxregister submenu added


Ptzcontrol

 - Areazoom


◦Profile parameter added


 - Aux


◦Activate status parameter added


Ptzconfig

 - Ptzsettings


◦ProportionalPTSpeed parameter added


 - Ptcorrection submenu added


Ai

 - Aiengine


◦Facerecognitionagreementtime and Agreementstatus parameter added

### **2.7. Version 2.5.7**

**Date** :2020-07-16


System

 - Deviceinfo


◦GUIVersion parameter added for Recoder


 - Date


◦DateFormat and Timeformat parameters added for Recorder


28 Introduction


 - Firmwareupdate


◦OnlineUpgrade parameter added for Recorder


 - Monitorout


◦Optimalresolution parameter added for Recorder


 - Peerconnectioninfo submenu added


Network

 - Interface


◦Interfacelabel parameter added


 - Snmptrap


◦UseCommunity parameter added


 - Dhcpserver and poestatus submenus added


Security

 - SSL


◦Clientcertificateauthentication and updatehostname parameters added


 - Users


◦Admin access privilege option added for normal users


 - Camerausers


◦Password encryption support added


 - Cameravalidationstatus, clienthttpsstatus, and tlsversion submenus added


Video

 - Thumbnail submenu added


Media

 - Videoprofile


◦Showall parameter added to show non-video profiles


 - Videocodecinfo


◦Compression level parameters added


 - Videoencoderinstances submenu added


Image

 - Camera submenu updated


 - Whitebalance


◦Whitebalance mode parameter added


 - Imageenhancements, imageenhacement2


◦LDCmode,xce,Disfocallength and gammacontrol parameters added


SUNAPI 29


 - Focus


◦Focuscontinuos and Zoomcontinuos parameters added


 - Iamgeoptions submenu updated


Eventsources

 - Videoanalysis2


◦Rulename and objectfilter parameters added


 - Tamperingdetection


◦Rulename parameter added


 - Defocusdetection


◦Rulename parameter added


 - Sourceoptions


◦Exclude area min and max index parameters added


◦Minimumareasizeinpixel parameter added


Eventrules

 - Dynamicrule and schedulelist submenus added


 - Handover, Handover2


◦Connectionmode parameter added for http/https


Io

 - Alarmoutput


◦IOPortindex parameter added for notifying the physical port index


 - Ioport submenu added for configurable IO


Ptzconfig

 - Digitalautotracking


◦Objecttype filter parameter added


Recording

 - General


◦Substream recording parameters added


 - Timeline


◦BkID parameter added for recorder (bookmark)


 - Bookmark and diskutility submenus added


Opensdk

 - Opensdkeventinfo


◦Type parameter added


30 Introduction


Ai

 - Metaattributesearch, ocrsearch, objectdetectfromimage, imagelibrary, facerecognitionsearch,

aiengine, and aitimeline submenus added

### **2.8. Version 2.5.6**

**Date** :2020-02-20


System

 - Deviceinfo


◦ActualDeviceTypeparameter added


 - Stratocast, Stratocastregister submenu added


 - Serial


◦DeviceId parameter added


 - Systemlog


◦Type parameter added


 - Storageinfo


◦IsSDCardEncrypted parameter added


◦NewDASPassword parameter added


◦IsNewDASPasswordEncrypted parameter added


◦IsDASEncryptable parameter added


◦DASPassword parameter added


◦IsDASPasswordEncrypted parameter added


Network

 - Interface


◦MTUSize parameter added


 - Ethstatus submenu added


Security

 - Camerausers submenu added


Media

 - Videosource


◦VideoType parameter added


◦Add/Remove actions added


 - Videooutput


◦RebootRequired parameter added


 - Streamurl


SUNAPI 31


◦RecordStreamType parameter added


 - Videocodecinfo


◦<EncodingType>.General.<Width>X<Height>.FrameLockMaxFPS added


◦<EncodingType>.Record.<Width>X<Height>.FrameLockMaxFPS added


 - Cameraregister


◦IsBypassSupported parameter added


◦VideoState, AudioState parameter added


Image

 - Camera


◦ImagePresetMode.#.BLCAreaCoordinates


◦ImagePresetMode.#.NormalizedBLC added


◦BLCAreaCoordinates parameter added


◦NormalizedBLCLevel parameter added


 - Ptr


◦Mode parameter added


 - Ptrpreset submenu added


 - Imageoptions


◦BLCAreaCoordinates-based parameter added


◦OSDType.Title.SupportedSpecialCharacters parameter added


◦BacklightType-based parameter added


◦MaxWDRSensorFrameRate parameter added


 - directionindicator, noisereduction submenus added


Eventsources

 - Overspeed submenu added


 - Tamperingdetection


◦ChannelIDList parameter added


 - Temperaturechangedetection


◦TemperatureChange.ROI.#.HandoverIndex parameter added


 - Boxtemperaturedetection


◦ROI.#.HandoverIndex parameter added


Eventrules

 - Rules


◦Support for PeopleCount added


32 Introduction


Eventstatus

 - Support for OpenSDK event added


 - Eventstatus


◦Support for EventFilter monitoridff added


 - Metadataschema


◦EventName parameter added


Ptzcontrol

 - Osdmenu, Rs485Command submenus added


Ptzconfig

 - Panzeroposition submenu added


 - Ptzprotocol


◦Status parameta added


Opensdk

 - Apps, Debug, Appstatus, Manifest


◦Channel parameter added


 - Opensdkeventinfo submenu added


Display

 - videooutlayout and spoutout submenus added

### **2.9. Version 2.5.5**

**Date** :2019-01-20


System

 - Deviceinfo


◦ONVIFVersion parameter added


 - Serial


◦Serialinterface parameter is added


 - Storageinfo


◦DasPassword support is added


 - Usbconfig


◦Enable parameter added


Network

 - Rtspovertls submenu added


Media


SUNAPI 33


 - Videosource


◦VideoMode & Sensorcapturesize support list extended


 - Videosourceoptions


◦Sensorcapturesize support extended


 - Videoprofile


◦Isfixedframerateprofile parameter added


 - Cameraregister


◦Camchannel parameter added


 - Cameraconnection


◦Camchannel parameter added


Image

 - Camera


◦ImagePresetMode based settings added


 - Whitebalance


◦ImagePresetMode based settings added


 - Imageenhancements2 submenu added


 - Ssdr


◦Imagepresetmode based settings added


 - Focus


◦Imagepresetmode based settings added


 - Overlay


◦Imagepresetmode based settings added


 - Multilineosd


◦Imagepresetmode based settings added


 - Imageoptions


◦AgcMode and Imagepresetmode parameter added


 - Autoimagealignment submenu added


 - Imagepreset2 submenu added


 - Imagepresetschedule submenu added


 - Thermalpalletesetting submenu added


 - Thermalpalletesettingoptions submenu added


 - Spottemperaturereading submenu added


Transfer

 - Dataserver submenu added


34 Introduction


Eventsources

 - Videoanalysis2


◦Roi based Duration support added


◦Defined area intrusion duration added


◦DetectionResult overlay support added


 - Wiperhousing submenu added


 - SoureOptions


◦Eventsource expanded for BoxTemperature detection


◦Eventaction expanded for AudioClip playback


 - Boxtemperaturedetection submenu added


 - Boxtemperaturedetectionoptions submenu added


Eventrules

 - Rules


◦Support for boxtemperaturedeteciton and audioclip added


 - Audiooutfiles submenu added


 - Internalhandovercalibration submenu added


 - Audiooutfileschedule submenu added


Eventstatus

 - Eventstatus


◦Support for BoxTemperatureDetection,HousingTampering, WaterLevelWarning added


 - Metadataschema submenu added


 - Eventstatusschema submenu added


Ptzconfig

 - Presetimageconfig


◦OpticalDefogFilterEnable parameter added


 - Presetvideoanalysis2


◦ROI duration and Defined area instrusionduration support added


 - Ptzsettings


◦Imagepresetmode support added


Recording

 - Timeline


◦Boxtemperaturedetection event support added


SUNAPI 35


### **2.10. Version 2.5.4**

Date:2018-08-07


System

 - Deviceinfo


◦DeviceReady and DeviceMode parameters added


 - Date


◦LastSyncTime, Week, DSTStart, DSTEnd, TimeZone and ActivateServer parameters added


 - Storageinfo


◦SDCardEncryption parameter added


 - Added holday, hddalarm, raid, monitorin and monitorout submenus


Network

 - Added dhcpclients submenu


Media

 - Videosource


◦RemoteName, VideoType and VideoMode parameters added


 - Added videosourceoptions and eqsettings submenus


 - Videoprofile


◦H264.MinDynamicFPS parameter added


 - Audioinput


◦NoiseReduction and NoiseReductionSensitivity parameters added


 - Videocodecinfo


◦AllProfiles parameter added


 - Added Cameraregister, Autoregister and Cameradiscovery submenus


 - Camerapasswordchange


◦OldPassword and IsPasswordEncrypted parameters added


 - Added Cameraconnection submenu


Image

 - Camera


◦LensModel, TemperatureUnit, ThermalColorPalette, ExposureControlSpeed parameters added


◦DayNightMode extended with ScheduleBW


 - Focus


◦AutoFocusRange parameter added


 - Imageoptions


36 Introduction


◦CompensationMode.#.SensorCaptureFrameRate.#.DefaultMaxShutterSpeed


◦and CompensationMode.#.SensorCaptureFrameRate.#.DefaultMinShutterSpeed parameters

added


Eventsources

 - Videoanalysis2


◦ROI.#.HandoverIndex, DefinedArea.#.HandoverIndex and Line.#.HandoverIndex parameters

added


 - Audioanalysis


◦ConfigurationToken and HandoverIndex parameters added


 - Facedetection


◦DynamicArea parameter added


 - Heatmap


◦Resolution parameter added


 - Tamperingdetection


◦HandoverIndex parameter added


 - Sourceoptions


◦ROIIncludeMinIndex, ROIIncludeMaxIndex,


◦ROIExcludeMinIndex, ROIExcludeMaxIndex, DefinedAreaIncludeMinIndex,


◦DefinedAreaIncludeMaxIndex, DefinedAreaExcludeMinIndex and


◦DefinedAreaExcludeMaxIndex parameters added


 - Added temperaturechangedetection, temperaturechangedetectionoptions and

shockdetection submenus


Eventactions

 - Complexaction parameter added


Eventrules

 - Rules


◦EventSource enum extended with ShockDetection


 - Added handover2 submenu


Eventstatus

 - Eventstatus


◦Channel.#.EventType parameter extended with ShockDetection,

TemperatureChangeDetection


Ptzcontrol

 - Continuous


SUNAPI 37


◦ViewModeType parameter added


 - Stop


◦ViewModeType parameter added


Ptzconfig

 - Presetimageconfig


◦AutoFocusRange parameter added


 - presetvideoanalysis2


◦ROI.#.HandoverIndex, DefinedArea.#.HandoverIndex and Line.#.HandoverIndex parameters

added


 - Ptzsettings


◦SpeedType parameter added


 - Ptlimits


◦DaysAfterReboot and StartTime parameters added


 - Ptzprotocol


◦ConnectionPortType parameter added


Recording

 - Timeline


◦Type and Channel.#.Result.#.Type parameters extended withShockDetection,

TemperatureChangeDetection


Display

 - Added layout, decoderboardinfo, wall, sequence and favorite submenus

### **2.11. Version 2.5.3**

**Date** : 2017-09-15


System

 - Added power, iscsidiscovery and sdcardinfo submenus


 - Deviceinfo


◦RequestedClientIPAddress parameter added


 - Date


◦SyncType enum extended with GPS


 - Serial


◦Signaltermination parameter added


 - Systemlog


◦GsensorEvent and GPSDisconnect event added


38 Introduction


 - Eventlog


◦QueueEvent added


 - Profileaccesinfo


◦Channel-based profilenamelist and currentbitrate parameters added


 - Databasereset


◦Datatype extended with QueueEvents


 - Storageinfo:


◦IsNASPasswordEncrypted and IsCHAPPasswordEncrypted added


 - digitalsignage:


◦IsFTPPasswordEncrypted added


Network

 - Added Mts and wifi submenus


 - Interface


◦InterfaceType extended with WIFI


◦IsPPoEPAsswordEncrypted parameter added


 - Dynamicdns


◦IsPublicPasswordEncrypted parameter added


 - Snmp


◦IsPasswordEncrypted parameter added


Security

 - Added rsa submenu


 - 802Dot1x


◦IsEAPOLPasswordEncrypted parameter added


 - Additionalpassword


◦IsPasswordEncrypted parameter added


 - Users


◦IsPasswordEncrypted parameter added


 - Usergroups


◦EventMenuAccess extended with Gsensor


◦NetworkMenuAccess extended with MTS


Media

 - Added setsynchronizationpoint submenu


 - Videosource


SUNAPI 39


◦Videosourcetoken parameter added


 - Videooutput


◦Channel parameter added


 - Videoprofile


◦Viewmodetype extended with QuadView.# parameter.


 - Multicast


◦Channel parameter added


 - Mediaoptions


◦Viewmodetype extended with QuadView.# parameter.


 - Videocodecinfo


◦Viewmode extended with QuadView.#


Image

 - Added ptr, ptrzusage, scheduler and flangeback submenus


 - Camera


◦LensModel and IrisMode parameters added


 - Focus


◦ImagePreview parameter added


◦IRShift parameter added


◦Temperature compensation enable added


 - Fisheyelens


◦RPLnumber parameter added


◦LensModel parameter enum extended with BoowonOpticals


 - Fisheyesetup


◦LensModel parameter enum extended with BoowinOpticals


◦ViewModeType parameter enum extended with QuadView.#


 - Multilineosd


◦OSDBlink parameter is added


◦ViewModeType parameter enum extended with QuadView.#


 - Viewmodes


◦ViewMode.#.Type parameter enum extended with QuadView.#


 - Imageoptions


◦ViewModeType parameter enum extended with QuadView.#


Transfer

 - ftp


40 Introduction


◦IsPasswordEncrypted parameter added


 - Smtp


◦IsPasswordEncrypted parameter added


 - http


◦IsPasswordEncrypted parameter added


◦IsProxyPasswordEncrypted parameter added


Eventsources

 - Added Peoplecount, Heatmap and QueueManagement and gsensor submenus


 - Facedetection


◦Overlaycolor parameter is added


 - Sourceoptions


◦Extended the enum with peoplecount, heatmap and queuemanagement.


Eventactions

 - Added Complexaction submenu


 - Smtp


◦Supported enum in Systemevent extended with EmergencyTrigger and gsensor


Eventrules

 - Handover


◦IsPasswordEncrypted parameter added


Eventstatus

 - Added Eventscheme submenu


 - QueueEvent support added to Channel.#.Eventype


 - EmergencyTrigger, InternalHDDWarmup, GSensorEvent, GPSDisconnect, WiFiSignalChanged added to

Systemevent


Ptzconfig

 - Presetimageconfig


◦Gamma, Control, LDCEnable, LDCMode, LDCLevel, SSNRMode, SSNR2DLevel, SSNR3DLevel

parameters added


 - Ptzsettings


◦Imagepreview parameter added


 - Ptlimits


◦Channel, TiltRange parameter added


Recording

 - Added queuesearch submenu added


SUNAPI 41


 - General


◦Recordoverlap extended support for FogDetection, AudioAnalysis, EmergencyTrigger,

GSensorEvent


 - Timeline


◦Type parameter extended for QueueEvent, Videoloss, EmergencyTrigger, InternalHDDWarmup,

GSensorEvent


Opensdk

 - Added Debug submenu

### **2.12. Version 2.5.2**

**Date** : 2017-05-15


System

 - Added logserver and sessioninfo submenu


 - systemlog


◦Added DatabaseRemove, USBWIFIConnect, and USBWIFIDisconnect to Type


 - eventlog


◦Added FogDetection and AudioAnalysis to Type


 - firmwareupdate


◦Added check action


Network

 - Added tutk submenu


Media

 - Added mediaoption submenu


 - videoprofile


◦Added CropRatio


◦Added MJPEG.PriorityType


◦Added H264.DynamicFPSEnable


◦Added H265.DynamicFPSEnable


 - videocodecinfo


◦Added <EncodingType>.General.<Width>X<Height>.DefaultFPS


◦Added <EncodingType>.Record.<Width>X<Height>.DefaultFPS


◦Added <EncodingType>.Email.<Width>X<Height>.DefaultFPS


◦Added <EncodingType>.DigitalPTZ.<Width>X<Height>.DefaultFPS


◦Added <EncodingType>.General.<ViewMode>.<Width>X<Height>.DefaultFPS


42 Introduction


◦Added <EncodingType>.DigitalPTZ.<ViewMode>.<Width>X<Height>.DefaultFPS


◦Added <EncodingType>.Record.<ViewMode>.<Width>X<Height>.DefaultFPS


◦Added <EncodingType>.Email.<ViewMode>.<Width>X<Height>.DefaultFPS


Image

 - camera


◦Added On and Off values to HLCMode


◦Added Black, Blue, Red, Cyan, and Magenta values to HLCMaskColor


◦Added HLCDim


◦Added HLCAreaTop


◦Added HLCAreaBottom


◦Added HLCAreaLeft


◦Added HLCAreaRight


◦Added PreferedShutterSpeed


◦Added SSNR2DLevel


◦Added SSNR3DLevel


◦Added WDRSeamlessTransition


◦Added WDRLowLight


◦Added WDRIRLEDEnable


 - imageenhancements


◦Added control action


◦Added Contrast


◦Added LDCEnable


◦Added LDCMode


◦Added LDCLevel


 - imageoptions


◦Added LeftHalfView and RightHalfView values to ViewModeType


◦Added TopLeftCoordinates


◦Added BottomRightCoordinates


◦Added CompensationMode.#.DefaultAutoShortShutterSpeed


◦Added CompensationMode.#.DefaultAutoLongShutterSpeed


◦Added CompensationMode.#.SensorCaptureFrameRate.#.DefaultPreferShutterSpeed


◦Added CompensationMode.#.SensorCaptureFrameRate.#.AutoShortShutterSpee


◦Added CompensationMode.#.SensorCaptureFrameRate.#.AutoLongShutterSpeed


◦Added CompensationMode.#.SensorCaptureFrameRate.#.PreferShutterSpeed


SUNAPI 43


Recording

 - Timeline


◦Added FogDetection and AudioAnalysis to Type


◦Added DefocusDetection, FogDetection, and AudioAnalysis to Channel.#.Result.#.Type


PTZ

 - Added ptzmode submenu


Event

 - Added videoanalysis2 submenu under eventsources.cgi


 - Added audioanalysis submenu under eventsources.cgi


 - Added fogdetection submenu under eventsources.cgi


 - Added samples submenu under eventsources.cgi


 - Added pushnotification under eventstatus.cgi


 - facedetection


◦Added DetectionArea.#.Mode


 - tamperingdetection


◦Added DarknessDetection, Duration, SensitivityLevel, and ThresholdLevel parameters


 - defocusdetection


◦Added Duration, ThresholdLevel, and AutoSimpleFocus parameters


 - heatmap


◦Added the check action


 - eventrules.cgi


◦Added FogDetection,and AudioAnalysis values to EventSource


 - eventstatus.cgi


◦FogDetection, SDFormat, SDFail, SDFull, SDInsert, AudioAnalytics, and USBWIFIConnect to

Channel.#.EventType


OpenSDK

 - Changed ApplicationSessionID to ApplicationSessionId

### **2.13. Version 2.5.1**

**Date** : 2016-09-30


System

 - Added databasereset submenu


 - Systemlog


◦New Type (databasefull) added


44 Introduction


Media

 - Videoprofilepolicy


◦Added Channel


 - streamuri


◦DeviceID added


◦Profiletoken added


 - Videoprofile


◦Added IsDigitalPTZProfile


◦Added Bitrate


◦Added H264.BitrateControlType


◦Added H265.BitrateControlType


◦Added MPEG4.BitrateControlType


◦Added ViewModeIndex


◦Added ViewModeType


 - Videocodecinfo


◦ChannelIDList added


◦ViewMode added


◦MaxUnknownTargetBitrate added


◦MinUnknownTargetBitrate added


◦<EncodingType>.IsDigitalPTZSupported


◦Viewmode based resolution and fps added


Network

 - Portconf


◦ProtocolType added


 - Added Standbydeviceinfo submenu


Eventsources

 - Added Heatmap submenu


 - Added peoplecount submenu


 - Added autotracking submenu


Recording

 - Added Posconf submenu


 - Added poseventconf submenu


 - Added posdata submenu


 - Added poscalendar submenu


SUNAPI 45


 - Timeline


◦PrimaryDeviceIPAddress added


 - Added metadata submenu


 - Calendarsearch


◦PrimaryDeviceIPAddress added


◦IgnoreChannelBasedResults added


◦Result added


 - Searchrecordingperiod


◦ResultsInUTC added


 - Storage


◦Channel added


 - Added smartsearch submenu


 - Heatmapsearch


◦ResultImageType added


◦ResultAsImage added


 - Added peoplecountsearch submenu


Security

 - Usergroups


◦DeviceMenuAccess added


 - Added Additionalpassword submenu


PtzControl

 - SubViewIndex parameter added for all ptz operations


EventStatus

 - Eventstatus


◦Pos EventType added


Image

 - Privacy


◦Channel Added


◦Mode added


◦Mask Index added


◦Mask Coordinates added


 - Viewmodes


◦ViewMode Type added


46 Introduction


 - Focus


◦Mode added


 - Fisheyelens


◦LensModel added


 - Added Fisheyesetup submenu


 - Added Imagealignment submenu


 - Added imageoptions submenu


Eventrules

 - Handover


◦PresetIndex added


 - Added scheduler submenu


Ptzconfig

 - Preset


◦SubViewIndex added


 - PtzSettings


◦RememberLastPosition and RememberLastPositionduration added

### **2.14. Version 2.5.0**

**Date** : 2016-06-20


**NOTE** JSON response support added


System

 - Device Information


◦Added Memo


 - Firmwareupdate


◦Added IgnoreMultipartResponse


 - OnvifFeature


◦Added FocusControl


Network

 - Added portconf submenu


Media

 - Videoprofile


◦Added IsFixedProfile


◦Added H264.DynamicGOVLength


SUNAPI 47


◦Added H265.DynamicGOVLength


 - Videocodecinfo


◦Added <encodingtype>.Record.<width>X<height>.DefaultCBRTarget


◦Added <encodingtype>.Record.<width>X<height>.DefaultVBRTarget


◦Added <encodingtype>.DigitalPTZ.<width>X<height>.Width


◦Added <encodingtype>.DigitalPTZ.<width>X<height>.Height


◦<EncodingType>.DigitalPTZ.<Width>X<Height>.MaxFPS


◦<EncodingType>.DigitalPTZ.<Width>X<Height>.MinCBRTargetBitrate


◦<EncodingType>.DigitalPTZ.<Width>X<Height>.MaxCBRTargetBitrate


◦<EncodingType>.DigitalPTZ.<Width>X<Height>.DefaultCBRTargetBitrate


Image

 - Camera


◦Added SSNRMode


◦Added ImagePreview


 - Whitebalance


◦Added ImagePreview


 - Imageenhancements


◦Added ImagePreview


 - Irled


◦Added Mode


◦Added ImagePreview


 - SSDR


◦Added Imagepreview


 - Focus


◦Added FastAutoFocus


 - Overlay


◦Added ImagePreview


 - Privacy


◦Added CommonMaskColor


 - Added fisheyesetup submenu


 - Added multiimageosd submenu


 - Added multilineosd submenu


 - Added imageoptions submenu


 - Imagepreset


48 Introduction


◦Added imagepreview


◦Added Mode


◦Added Schedule.#.Mode


Eventsources

 - Added defocusdetection submenu


 - Added Sourceoptions submenu


 - Audiodetection


◦Added check action


 - Rules


◦Added eventsource


Eventrules

 - Added handover submenu


Eventstatus

 - Eventstatus


◦Profile.#.DigitalAutoTracking added


Ptz

 - Continuous


◦Added IgnoreIfBusy


◦Added digitalautotracking submenu

### **2.15. Version 2.4.3**

**Date** : 2016-05-15


System

 - Eventlog


◦Type: added Defocusdetecion, TrackingStart and TrackingEnd.


Media

 - Videoprofile


◦IsDigitalPTZProfile added


Image

 - Focus


◦Channel added for NVR


◦Mode added for NVR


EventStatus


SUNAPI 49


 - Eventstatus


◦New eventtypes added (DefocusDetection and Tracking added)


Recording

 - General


◦RecordOverlap (DefocusDetection and Tracking added)


 - Timeline


◦Type(DefocusDetection and Tracking added)


 - Added Smartsearch submenu

### **2.16. Version 2.4.2**

**Date** : 2016-01-30


System

 - Added vehicleinformation submenu


Network

 - DNS


◦Interfacename added


 - Dynamicdns


◦Interfacename added


Media

 - Streamuri


◦Eventsearchtype added


Eventstatus

 - Eventstatus


◦New eventtypes added (SDFail and SDFull added)


Eventactions

 - Smtp


◦SystemEvent added


◦RecipientGroupID.#.SystemEvent added


Ptzcontrol

 - Added Aux submenu


Recording

 - Storage


◦Channel added


50 Introduction


 - Timeline


◦EventSearchType added

### **2.17. Version 2.4.1**

**Date** : 2015-03-28


System

 - Added gps submenu


 - Added autobackup submenu


 - Added digitalsignage submenu


Network

 - Interface


◦Added IPv4SubnetMask


 - Dns


◦Added IPType


Security

 - Usergroups


◦DeviceMenuAccess Added


Media

 - Videoprofilepolicy


◦LiveMode added


 - Videoprofile


◦H265.BitrateControlType added


◦H265GoveLength added


◦H265.Profile added


◦H265.EntropyCoding added


◦H265.SmartCodecEnable added


 - Added camerapasswordchange submenu


Image

 - Imageenhancements


◦LDCEnable added


◦LDCLevel added


 - Flip


◦Rotate added


SUNAPI 51


Transfer

 - ftp


◦Status added


 - Smtp


◦Status added

### **2.18. Version 2.4.0**

**Date** : 2014-02-28


System

 - Device Information


◦Added MicomVersion


 - Date and Time


◦Added NTPStatus and NTPLastUpdatedTime


 - Factory Reset


◦Added the ‘None’ value to ExcludeSettings


 - Storage Information


◦Added SlotNumber, Storage.#.Usage, Storage.#.Model, and Storage.#.Temperature, TargetIP, Port,

TargetIQN, CHAPUserID, and CHAPPassword


Network

 - Added svp submenu (15 SVP)


 - Added bandwidth submenu (16 Bandwidth)


 - Network Interface


◦Added IsDefaultGateway, and HostName


 - DNS


◦Added Type


 - DDNS


◦Added SamsungQuickConnectStatus


 - SNMP Trap Settings


◦Added Trap.#.LinkDown and Trap.#.WarmStart


 - RTSP


◦Added MobilePort


Security

 - Added usergroups submenu (8 User Group Configuration)


 - Added authority submenu (9 Authority)


52 Introduction


 - IP Address Filtering


◦Added IPType for the set action


 - 802.1x


◦Added InterfaceName for the install and remove actions


 - User Configuration


◦Added UserName, ViewerAccess, GroupID, and UserLevel


Video/Audio

 - Added sessionkey submenu (2.10 Session Key)


 - Video Source


◦Added Name, and State


 - Video-Profile Policy


◦Added NetworkProfile and LiveProfile


 - Stream URI


◦Added ClientType


Event

 - Added networkalarminput submenu (2.9 Network Alarm Input)


 - Added smtp submenu of eventactions.cgi (3.1 Email Sending)


 - Added complexaction submenu of eventactions.cgi (3.2 Complex Action)


 - Event Status


◦Added SystemEvent for the check action


Transfer

 - Added smtpusers submenu (4 SMTP Users)


 - Added smtpgroups submenu (5 SMTP User Groups)


PTZ

 - Continuous PTZ Operation Control


◦Added Iris


 - Stop Control


◦Added ‘Pan’, ‘Tilt’ and ‘Zoom’ values to OperationType


I/O

 - Added alarmreset submenu (5 Alarm Reset)


 - Alarm Output


◦Added AlarmOutput.#.<dddh>


Recording


SUNAPI 53


 - Added manualrecording submenu(6 Manual Recording)


 - Added searchrecordingperiod submenu (9 Recording Period)


 - Added heatmapsearch submenu (10 Heat Map Search)


 - Storage


◦Added DiskEndBeep


 - General


◦Added FullFrameBandwidth, FullFrameRate, KeyFrameBandWidth, KeyFrameRate, Codec,

RecordOverlap, SourceProfile, Resolution, FrameRate, CompressionLevel, AudioEnable, and

BitrateLimit


 - Recording Schedule


◦Added the ‘enum’ to value type <ddd>, EveryDay, <dddh>, and EveryDay<h> for NVR


 - Timeline


◦Added the ‘UserInput’ value to Channel.#.Result.#.Type

### **2.19. Version 2.3.2**

**Date** : 2014-12-12


System

 - Device Information


◦Added OpenSDKVersion


 - Storage Information


◦Added Storage.#.Status


Network

 - SNMP Trap Settings


◦Added p.#.AlarmInput.#, Trap.#.AlarmOutput.#, and Trap.#.TamperingDetection


Security

 - 802.1x Setup


◦Added EAPOLType


Video/Audio

 - Stream URI


◦Added OverlappedID


Image

 - Camera


◦Added the ‘Off’ and’ On’ values to AFLKMode


◦Added the ‘P-Iris-SLAM2890PN’ value to IrisMode


54 Introduction


◦Added AGCLevel


 - White Balance


◦Added the ‘Mercury’ and ’Sodium’ values to WhiteBalanceMode


 - Focus


◦Added Channel and FocusAreaCoordinate for the Control action


 - Overlay


◦Added AzimuthEnable


 - Privacy


◦Added MaskIndex, MaskPattern, and ZoomThresholdEnable


 - Image Preset


◦Added the ‘UserPreset ‘ value to Mode


◦Added the ‘Off’ and’ UserPreset’ values to Schedule.#.Mode


Event

 - Video Analytics Setup


◦Added the ‘Off’ value to EntireAreaMode


◦Added DetectionType for the view action


 - Event Status


◦Added Aux for check, monitor, and monitordiff actions


PTZ

 - Requesting Camera’s Position Information


◦Added ZoomPulse and Iris


 - Preset Image Configuration


◦Added AfterActionTrackingTime and AFLKMode


◦Added the ‘Off’ and ’VideoAnalytics’ values to AfterAction


◦Added the ‘Mercury’ and ’Sodium’ values to WhiteBalanceMode


 - Preset Video Analysis Setup


◦Added ROI.#.Coordinate and ROIMode


 - PTZ Settings


◦Added DigitalPTZEnable, and NorthDirection


Recording

 - Added overlapped submenu (Chapter 5 Overlapped Recording)


 - Storage


◦Added AutoDeleteEnable and AutoDeleteDays


SUNAPI 55


 - Timeline


◦Added the ‘UserInput’value to Type and Channel.#.Result.#.Type


◦Added OverlappedID

### **2.20. Version 2.3.1**


**NOTE** Internal release


Video/Audio

 - Video Profile


◦Added ViewModeIndex


 - Video Codec Info


◦Added ViewMode


◦Added <EncodingType>.General.<ViewMode>.<Width>X<Height>.Width,

<EncodingType>.General.<ViewMode>.<Width>X<Height>.Height,

<EncodingType>.General.<ViewMode>.<Width>X<Height>.MaxFPS,

<EncodingType>.General.<ViewMode>.<Width>X<Height>.MaxCBRTargetBitrate,

<EncodingType>.General.<ViewMode>.<Width>X<Height>.MinCBRTargetBitrate,

<EncodingType>.General.<ViewMode>.<Width>X<Height>.DefaultCBRTargetBitrate,

<EncodingType>.General.<ViewMode>.<Width>X<Height>.MaxVBRTargetBitrate,

<EncodingType>.General.<ViewMode>.<Width>X<Height>.MinVBRTargetBitrate,

<EncodingType>.General.<ViewMode>.<Width>X<Height>.DefaultVBRTargetBitrate


Image

 - Added the fisheyelens submenu


 - Added the viewmodes submenu


Event

 - Event Status


◦Added IncludeTimestamp and Timestamp for check, monitor, and monitordiff actions


PTZ

 - Absolute Position Control


◦Added ViewModeIndex and SubViewIndex


 - Relative Position Control


◦Added ViewModeIndex and SubViewIndex


 - Continuous PTZ Operation Control


◦Added ViewModeIndex


 - Requesting Camera’s Position Information


◦Added ViewModeIndex and SubViewIndex


56 Introduction


 - Moving to Preset Position


◦Added ViewModeIndex


 - Group Control


◦Added ViewModeIndex


 - Moving to Home Position


◦Added ViewModeIndex


 - Stop Control


◦Added ViewModeIndex


 - Movement Control


◦Added ViewModeIndex


 - Group Setup


◦Added ViewModeIndex


 - Home Position Setup


◦Added ViewModeIndex


 - Preset Configuration


◦Added ViewModeIndex

### **2.21. Version 2.3.0**


**NOTE** Internal release


System

 - Device Information


◦Added PasswordStrength


 - Event Log


◦Added the ‘OpenSDK’ and ‘PTZMotion’ values to Type


 - Profile Access Information


◦Added the ‘Optimized’ value to User.#.ClientNetworkConnectionStatus


Video/Audio

 - Video Profile


◦Added ATCTrigger and ATCEventType


Event

 - Auto Tracking


◦Added the TrackingAreas parameter to the view action


◦Added the TargetLockCoordinate parameter to the control action


SUNAPI 57


◦Added the TrackingAreaEnable parameter to the set action


◦Added Channel, TrackingAreaID, Coordinate parameters to the add action


◦Added Channel and TrackingAreaID to the remove action


 - Alarm Input


◦Changed Alarminput.#.Enable to AlarmInput.#.Enable


 - Event Rules


◦Added the ‘OpenSDK’ and ‘UserInput’ values to EventSource


 - Event Status


◦Added the 'PTZMotion', 'UserInput' values to Channel.#.EventType for the check, monitor, and

monitordiff actions


Image

 - Camera


◦Deleted the ‘Off’ value from AFLKMode


PTZ

 - Auto Run Setup


◦Added the ‘Schedule’ value to Mode of the set action


◦Added the SwingMode parameter to the set action


◦Added the update action including the Channel, ScheduleMode, FromTo, Preset, Group, Trace,

AutoPanSpeed, AutoPanTiltAngle, Tour, and SwingMode parameters


 - Preset Image Configuration


◦Added the DefogMode and DefogLevel parameters


◦Changed the ‘OneShot’ value of FocusMode to ‘OneShotAutoFocus’


 - Preset Video Analysis Setup


◦Added MinimumObjectSizeInPixels, MaximumObjectSizeInPixels, IVRuleType,

DetectionResultOverlay, and DisplayRules parameters


 - PTZ Settings


◦Added the ProportionalPTSpeedMode parameter


I/O

 - Added the UserInput submenu (4 User Input State)


Recording

 - Timeline


◦Added the ‘UserInput’ value to Type


Open SDK

 - Added opensdk.cgi with the apps, appstatus, and manifest submenus


58 Introduction


### **2.22. Version 2.2.1**

**NOTE** Internal release


**Date** : 2014-01-17


System

 - 2 Device Information


◦Added PTZBoardVersion, InterfaceBoardVersion, and TrackingVersion


 - 3 Date and Time


◦Added NTPURLList


 - 5 System Log


◦Added the ‘NASFormat’, ‘NASFail’, ‘NASFull’, ‘NASConnect, and ‘NASDisconnect’ values to Type


 - 7 Event Log


◦Added the ‘Tracking’ value to Type


 - 11 Firmware Update


◦Added Status, FirmwareModule, and Progress


 - 14 Storage Information


◦Added Storage.#.UsedSpace, Storage.#.TotalSpace, Storage.#.Type, Storage, Enable, DefaultFolder,

NASIP, NASUserID, NASPassword, Status, and Mode parameters


Network

 - Removed submenus - arping, upnpnat


 - 2 Network Interface


◦Removed AutoIPv6Address, IsDefaultGateway, HostName, DomainName, and

IPv6RouterAdvertisement


◦Added ‘Default’ value to IPv6Type


◦Removed the InterfaceType value


◦Removed value ranges for IPv4PrefixLength and IPv6PrefixLength


 - 3 DNS


◦Removed Type and SearchDomainList


 - 4 DDNS


◦Removed ‘www.changeip.org’ value from PublicServiceEntry


◦Eliminated maximum value length for SamsungProductID, PublicHostName, PublicUserName, and

PublicPassword


 - 5 Bonjour


◦Eliminated maximum value length for FriendlyName


SUNAPI 59


 - 6 UPnP Discovery


◦Eliminated maximum value length for FriendlyName


 - 8 SNMP Setup


◦Eliminated maximum value length for ReadCommunity, WriteCommunity, and UserPassword


 - 10 QoS Setup


◦Removed value ranges for Index, PrefixLength, and DSCP


 - 13 RTSP


◦Changed values ‘0’ and ‘60’ to ‘0s’ and ‘60s’ for Timeout


Security

 - 2 IP Address Filtering


◦Removed value ranges for IPIndex and Mask


 - 3 802.1x Setup


◦Removed value of Status


◦Eliminated maximum value length for EAPOLId and EAPOLPassword


 - 7 Configuring Users


◦Eliminated maximum value length for UserID, Index, and Password


Video/Audio

 - 2.1 Snapshot


◦Changed ProfileID to Profile


◦Removed value range for Profile


 - 2.2 Stream


◦Added the Resolution parameter


◦Changed ProfileID to Profile


◦Removed value ranges for Profile, FrameRate, and CompressionLevel


 - 2.3 Video Source


◦Added value ‘20’ to SensorCaptureFrameRate


 - 2.5 Video-Profile Policy


◦Removed value ranges for DefaultProfile, EventProfile, and RecordProfile


 - 2.6 Video Profile


◦Added MPEG4.BitrateControlType, MPEG4.GOVLength MPEG4.PriorityType, and

H264.SmartCodecEnable


◦Removed the value for Resolution


◦Removed value ranges for Profile, Name, ATCLimit, SVNPMulticastTTL, RTPMulticastTTL,

CropAreaCoordinate, FrameRate, CompressionLevel, Bitrate, and H264.GOVLength


60 Introduction


 - 2.7 Audio Input


◦Added the value to SampleRate


 - 2.8 Audio Output


◦Added the value to SampleRate


 - 2.9 Stream URI


◦Removed OverlappedID


◦Removed value range for Profile


 - 2.10 Multicast


◦Removed value range for Profile


 - 2.11 Video Codec Info


◦Added Profile parameter


Image

 - Added the following submenus


◦irled (Chapter 5 IR LED)


◦smartcodec (Chapter 10 Smart Codec)


◦fisheyelens (Chapter 12 Fisheye Lens)


◦imagepreset (Chapter 13 Image Preset)


 - 2 Camera


◦Added HLCMode, HLCLevel, HLCMaskTone, HLCMaskColor, WDRLimit, WDRBlackLevel,

WDRWhiteLevel, ShutterMode, ManualShutterSpeed, DayNightModeSchedule.EveryDay,

DayNightModeSchedule.EveryDay.FromTo, DayNightSwitchingTimeColorToBW,

DayNightSwitchingBrightnessColorToBW, DayNightSwitchingTimeBWToColor,

DayNightSwitchingBrightnessBWToColor, NegativeModeEnable, SensUpMode, and SensUpLevel

parameters


◦Removed the values from AutoLongShutterSpeed, AutoShortShutterSpeed,

DayNightSwitchingTime and IrisFno


◦Removed value ranges for BLCAreaTop, BLCAreaBottom, BLCAreaLeft, BLCAreaRight, and

SSNRLevel


◦Added values ‘P-Iris-SLAM3180PN’ and ‘P-Iris-M13VP288IR’ to IrisMode


 - 3 White Balance


◦Added values ‘ATW1’, ‘ATW2’, ‘3200K’, and ‘5600K’ to WhiteBalanceMode


◦Removed value ranges for WhiteBalanceManualRedLevel and WhiteBalanceManualBlueLevel


 - 4 Image Enhancement


◦Removed value ranges for SharpnessLevel, Brightness, Gamma, Saturation, and DefogLevel


◦Added CAR


 - 7 SSDR


SUNAPI 61


◦Removed value range for Level


 - 8 Focus


◦Added Mode, ZoomTrackingMode, ZoomTrackingSpeed, and LensResetSchedule of set action and

Zoom of the control action


◦Removed value from Focus


 - 9 Overlay


◦Added PTZPositionEnable, CameraIDEnable, PresetNameEnable, and OSDColor


◦Removed value ranges for Title, TitlePositionX, and TitlePositionY


 - 11 Privacy


◦Changed the value range for MaskIndex and MaskName


Transfer

 - FTP


◦Changed maximum value length of Host


 - SMTP


◦Changed maximum value length of Host


Event

 - Added following submenus


◦videoloss (Chapter 2.5 Video Loss)


◦autotracking (Chapter 2.6 Auto Tracking)


 - Video Analytics Setup


◦Added ObjectSize, MinimumObjectSizeInPixels, and MaximumObjectSizeInPixels


◦Removed value from ROIIndex


◦Removed the value range for MinimumObjectSize and MaximumObjectSize


◦Changed the parameter name from DefinedArea.#.Coordinates to DefinedArea.#.Coordinate and

from Line.#.Coordinates to Line.#.Coordinate.


◦Changed the value type of EntireAreaMode from enum to csv


 - Face Detection Setup


◦Changed the parameter name from DetectionArea.#.Coordinates to DetectionArea.#.Coordinate


◦Removed the value from DetectionAreaIndex


◦Removed the value range for Sensitivity


 - Audio Detection


◦Removed the value range for InputThresholdLevel


 - Event Rules


◦Added EveryDay, EveryDay<h>, and EveryDay<h>.FromTo


62 Introduction


◦Removed the value range for PresetNumber


 - Event Status


◦Removed the values for AlarmInput and AlarmOutput


◦Removed ChangedConfigURI from the check action


◦Added SystemEvent to the monitor and monitordiff actions


◦Added value ‘Tracking’ to Channel.#.EventType


I/O

 - Alarm Output


◦Removed value from AlarmOutput.#.ManualDuration and AlarmOutput.#.ManualDuration


PTZ

 - Added following submenus of ptzcontrol.cgi


◦absolute (Chapter 2.1 Absolute Position Control)


◦relative (Chapter 2.2 Relative Position Control)


◦query (Chapter 2.4 Requesting Current PTZ Info)


◦swing (Chapter 2.6 Swing Control)


◦group (Chapter 2.7 Group Control)


◦tour (Chapter 2.8 Tour Control)


◦trace (Chapter 2.9 Trace Control)


◦home (Chapter 2.10 Moving to Home Position)


◦areazoom (Chapter 2.11 Zoom Area)


 - Added following submenus of ptzconfig.cgi


◦swing (Chapter 3.1 Swing Setup)


◦group (Chapter 3.2 Group Setup)


◦tour (Chapter 3.3 Tour Setup)


◦trace (Chapter 3.4 Trace Setup)


◦autorun (Chapter 3.5 Auto Run Setup)


◦home (Chapter 3.6 Home Position Setup)


◦presetimageconfig (Chapter 3.8 Preset Image configuration)


◦presetvideoanalysis (Chapter 3.9 Preset Video Analysis Setup)


◦ptzsettings (Chapter 3.10 PTZ Settings)


◦ptlimits (Chapter 3.11 PT Operation Limits)


 - 2.3 Continuous PTZ Operation Control


◦Added the NormalizedSpeed parameter


◦Removed value ranges for Pan, Tilt, Zoom, and Duration


SUNAPI 63


 - 2.12 Stop Control


◦Added values ‘Focus’ and ‘Iris’ to OperationType


 - 2.13 Movement Control


◦Removed value ranges for MoveSpeed


Recording

 - General


◦Removed values for PreEventDuration and PostEventDuration

### **2.23. Version 2.0.0**

**Date** : 2013-03-29


**NOTE** Internal release


-First edition


64 Introduction


