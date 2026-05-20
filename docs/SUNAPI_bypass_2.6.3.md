# Bypass


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

1. Overview . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . 3

1.1. Description . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . 3

2. bypass . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . 4

2.1. Description . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . 4

2.2. Syntax . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . 4

2.3. Parameters . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . 4

2.4. Examples . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . 4

2.4.1. Getting Camera Attributes . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . 4

2.4.2. Getting camera events in text format . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . 5

2.4.3. Getting camera events in JSON format . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . 6

2.4.4. Configuration backup . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . 7

2.4.5. Configuration restore . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . 7

2.4.6. Firmware update . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . 7


2 Bypass


## **Chapter 1. Overview**
### **1.1. Description**

**bypass.cgi** is used to send SUNAPI commands to the connected cameras (Registered using SUNAPI

protocol only) via NVR, and to get the response for the corresponding command.


**NOTE** This chapter applies to NVR only.


SUNAPI 3


## **Chapter 2. bypass**
### **2.1. Description**

The **bypass** submenu in NVR bypasses the commands sent by SUNAPI client applications directly to the

camera, and gets the response from the camera.


This submenu supports all SUNAPI commands except for multi-part response commands

such as intermediate events for firmware update, monitor and monitordiff actions in

eventstatus.cgi.



**NOTE**


**Access level**



For the Firmware update command, only the final response will be sent to the requested

client.

For other commands, the response sent by the camera will be given as the response for a

bypass command.



|Action|Camera|
|---|---|
|control|User|

### **2.2. Syntax**

```
 http://<Device IP>/stw cgi/bypass.cgi?msubmenu=bypass&action==<value>[&<parameter>=<value>]

### **2.3. Parameters**

```








|Action|Parameters|Request/<br>Response|Type/<br>Value|Description|
|---|---|---|---|---|
|control|Channel|REQ|<int>|Channel number|
||HeadersToSend|REQ|<csv>|Extra headers to be sent to camera<br>such as cookies, response format etc.|
||BypassURI|REQ|<string>|SUNAPI command to be sent to<br>camera|

### **2.4. Examples**

#### **2.4.1. Getting Camera Attributes**

REQUEST

```
 http://<Device IP>/stw cgi/bypass.cgi?msubmenu=bypass&action=control&Channel=0&BypassURI=/stw
```

4 Bypass


```
 cgi/attributes.cgi/eventsources/videoanalysis/view/DetectionType

```

TEXT RESPONSE

```
 <parameter response="false" request="true" name="DetectionType">
 <dataType>
 <enum>
 <entry value="Off"/>
 <entry value="MotionDetection"/>
 <entry value="IntelligentVideo"/>
 <entry value="MDAndIV"/>
 </enum>
 </dataType>
 </parameter>

#### **2.4.2. Getting camera events in text format**
```

REQUEST

```
 http://<Device IP>/stw cgi/bypass.cgi?msubmenu=bypass&action=control&Channel=0&BypassURI=/stw cgi/eventstatus.cgi?msubmenu=eventstatus&action=check

```

TEXT RESPONSE

```
 HTTP/1.0 200 OK
 Content-type: text/plain
 <Body>

 Channel.0.MotionDetection=True
 Channel.0.MotionDetection.RegionID.1=True
 Channel.0.MotionDetection.RegionID.2=False
 Channel.0.MotionDetection.RegionID.3=False
 Channel.0.MotionDetection.RegionID.4=False
 Channel.0.Tampering=False
 Channel.0.DefocusDetection=False
 Channel.0.AudioDetection=False
 Channel.0.VideoAnalytics.Passing=False
 Channel.0.VideoAnalytics.Entering=False
 Channel.0.VideoAnalytics.Exiting=False
 Channel.0.VideoAnalytics.Appearing=False

```

SUNAPI 5


```
 Channel.0.VideoAnalytics.Disappering=False
 AlarmInput.1=False
 AlarmOutput.1=False

#### **2.4.3. Getting camera events in JSON format**
```

REQUEST

```
 http://<Device IP>/stw cgi/bypass.cgi?msubmenu=bypass&action=control&Channel=0&
 HeadersToSend=Accept:application/json&BypassURI=/stw cgi/eventstatus.cgi?msubmenu=eventstatus&action=check

```

JSON RESPONSE

```
 HTTP/1.0 200 OK
 Content-type: application/json
 <Body>

 {
 "ChannelEvent": [
 {
 "Channel": 0,
 "MotionDetection": true,
 "MotionDetectionRegions": {
 "1": true,
 "2": false,
 "3": false,
 "4": false
 },
 "Tampering": false,
 "DefocusDetection": false,
 "AudioDetection": false,
 "VideoAnalytics": {
 "Passing": false,
 "Entering": false,
 "Exiting": false,
 "Appearing": false,
 "Disappering": false
 }
 }

```

6 Bypass


```
],
"AlarmInput": {
"1": false
},
"AlarmOutput": {
"1": false
}
}

```

HeadersToSend is not mandatory; this parameter is used to send any special headers to



**NOTE**



the camera. "Accept:application/json" header can also be sent to NVR to get the response

from the camera in JSON format.


#### **2.4.4. Configuration backup**

REQUEST

```
 curl --digest -u <userid>:<password> "http://<Device IP>/stw cgi/bypass.cgi?msubmenu=bypass&action=control&Channel=0&BypassURI=/stw cgi/system.cgi?msubmenu=configbackup&action=control" > config.bin

#### **2.4.5. Configuration restore**
```

Encode to base64

```
 openssl base64 -in config.bin -out encoded.bin

```

REQUEST

```
 curl --digest -u <userid>:<password> "http://<Device IP>/stw cgi/bypass.cgi?msubmenu=bypass&action=control&Channel=0&BypassURI=/stw cgi/system.cgi?msubmenu=configrestore&action=control&ExcludeSettings=Network
,Camera" -H "Expect:" --data-urlencode @encoded.bin

#### **2.4.6. Firmware update**
```

REQUEST

```
 curl --digest -u <userid>:<password> "http://<Device IP>/stw cgi/bypass.cgi?msubmenu=bypass&action=control&Channel=0&BypassURI=/stw cgi/system.cgi?msubmenu=firmwareupdate&action=control&Type=Normal" -H
 "Expect:" -F uploadFile=@srn-4000-pkg_v2.00_150114103354.img

```

SUNAPI 7


