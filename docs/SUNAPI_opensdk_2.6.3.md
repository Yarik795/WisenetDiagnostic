# Open SDK


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

2. Applications . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . 5

2.1. Description . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . 5

2.2. Syntax . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . 5

2.3. Parameters . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . 5

2.4. Examples . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . 9

2.4.1. Getting the currently installed apps . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . 9

2.4.2. Installing a new application with CURL. . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . 10

2.4.3. Updating the existing application with CURL . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . 15

2.4.4. Installing license. . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . 17

2.4.5. Removing the installed application . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . 17

2.4.6. Starting the application . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . 17

2.4.7. Setting the application priority and enabling AutoStart . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . 18

2.4.8. Updating (Uploading) a datafile to openapp . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . 18

3. Application Status . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . 19

3.1. Description . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . 19

3.2. Syntax . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . 19

3.3. Parameters . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . 19

3.4. Examples . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . 21

3.4.1. Checking the application status once . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . 21

3.4.2. Monitoring the application status of Channel 0 every 5 seconds. . . . . . . . . . . . . . . . . . . . . . . . . . . 22

4. Application Manifest . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . 25

4.1. Description . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . 25

4.2. Syntax . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . 25

4.3. Parameters . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . 25

4.4. Examples . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . 25

4.4.1. Getting the application manifest file. . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . 25

5. Application Debug. . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . 28

5.1. Description . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . 28

5.2. Syntax . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . 28

5.3. Parameters . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . 28

5.4. Examples . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . 29

5.4.1. Setting the application to debug . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . 29

6. Application Event Information . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . 30

6.1. Description . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . 30


2 Open SDK


6.2. Syntax . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . 30

6.3. Parameters . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . 30

6.4. Examples . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . 31

6.4.1. Getting the event result format from installed opensdk applications. . . . . . . . . . . . . . . . . . . . . . . 31

7. Metaframe Schema. . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . 33

7.1. Description . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . 33

7.2. Syntax . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . 33

7.3. Parameters . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . 33

7.4. Examples . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . 33

7.4.1. Getting the schema of frame metadata supported by an app. . . . . . . . . . . . . . . . . . . . . . . . . . . . . 33

8. Metaframe Capability . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . 36

8.1. Description . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . 36

8.2. Syntax . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . 36

8.3. Parameters . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . 36

8.4. Examples . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . 36

8.4.1. Getting the metaframe capability of the installed apps. . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . 36


SUNAPI 3


## **Chapter 1. Overview**
### **1.1. Description**

**opensdk.cgi** is used to install and manage the application.


The following submenus are used for open SDK functionalities:


 - **apps** : Requests and configures the application general settings. The **apps** submenu is also used to

install and remove the application.


 - **appstatus** : Requests the application status such as memories and CPU used for one time or

periodically.


 - **manifest** : Requests the application manifest file.


 - **debug** : Requests to debug an opensdk application using ‘RemoteDebugViewer’.


 - **opensdkeventinfo** : Reads the event schema from the camera’s third party application.


 - **metaframeschema** : Used to notify the metaframe schema supported by an app.


 - **metaframecapability** : Submenu to notify all supported values/ranges of metadata parameters.


This document applies to the network cameras only.

Attribute to check for feature support: "attributes/System/Support/OpenSDK"



**NOTE**



For multi-directional cameras, please refer to the value

"attributes/System/Support/OneOpenAppPerChannel". When this value is set to true, the

application can be installed on any one channel.



4 Open SDK


## **Chapter 2. Applications**
### **2.1. Description**

The **apps** submenu requests, configures and controls the application settings. It is also used to install and

remove the application.


Attribute to check maximum applications: "
**NOTE**

**attributes/system/Limit/OpenSDK.MaxApps** "


**Access level**

|Action|Camera|
|---|---|
|view|Admin|
|set|Admin|
|control|Admin|
|install|Admin|
|remove|Admin|


### **2.2. Syntax**

```
 http://<Device IP>/stw cgi/opensdk.cgi?msubmenu=apps&action=<value>[&<parameter>=<value>...]

### **2.3. Parameters**

```













|Action|Parameters|Request/<br>Response|Type/<br>Value|Description|
|---|---|---|---|---|
|view||||Reads the application setting<br>information|
||InstalledApps|RES|<int>|The number of currently installed<br>applications|
||<AppID>.Status|RES|<enum><br>UnInstallin<br>g,Installed,I<br>nstalling,St<br>artedNotRu<br>nning,Runn<br>ing,Stopped|Status of the application|



SUNAPI 5


|Action|Parameters|Request/<br>Response|Type/<br>Value|Description|
|---|---|---|---|---|
||<AppID>.InstalledDate|RES|<string>|Installation date of the application<br>The date is specified in the format of<br><YYYY-MM-DDThh:mm:ssZ> (UTC<br>time).|
||<AppID>.Version|RES|<string>|Application version|
||<AppID>.Permission|RES|<csv><br>Device, PTZ,<br>Network,<br>SDCard,<br>None|Application permission is a Read Only<br>parameter. This information is<br>retrieved from the manifest xml of the<br>application.|
||<AppID>.AutoStart|RES|<bool><br>True, False|Enables or disables the application to<br>automatically start|
||<AppID>.Priority|RES|<enum><br>Low,<br>Medium,<br>High|Priority|
||<AppID>.Channel|RES|<csv>|The channel index where the<br>application is installed<br>**Note**<br>To use the Channel parameter,<br>check<br>attributes/system/support/OneOp<br>enAppPerChannel|
||<AppID>.IsDefault|RES|<bool><br>True, False|Shows whether this app is the Default<br>app<br>**Note**<br>Default apps will not be<br>uninstalled when a factory reset is<br>performed, and the app’s Priority<br>setting will automatically be set to<br>High and frozen|



6 Open SDK


|Action|Parameters|Request/<br>Response|Type/<br>Value|Description|
|---|---|---|---|---|
||ControlForbidden|RES|<csv><br>StartStop,Pr<br>iority,AutoS<br>tart|• StartStop: This means app will not<br>be controled by "control" action<br>"Mode" parameter Start/Stop.<br>Always auto start.<br>• Priority: This means Priority<br>setting is forbidden.<br>• AutoStart: This means AutoStart<br>setting is forbidden.|
|set|AppID|REQ|<string>|Application ID<br>**Note**<br>**AppID** must be sent together with<br>the**set** action.|
||AutoStart|REQ|<bool><br>True, False|Enables or disables the application to<br>automatically start|
||Priority|REQ|<enum><br>Low,<br>Medium,<br>High|Priority|
||Channel|REQ|<int>|Channel ID where the application is<br>installed<br>**Note**<br>To use the Channel parameter,<br>check<br>attributes/system/support/OneOp<br>enAppPerChannel|
||IsDefault|RES|<bool><br>True, False|Whether this app is the default app<br>**Note**<br>Default apps will not be<br>uninstalled when a factory reset is<br>performed, and the app’s Priority<br>setting will automatically be set to<br>High and frozen|
|control|AppID|REQ|<string>|Application ID<br>**Note**<br>**AppID** must be sent together with<br>the**control** action.|


SUNAPI 7


|Action|Parameters|Request/<br>Response|Type/<br>Value|Description|
|---|---|---|---|---|
||Mode|REQ|<enum><br>Start, Stop|Mode|
||Channel|REQ|<int>|Channel ID where the application is<br>installed<br>**Note**<br>To use the Channel parameter,<br>check<br>attributes/system/support/OneOp<br>enAppPerChannel|
|install|AppID|REQ|<string>|Application ID<br>**Note**<br>**AppID** must be sent together with<br>the**install** action.|
||Permission|RES|<csv>|Permission|
||InstallType|RES|<enum><br>New,<br>Upgrade|Installation type|
||IgnoreCookie|REQ|<bool><br>True, False|Ignore Application Session ID as a<br>cookie|
||ApplicationSessionId|REQ, RES|<string>|Application Session ID if cookie is not<br>used|
||KeepOldSettings|REQ|<bool><br>True, False|Keeps the old settings<br>**Note**<br>**AppID** and**KeepOldSettings** must<br>be sent together for the**install**<br>action if**InstallType**parameter is<br>NOT set to New.|
||Channel|REQ|<int>|Channel ID where the application will<br>be installed<br>**Note**<br>To use the Channel parameter,<br>check<br>attributes/system/support/OneOp<br>enAppPerChannel|


8 Open SDK


|Action|Parameters|Request/<br>Response|Type/<br>Value|Description|
|---|---|---|---|---|
|remove|AppID|REQ|<string>|Application ID<br>**Note**<br>**AppID** must be sent together with<br>the**remove** action.|
||Channel|REQ|<int>|Channel ID where the application is<br>installed<br>**Note**<br>To use the Channel parameter,<br>check<br>attributes/system/support/OneOp<br>enAppPerChannel|
|update|AppID|REQ|<string>|It can upload any files to openapp.<br>Ex.) AI binary data, application config<br>json file, jpg, …|

### **2.4. Examples**

#### **2.4.1. Getting the currently installed apps**

REQUEST

```
 http://<Device IP>/stw-cgi/opensdk.cgi?msubmenu=apps&action=view

```

TEXT RESPONSE

```
 HTTP/1.0 200 OK
 Content-type: text/plain
 <Body>

 InstalledApps=1
 ANPR.InstalledDate=2014-01-29T15:00:00Z
 ANPR.Verion=1.0
 ANPR.Permission=SD,Network
 ANPR.Status=Stopped
 ANPR.AutoStart=False
 ANPR.Priority=High
 ANPR.Channel=0

```

SUNAPI 9


JSON RESPONSE

```
 HTTP/1.0 200 OK
 Content-type: application/json
 <Body>

 {
 "InstalledApps": 1,
 "Apps": [
 {
 "AppID": "ANPR",
 "Status": "Stopped",
 "InstalledDate": "2014-01-29T15:00:00Z",
 "Version": "1.0",
 "Permission": [
 "Sd",
 "Network"
 ],
 "AutoStart": false,
 "Priority": "High",
 "Channel": "0"
 }
 ]
 }

#### **2.4.2. Installing a new application with CURL**
```

The OpenSDK application installation is a two-step process. First, the application file needs to be sent to

the camera via HTTP POST. The camera sends a session id cookie, installation type and the permissions

required by the application. Then, based on the installation type and required permissions, a user can

decide whether to install the application or not by sending the install command via HTTP GET.


AppID should be same as the application cap file name (without extension).


**NOTE** To get JSON response add the -H "Accept: application/json" header to the request.


**Without using cookies:**


**Step 1: CURL command for sending the application to the camera**


REQUEST

```
 curl -v --digest -u <userid>:<password> -F UploadedFile=@ServerPushMJPEG.cap

```

10 Open SDK


```
 "http://<Device IP>/stw cgi/opensdk.cgi?msubmenu=apps&action=install&AppID=ServerPushMJPEG&Channel=0
 &IgnoreCookie=True" -H "Expect:"

```

The above command will produce a request to the device as below:

```
 POST /stw cgi/opensdk.cgi?msubmenu=apps&action=install&AppID=ServerPushMJPEG&Channel=0
 HTTP/1.1
 User-Agent: curl/7.26.0
 Host: 111.111.11.11
 Accept: */*
 Content-Length: 119523
 Content-Type: multipart/form-data; boundary=--------------------------- fb674236d482

```

TEXT RESPONSE

```
 HTTP/1.1 200 OK
 Content-Type: text/plain
 Content-Length: 32
 Date: Thu, 20 Mar 2014 01:32:12 GMT
 Server: lighttpd/1.4.31
 <Body>

 ApplicationSessionId=ServerPushMJPEG-111.111.11.111
 Permission=SD,Network
 InstallType=New

```

JSON RESPONSE

```
 HTTP/1.1 200 OK
 Content-Type: application/json
 Content-Length: 32
 Date: Thu, 20 Mar 2014 01:32:12 GMT
 Server: lighttpd/1.4.31
 <Body>

 {

```

SUNAPI 11


```
 "ApplicationSessionId": " ServerPushMJPEG-111.111.11.111",
 "Permission": ["SD","Network"],
 "InstallType": "New",
 }

```

**Step 2:CURL command for installing the application**


REQUEST

```
 curl -v --digest -u <userid>:<password> "http://<Device IP>/stw cgi/opensdk.cgi?msubmenu=apps&action=install&AppID=ServerPushMJPEG&Channel=0
 & ApplicationSessionId=ServerPushMJPEG-111.111.11.111

```

The above command will produce a request to the device as below:

```
 GET /stw cgi/opensdk.cgi?msubmenu=apps&action=install&AppID=ServerPushMJPEG&Channel=0
 HTTP/1.1
 User-Agent: curl/7.26.0
 Host: 111.111.11.11
 Accept: */*
 TEXT RESPONSE
 HTTP/1.1 200 OK
 Content-Type: text/plain
 Content-Length: 2
 Date: Thu, 20 Mar 2014 01:46:04 GMT
 Server: lighttpd/1.4.31
 <Body>

 OK

```

JSON RESPONSE

```
 HTTP/1.1 200 OK
 Set-Cookie: AppInstallSessionID=deleted; expires=Wed, 20-Mar-2013 01:46:03
 GMT
 Content-Type: application/json
 Content-Length: 2
 Date: Thu, 20 Mar 2014 01:46:04 GMT
 Server: lighttpd/1.4.31

```

12 Open SDK


```
 <Body>

 {
 "Response": "Success"
 }

```

**Using Cookies:**


**Step 1: CURL command for sending the application to the camera**


REQUEST

```
 curl -v --digest -u <userid>:<password> -F UploadedFile=@ServerPushMJPEG.cap
 "http://<Device IP>/stw cgi/opensdk.cgi?msubmenu=apps&action=install&AppID=ServerPushMJPEG&Channel=0
 " -H "Expect:"

```

The above command will produce a request to the device as follows:

```
 POST /stw cgi/opensdk.cgi?msubmenu=apps&action=install&AppID=ServerPushMJPEG&Channel=0
 HTTP/1.1
 User-Agent: curl/7.26.0
 Host: 111.111.11.11
 Accept: */*
 Content-Length: 119523
 Content-Type: multipart/form-data; boundary=--------------------------- fb674236d482

```

TEXT RESPONSE

```
 HTTP/1.1 200 OK
 Set-Cookie: AppInstallSessionID=ServerPushMJPEG-111.111.11.111
 Content-Type: text/plain
 Content-Length: 32
 Date: Thu, 20 Mar 2014 01:32:12 GMT
 Server: lighttpd/1.4.31
 <Body>

 Permission=SD,Network

```

SUNAPI 13


```
 InstallType=New

```

JSON RESPONSE

```
 HTTP/1.1 200 OK
 Set-Cookie: AppInstallSessionID=ServerPushMJPEG-111.111.11.111
 Content-Type: application/json
 Content-Length: 32
 Date: Thu, 20 Mar 2014 01:32:12 GMT
 Server: lighttpd/1.4.31
 <Body>

 {
 "Response": "Success"
 }

```

**Step 2:CURL command for installing the application**


REQUEST

```
 curl -v --digest -u <userid>:<password> --cookie
 AppInstallSessionID=ServerPushMJPEG-<Device IP> "http://<Device IP>/stw cgi/opensdk.cgi?msubmenu=apps&action=install&AppID=ServerPushMJPEG&Channel=0
 "

```

The above command will produce a request to the device as below:

```
 GET /stw cgi/opensdk.cgi?msubmenu=apps&action=install&AppID=ServerPushMJPEG&Channel=0
 HTTP/1.1
 User-Agent: curl/7.26.0
 Host: 111.111.11.11
 Accept: */*
 Cookie: AppInstallSessionID=ServerPushMJPEG-111.111.11.111

```

TEXT RESPONSE

```
 HTTP/1.1 200 OK
 Set-Cookie: AppInstallSessionID=deleted; expires=Wed, 20-Mar-2013 01:46:03
 GMT

```

14 Open SDK


```
 Content-Type: text/plain
 Content-Length: 2
 Date: Thu, 20 Mar 2014 01:46:04 GMT
 Server: lighttpd/1.4.31
 <Body>

 OK

```

JSON RESPONSE

```
 HTTP/1.1 200 OK
 Set-Cookie: AppInstallSessionID=deleted; expires=Wed, 20-Mar-2013 01:46:03
 GMT
 Content-Type: application/json
 Content-Length: 2
 Date: Thu, 20 Mar 2014 01:46:04 GMT
 Server: lighttpd/1.4.31
 <Body>

 {
 "Response": "Success"
 }

#### **2.4.3. Updating the existing application with CURL**
```

**Step 1: CURL command for sending the application to the camera**


REQUEST

```
 curl -v --digest -u <userid>:<password> -F UploadedFile=@ServerPushMJPEG.cap
 "http://<Device IP>/stw cgi/opensdk.cgi?msubmenu=apps&action=install&AppID=ServerPushMJPEG&Channel=0
 " -H "Expect:"

```

TEXT RESPONSE

```
 HTTP/1.1 200 OK
 Set-Cookie: AppInstallSessionID=ServerPushMJPEG-111.111.11.111
 Content-Type: text/plain
 Content-Length: 32
 Date: Thu, 20 Mar 2014 01:32:12 GMT

```

SUNAPI 15


```
 Server: lighttpd/1.4.31
 <Body>

 Permission=SD,Network
 InstallType=Upgrade

```

JSON RESPONSE

```
 HTTP/1.1 200 OK
 Set-Cookie: AppInstallSessionID=deleted; expires=Wed, 20-Mar-2013 01:46:03
 GMT
 Content-Type: application/json
 Content-Length: 2
 Date: Thu, 20 Mar 2014 01:46:04 GMT
 Server: lighttpd
 <Body>

 {
 "Response": "Success"
 }

```

**Step 2: CURL command for updating the application**


REQUEST

```
 curl -v --digest -u <userid>:<password> --cookie AppInstallSessionID=<value>
 "http://<Device IP>/stw cgi/opensdk.cgi?msubmenu=apps&action=install&AppID=ServerPushMJPEG&Channel=0
 &KeepOldSettings=True"

```

TEXT RESPONSE

```
 HTTP/1.1 200 OK
 Set-Cookie: AppInstallSessionID=deleted; expires=Wed, 20-Mar-2013 01:46:03
 GMT
 Content-Type: text/plain
 Content-Length: 2
 Date: Thu, 20 Mar 2014 01:46:04 GMT
 Server: lighttpd

```

16 Open SDK


```
 <Body>

 OK

```

JSON RESPONSE

```
 HTTP/1.1 200 OK
 Set-Cookie: AppInstallSessionID=deleted; expires=Wed, 20-Mar-2013 01:46:03
 GMT
 Content-Type: application/json
 Content-Length: 2
 Date: Thu, 20 Mar 2014 01:46:04 GMT
 Server: lighttpd

 <Body>

 {
 "Response": "Success"
 }

#### **2.4.4. Installing license**
```

REQUEST

```
 curl -v --digest -u admin:<password> -F LicenseFile=@filename
 "http://<Device IP>/stw cgi/opensdk.cgi?msubmenu=apps&action=install&AppID=ServerTest&Channel=0" -H
 "Expect:"

#### **2.4.5. Removing the installed application**
```

REQUEST

```
 http://<Device IP>/stw cgi/opensdk.cgi?msubmenu=apps&action=remove&AppID=ServerPushMJPEG&Channel=0

#### **2.4.6. Starting the application**
```

REQUEST

```
 http://<Device IP>/stw
```

SUNAPI 17


```
 cgi/opensdk.cgi?msubmenu=apps&action=control&AppID=ServerPushMJPEG&Mode=Star
 t&Channel=0

#### **2.4.7. Setting the application priority and enabling AutoStart**
```

REQUEST

```
 http://<Device IP>/stw cgi/opensdk.cgi?msubmenu=apps&action=set&AppID=ServerPushMJPEG&Priority=Medi
 um&AutoStart=True&Channel=0

#### **2.4.8. Updating (Uploading) a datafile to openapp**
```

REQUEST

Binary data

```
 curl -v --digest -u admin:<password> -F DataFile=@{datafilename}
 "http://<IP>/stw-cgi/opensdk.cgi?msubmenu=apps&action=update&AppID=SNTest"
 -H "Expect:"

```

In case of not binary data, we need to put "octet-stream type" in data.


REQUEST

```
 curl -v --digest -u admin:<password> -F
 DataFile=@test.txt;type=application/octet-stream
 "http://<IP>/stw cgi/opensdk.cgi?msubmenu=apps&action=update&AppID=test_Upload_File" -H
 "Expect:"

```

18 Open SDK


## **Chapter 3. Application Status**
### **3.1. Description**

The **appstatus** submenu requests the status of the application.


**Access level**

|Action|Camera|
|---|---|
|view|Admin|


### **3.2. Syntax**

```
 http://<Device IP>/stw cgi/opensdk.cgi?msubmenu=appstatus&action=<value>[&<parameter>=<value>...]

### **3.3. Parameters**

```



















|Action|Parameters|Request/<br>Response|Type/<br>Value|Description|
|---|---|---|---|---|
|view||||Reads the application status|
||AppID|REQ|<csv><br><AppID>|Application ID<br>If the specific App ID is not sent, the<br>status of all applications is returned.|
||Channel|REQ|<int>|Channel ID<br>Used when the application status for a<br>specific channel is needed. If**Channel**<br>is not sent, all channels’ application<br>status is returned.<br>**Note**<br>To use the Channel parameter,<br>check<br>attributes/system/support/OneOp<br>enAppPerChannel|
||Check|REQ|<enum><br>Once,<br>Periodically|Whether to checks the application<br>status only once or periodically.<br>If**Check** is not sent, the status of the<br>application is returned to Once.|



SUNAPI 19


|Action|Parameters|Request/<br>Response|Type/<br>Value|Description|
|---|---|---|---|---|
||Periodicity|REQ|<int>|Interval for checking the application<br>status<br>If**Periodicity** is not sent, the default<br>periodicity is applicable.<br>The values must be within the range<br>of 1 to 9 and the unit is a second.|
||TotalCPUUsage|RES|<int>|Total CPU used<br>The values must be within the range<br>of 1 to 100.|
||TotalMemoryUsage|RES|<int>|Memory totally used<br>The values must be in the range of 1<br>to 100.|
||<AppID>.CPUUsage|RES|<int>|CPU used in the corresponding<br>application<br>The values must be within the range<br>of 1 to 100.|
||<AppID>.MemoryUsage|RES|<int>|Memory used in the corresponding<br>application<br>The values must be within the range<br>of 1 to 100.|
||<AppID>.ThreadsCount|RES|<int>|Thread count of the corresponding<br>application|
||<AppID>.Duration|RES|<string>|Duration of the corresponding<br>application<br>Durations are represented by the<br>format<br><P[n]Y[n]M[n]DT[n]H[n]M[n]S>,<br>following the ISO 8601 duration<br>format.|


20 Open SDK


|Action|Parameters|Request/<br>Response|Type/<br>Value|Description|
|---|---|---|---|---|
||<AppID>.Channel|RES|<csv>|Channel ID where the application is<br>installed<br>**Note**<br>To use the Channel parameter,<br>check<br>attributes/system/support/OneOp<br>enAppPerChannel|

### **3.4. Examples**

#### **3.4.1. Checking the application status once**

REQUEST

```
 http://<Device IP>/stw cgi/opensdk.cgi?msubmenu=appstatus&action=view&AppID=ANPR

```

TEXT RESPONSE

```
 HTTP/1.0 200 OK
 Content-type: text/plain
 <Body>

 TotalCPUUsage=40
 TotalMemoryUsage=30
 ANPR.CPUUsage=30
 ANPR.MemoryUsage=10
 ANPR.ThreadsCount=11
 ANPR.Duration=P0Y0M0DT1H0M0S
 ANPR.Channel=0

```

JSON RESPONSE

```
 HTTP/1.0 200 OK
 Content-type: application/json
 <Body>

 {

```

SUNAPI 21


```
 "TotalCPUUsage": 40,
 "TotalMemoryUsage": 30,
 "Apps": [
 {
 "AppID": "ANPR",
 "CPUUsage": 30,
 "MemoryUsage": 10,
 "ThreadsCount": 11,
 "Duration": "P0Y0M0DT1H0M0S",
 "Channel": "0"
 }
 ]
 }

#### **3.4.2. Monitoring the application status of Channel 0 every 5 seconds**
```

REQUEST

```
 http://<Device IP>/stw cgi/opensdk.cgi?msubmenu=appstatus&action=view&Check=Periodically&Periodicit
 y=5&Channel=0

```

TEXT RESPONSE

```
 <Body>

 --SamsungTechwin
 Content-Type: text/plain
 TotalCPUUsage=40
 TotalMemoryUsage=30
 ANPR.CPUUsage=30
 ANPR.MemoryUsage=10
 ANPR.ThreadsCount=11
 ANPR.Duration=P0Y0M0DT1H0M0S
 ServerPushMJPEG.CPUUsage=10
 ServerPushMJPEG.MemoryUsage=5
 ServerPushMJPEG.ThreadsCount=9
 ServerPushMJPEG.Duration=P0Y0M0DT2H10M0S

 --SamsungTechwin
 Content-Type: text/plain

```

22 Open SDK


```
 TotalCPUUsage=40
 TotalMemoryUsage=30
 ANPR.CPUUsage=20
 ANPR.MemoryUsage=10
 ANPR.ThreadsCount=11
 ANPR.Duration=P0Y0M0DT1H10M0S
 ServerPushMJPEG.CPUUsage=20
 ServerPushMJPEG.MemoryUsage=5
 ServerPushMJPEG.ThreadsCount=9
 ServerPushMJPEG.Duration=P0Y0M0DT2H15M0S

```

JSON RESPONSE

```
 <Body>

 --SamsungTechwin
 Content-Type: application/json

 {
 "TotalCPUUsage": 40,
 "TotalMemoryUsage": 30,
 "Apps": [
 {
 "AppID": "ANPR",
 "CPUUsage": 30,
 "MemoryUsage": 10,
 "ThreadsCount": 11,
 "Duration": "P0Y0M0DT1H0M0S"
 },
 {
 "AppID": "ServerPushMJPEG",
 "CPUUsage": 10,
 "MemoryUsage": 5,
 "ThreadsCount": 9,
 "Duration": "P0Y0M0DT2H10M0S"
 }
 ]
 }

 --SamsungTechwin

```

SUNAPI 23


```
 Content-Type: application/json

 {
 "TotalCPUUsage": 40,
 "TotalMemoryUsage": 30,
 "Apps": [
 {
 "AppID": "ANPR",
 "CPUUsage": 20,
 "MemoryUsage": 10,
 "ThreadsCount": 11,
 "Duration": "P0Y0M0DT1H10M0S"
 },
 {
 "AppID": " ServerPushMJPEG",
 "CPUUsage": 20,
 "MemoryUsage": 5,
 "ThreadsCount": 9,
 "Duration": "P0Y0M0DT2H15M0S"
 }
 ]
 }

```

24 Open SDK


## **Chapter 4. Application Manifest**
### **4.1. Description**

The **manifest** submenu requests the application manifest xml file which contains detailed information of

the application such as the application name, location, version, etc.


**Access level**

|Action|Camera|
|---|---|
|view|Admin|


### **4.2. Syntax**

```
 http://<Device IP>/stw cgi/opensdk.cgi?msubmenu=manifest&action=<value>[&<parameter>=<value>...]

### **4.3. Parameters**

```








|Action|Parameters|Request/<br>Response|Type/<br>Value|Description|
|---|---|---|---|---|
|view||||Reads the application manifest in the<br>xml file format.|
||AppID|REQ|<string>|Application ID<br>**Note**<br>**AppID** must be sent together with<br>the**view** action.|
||Channel|REQ|<int>|Channel ID where the application is<br>installed<br>**Note**<br>To use the Channel parameter,<br>check<br>attributes/system/support/OneOp<br>enAppPerChannel|

### **4.4. Examples**

#### **4.4.1. Getting the application manifest file**

SUNAPI 25


REQUEST

```
 http://<Device IP>/stw cgi/opensdk.cgi?msubmenu=manifest&action=view&AppID=ServerPushMJPEG&Channel=
 0

```

RESPONSE

```
 <Body>

 <?xml version="1.0" encoding="UTF-8" standalone="no"?>
 <manifest>
 <appName>ServerPushMJPEG</appName>
 <appLocation>/home/user/workspace/ServerPushMJPEG</appLocation>
 <appVersion>1.0</appVersion>
 <minSDK>2.0</minSDK>
 <targetSDK>2.0</targetSDK>
 <maxSDK>2.0</maxSDK>
 <debug>false</debug>
 <vendor>Hanwha</vendor>
 <description/>
 <platform>
 <model>SNP6320</model>
 <videoEncoding>
 <codec>MJPEG</codec>
 <resolution>640 X 480</resolution>
 <frameRate>10</frameRate>
 <compression>2</compression>
 <bitRate>10240</bitRate>
 <audio>false</audio>
 </videoEncoding>
 <rawVideo>
 <format>YUV 400</format>
 <resolution>1920 X 1080</resolution>
 <frameRate>3</frameRate>
 </rawVideo>
 </platform>
 <permissions/>
 <appConfigData>
 <portNo>8080</portNo>
 </appConfigData>

```

26 Open SDK


```
 </manifest>

```

SUNAPI 27


## **Chapter 5. Application Debug**
### **5.1. Description**

The **debug** submenu requests to debug the application using the ‘RemoteDebugViewer’ program. Only

one application can be debugged at a time. All applications can be debugged.


**Access level**

|Action|Camera|
|---|---|
|set|Admin|


### **5.2. Syntax**

```
 http://<Device IP>/stw cgi/opensdk.cgi?msubmenu=debug&action=<value>[&<parameter>=<value>...]

### **5.3. Parameters**

```








|Action|Parameters|Request/<br>Response|Type/<br>Value|Description|
|---|---|---|---|---|
|set|AppID|REQ, RES|<string>|Application ID<br>**Note**<br>**AppID**, **Port**, and**Enable** must be<br>sent together.|
||Port|REQ, RES|<int>|Camera’s port number<br>**Note**<br>**AppID**, **Port**, and**Enable** must be<br>sent together.|
||Enable|REQ, RES|<bool>|Enabling debugging<br>**Note**<br>**AppID**, **Port**, and**Enable** must be<br>sent together.|


28 Open SDK


|Action|Parameters|Request/<br>Response|Type/<br>Value|Description|
|---|---|---|---|---|
||Channel|REQ|<int>|Channel ID where the application is<br>installed<br>**Note**<br>An optional parameter. If**Channel**<br>is not sent, the first channel’s<br>application will be debugged. To<br>use the Channel parameter, check<br>attributes/system/support/OneOp<br>enAppPerChannel|

### **5.4. Examples**

#### **5.4.1. Setting the application to debug**

REQUEST

```
 http://<Device IP>/stw cgi/opensdk.cgi?msubmenu=debug&action=set&AppID=abc&Port=8080&Enable=True&Ch
 annel=0

```

SUNAPI 29


## **Chapter 6. Application Event Information**
### **6.1. Description**

The **opensdkeventinfo** submenu provides the open SDK application’s event schema. Users can get event

results from the open SDK application using eventstatus.cgi. Please refer to the document regarding this

event.


**Access level**

|Action|Camera|
|---|---|
|view|Admin|


### **6.2. Syntax**

```
 http://<Device IP>/stw cgi/opensdk.cgi?msubmenu=opensdkeventinfo&action=<value>[&<parameter>=<value
 >...]

### **6.3. Parameters**

```














|Action|Parameters|Request/<br>Response|Type/<br>Value|Description|
|---|---|---|---|---|
|view|AppName|RES|<string>|Application name|
||AppEvent|RES|<string>|Application event name|
||EventTopic|RES|<string>|Event topic name|
||Type|RES|<enum><br>Event, Meta|It can be either an Event or Metadata<br>When type is event, schema follows<br>the onvif event schema format.<br>When type is Metadata, metadata xml<br>schema is provided. e.g. Like<br>licenplate information etc.,|
||EventSchema|REQ|<string>|Event schema<br>**Note**<br>This schema information is set<br>with an open application.|


30 Open SDK


### **6.4. Examples**

#### **6.4.1. Getting the event result format from installed opensdk applications**

REQUEST

```
 http://<Device IP>/stw-cgi/opensdk.cgi?msubmenu=opensdkeventinfo&action=view

```

JSON RESPONSE

```
 HTTP/1.0 200 OK
 Content-type: application/json
 <Body>

 {
 "OpenSDKEventInfo": [
 {
 "AppName": "LicensePlateDetection",
 "AppEvent": "LicensePlateNumber",
 "Type": "Event",
 "EventTopic":
 "tns1:OpenApp/LicensePlateDetection/LicensePlateNumber",
 "EventSchema":
 "<tns1:OpenApp><LicensePlateDetection><LicensePlateNumber
 wstop:topic=\"true\"><tt:MessageDescription><tt:Source><tt:SimpleItemDescrip
 tion Name=\"VideoSourceToken\"
 Type=\"tt:ReferenceToken\"/></tt:Source><tt:Data><tt:SimpleItemDescription
 Name=\"LicensePlateNumber\"
 Type=\"xsd:string\"/></tt:Data></tt:MessageDescription></LicensePlateNumber>
 </LicensePlateDetection></tns1:OpenApp>"
 },
 {
 "AppName": "VehicleDetection",
 "AppEvent": "VehicleDetected",
 "Type": "Event",
 "EventTopic": "tns1:OpenApp/VehicleDetection/VehicleDetected",
 "EventSchema": "<tns1:OpenApp><VehicleDetection><VehicleDetected
 wstop:topic=\"true\"><tt:MessageDescription><tt:Source><tt:SimpleItemDescrip
 tion Name=\"VideoSourceToken\"
 Type=\"tt:ReferenceToken\"/></tt:Source><tt:Data><tt:SimpleItemDescription
 Name=\"VehicleDetected\"
 Type=\"xsd:boolean\"/></tt:Data></tt:MessageDescription></VehicleDetected></

```

SUNAPI 31


```
 VehicleDetection></tns1:OpenApp>"
 }
 ]
 }

```

32 Open SDK


## **Chapter 7. Metaframe Schema**
### **7.1. Description**

The **metaframeschema** submenu, used to provide the schema of the frame metadata supported by an

installed app.


**Access level**

|Action|Camera|
|---|---|
|view|User|


### **7.2. Syntax**

```
 http://<Device IP>/stw cgi/opensdk.cgi?msubmenu=metaframeschema&action=<value>[&<parameter>=<value>
 ...]

### **7.3. Parameters**

```










|Action|Parameters|Request/<br>Response|Type/<br>Value|Description|
|---|---|---|---|---|
|view|Channel|REQ, RES|<int>|ChannelID, optional parameter in the<br>request. If passed, the result will be<br>filtered only for that channel.|
||AppID|REQ, RES|<string>|Application ID|
||Schema|RES|<string>|Frame metadata schema as base64<br>encoded string.|
||Encoding|RES|<enum><br>base64|Used to notify the encoding format of<br>schema.|

### **7.4. Examples**




#### **7.4.1. Getting the schema of frame metadata supported by an app.**

REQUEST

```
 http://<Device IP>/stw-cgi/opensdk.cgi?msubmenu=metaframeschema&action=view

```

JSON RESPONSE

```
 HTTP/1.0 200 OK

```

SUNAPI 33


```
 Content-type: application/json
 <Body>

 {
 "MetaFrameSchema": [
 {
 "Channel": 0,
 "AppFrameSchema": [
 {
 "AppID": "SampleAIAPP",
 "Schema":
 "PHhzOnNjaGVtYSBhdHRyaWJ1dGVGb3JtRGVmYXVsdD0idW5xdWFsaWZpZWQiIGVsZW1lbnRGb3J
 tRGVmYXVsdD0icXVhbGlmaWVkIiB0YXJnZXROYW1lc3BhY2U9Imh0dHA6Ly93d3cub252aWYub3J
 nL3ZlcjEwL3NjaGVtYSIgeG1sbnM6eHM9Imh0dHA6Ly93d3cudzMub3JnLzIwMDEvWE1MU2NoZW1
 hIj48eHM6ZWxlbWVudCBuYW1lPSJNZXRhZGF0YVN0cmVhbSI+PHhzOmNvbXBsZXhUeXBlPjx4czp
 zZXF1ZW5jZT48eHM6ZWxlbWVudCBuYW1lPSJWaWRlb0FuYWx5dGljcyI+PHhzOmNvbXBsZXhUeXB
 lPjx4czpzZXF1ZW5jZT48eHM6ZWxlbWVudCBuYW1lPSJGcmFtZSI+PHhzOmNvbXBsZXhUeXBlPjx
 4czpzZXF1ZW5jZT48eHM6ZWxlbWVudCBuYW1lPSJUcmFuc2Zvcm1hdGlvbiI+PHhzOmNvbXBsZXh
 UeXBlPjx4czpzZXF1ZW5jZT48eHM6ZWxlbWVudCBuYW1lPSJUcmFuc2xhdGUiPjx4czpjb21wbGV
 4VHlwZT48eHM6c2ltcGxlQ29udGVudD48eHM6ZXh0ZW5zaW9uIGJhc2U9InhzOnN0cmluZyI+PHh
 zOmF0dHJpYnV0ZSB0eXBlPSJ4czpmbG9hdCIgbmFtZT0ieCIvPjx4czphdHRyaWJ1dGUgdHlwZT0
 ieHM6ZmxvYXQiIG5hbWU9InkiLz48L3hzOmV4dGVuc2lvbj48L3hzOnNpbXBsZUNvbnRlbnQ+PC9
 4czpjb21wbGV4VHlwZT48L3hzOmVsZW1lbnQ+PHhzOmVsZW1lbnQgbmFtZT0iU2NhbGUiPjx4czp
 jb21wbGV4VHlwZT48eHM6c2ltcGxlQ29udGVudD48eHM6ZXh0ZW5zaW9uIGJhc2U9InhzOnN0cml
 uZyI+PHhzOmF0dHJpYnV0ZSB0eXBlPSJ4czpmbG9hdCIgbmFtZT0ieCIvPjx4czphdHRyaWJ1dGU
 gdHlwZT0ieHM6ZmxvYXQiIG5hbWU9InkiLz48L3hzOmV4dGVuc2lvbj48L3hzOnNpbXBsZUNvbnR
 lbnQ+PC94czpjb21wbGV4VHlwZT48L3hzOmVsZW1lbnQ+PC94czpzZXF1ZW5jZT48L3hzOmNvbXB
 sZXhUeXBlPjwveHM6ZWxlbWVudD48eHM6ZWxlbWVudCBuYW1lPSJPYmplY3QiPjx4czpjb21wbGV
 4VHlwZT48eHM6c2VxdWVuY2U+PHhzOmVsZW1lbnQgbmFtZT0iQXBwZWFyYW5jZSI+PHhzOmNvbXB
 sZXhUeXBlPjx4czpzZXF1ZW5jZT48eHM6ZWxlbWVudCBuYW1lPSJTaGFwZSI+PHhzOmNvbXBsZXh
 UeXBlPjx4czpzZXF1ZW5jZT48eHM6ZWxlbWVudCBuYW1lPSJCb3VuZGluZ0JveCI+PHhzOmNvbXB
 sZXhUeXBlPjx4czpzaW1wbGVDb250ZW50Pjx4czpleHRlbnNpb24gYmFzZT0ieHM6c3RyaW5nIj4
 8eHM6YXR0cmlidXRlIHR5cGU9InhzOmZsb2F0IiBuYW1lPSJsZWZ0Ii8+PHhzOmF0dHJpYnV0ZSB
 0eXBlPSJ4czpmbG9hdCIgbmFtZT0idG9wIi8+PHhzOmF0dHJpYnV0ZSB0eXBlPSJ4czpmbG9hdCI
 gbmFtZT0icmlnaHQiLz48eHM6YXR0cmlidXRlIHR5cGU9InhzOmZsb2F0IiBuYW1lPSJib3R0b20
 iLz48L3hzOmV4dGVuc2lvbj48L3hzOnNpbXBsZUNvbnRlbnQ+PC94czpjb21wbGV4VHlwZT48L3h
 zOmVsZW1lbnQ+PHhzOmVsZW1lbnQgbmFtZT0iQ2VudGVyT2ZHcmF2aXR5Ij48eHM6Y29tcGxleFR
 5cGU+PHhzOnNpbXBsZUNvbnRlbnQ+PHhzOmV4dGVuc2lvbiBiYXNlPSJ4czpzdHJpbmciPjx4czp
 hdHRyaWJ1dGUgdHlwZT0ieHM6ZmxvYXQiIG5hbWU9IngiLz48eHM6YXR0cmlidXRlIHR5cGU9Inh
 zOmZsb2F0IiBuYW1lPSJ5Ii8+PC94czpleHRlbnNpb24+PC94czpzaW1wbGVDb250ZW50PjwveHM

```

34 Open SDK


```
 6Y29tcGxleFR5cGU+PC94czplbGVtZW50PjwveHM6c2VxdWVuY2U+PC94czpjb21wbGV4VHlwZT4
 8L3hzOmVsZW1lbnQ+PHhzOmVsZW1lbnQgbmFtZT0iQ29sb3IiPjx4czpjb21wbGV4VHlwZT48eHM
 6c2VxdWVuY2U+PHhzOmVsZW1lbnQgbmFtZT0iQ29sb3JDbHVzdGVyIj48eHM6Y29tcGxleFR5cGU
 +PHhzOnNlcXVlbmNlPjx4czplbGVtZW50IG5hbWU9IkNvbG9yIj48eHM6Y29tcGxleFR5cGU+PHh
 zOnNpbXBsZUNvbnRlbnQ+PHhzOmV4dGVuc2lvbiBiYXNlPSJ4czpzdHJpbmciPjx4czphdHRyaWJ
 1dGUgdHlwZT0ieHM6Ynl0ZSIgbmFtZT0iWCIvPjx4czphdHRyaWJ1dGUgdHlwZT0ieHM6Ynl0ZSI
 gbmFtZT0iWSIvPjx4czphdHRyaWJ1dGUgdHlwZT0ieHM6c2hvcnQiIG5hbWU9IloiLz48L3hzOmV
 4dGVuc2lvbj48L3hzOnNpbXBsZUNvbnRlbnQ+PC94czpjb21wbGV4VHlwZT48L3hzOmVsZW1lbnQ
 +PHhzOmVsZW1lbnQgbmFtZT0iQ292YXJpYW5jZSI+PHhzOmNvbXBsZXhUeXBlPjx4czpzaW1wbGV
 Db250ZW50Pjx4czpleHRlbnNpb24gYmFzZT0ieHM6c3RyaW5nIj48eHM6YXR0cmlidXRlIHR5cGU
 9InhzOmZsb2F0IiBuYW1lPSJYWCIvPjx4czphdHRyaWJ1dGUgdHlwZT0ieHM6Ynl0ZSIgbmFtZT0
 iWVkiLz48eHM6YXR0cmlidXRlIHR5cGU9InhzOmJ5dGUiIG5hbWU9IlpaIi8+PC94czpleHRlbnN
 pb24+PC94czpzaW1wbGVDb250ZW50PjwveHM6Y29tcGxleFR5cGU+PC94czplbGVtZW50Pjx4czp
 lbGVtZW50IHR5cGU9InhzOmZsb2F0IiBuYW1lPSJXZWlnaHQiLz48L3hzOnNlcXVlbmNlPjwveHM
 6Y29tcGxleFR5cGU+PC94czplbGVtZW50PjwveHM6c2VxdWVuY2U+PC94czpjb21wbGV4VHlwZT4
 8L3hzOmVsZW1lbnQ+PHhzOmVsZW1lbnQgbmFtZT0iQ2xhc3MiPjx4czpjb21wbGV4VHlwZT48eHM
 6c2VxdWVuY2U+PHhzOmVsZW1lbnQgbmFtZT0iVHlwZSI+PHhzOmNvbXBsZXhUeXBlPjx4czpzaW1
 wbGVDb250ZW50Pjx4czpleHRlbnNpb24gYmFzZT0ieHM6c3RyaW5nIj48eHM6YXR0cmlidXRlIHR
 5cGU9InhzOmZsb2F0IiBuYW1lPSJMaWtlbGlob29kIi8+PC94czpleHRlbnNpb24+PC94czpzaW1
 wbGVDb250ZW50PjwveHM6Y29tcGxleFR5cGU+PC94czplbGVtZW50PjwveHM6c2VxdWVuY2U+PC9
 4czpjb21wbGV4VHlwZT48L3hzOmVsZW1lbnQ+PC94czpzZXF1ZW5jZT48L3hzOmNvbXBsZXhUeXB
 lPjwveHM6ZWxlbWVudD48L3hzOnNlcXVlbmNlPjx4czphdHRyaWJ1dGUgdHlwZT0ieHM6Ynl0ZSI
 gbmFtZT0iT2JqZWN0SWQiLz48eHM6YXR0cmlidXRlIHR5cGU9InhzOmJ5dGUiIG5hbWU9IlBhcmV
 udCIvPjwveHM6Y29tcGxleFR5cGU+PC94czplbGVtZW50PjwveHM6c2VxdWVuY2U+PHhzOmF0dHJ
 pYnV0ZSB0eXBlPSJ4czpkYXRlVGltZSIgbmFtZT0iVXRjVGltZSIvPjwveHM6Y29tcGxleFR5cGU
 +PC94czplbGVtZW50PjwveHM6c2VxdWVuY2U+PC94czpjb21wbGV4VHlwZT48L3hzOmVsZW1lbnQ
 +PC94czpzZXF1ZW5jZT48L3hzOmNvbXBsZXhUeXBlPjwveHM6ZWxlbWVudD48L3hzOnNjaGVtYT4
 =",
 "Encoding": "base64"
 }
 ]
 }
 ]
 }

```

SUNAPI 35


## **Chapter 8. Metaframe Capability**
### **8.1. Description**

The **metaframecapability** submenu, used to provide all supported values of a metadata field. Therefore,

the client can know what to expect based on this capability.


XPATH based capability notification mechanism is being used.


Providing the XPATH of the parameter and its data type and supported values or range.


If there are dependencies with another parameter, the dependency section is provided, for which XPATH

affects the supported values of this parameter.


Please check the example section.


**Access level**

|Action|Camera|
|---|---|
|view|User|


### **8.2. Syntax**

```
 http://<Device IP>/stw cgi/opensdk.cgi?msubmenu=metaframecapability&action=<value>[&<parameter>=<va
 lue>...]

### **8.3. Parameters**

```








|Action|Parameters|Request/<br>Response|Type/<br>Value|Description|
|---|---|---|---|---|
|view|Channel|REQ, RES|<int>|ChannelID, optional parameter in<br>request. If passed, result will be<br>filtered only for that channel.|
||AppID|REQ, RES|<string>|Application ID|
||Capabilities|RES|<string>|Capability Response|

### **8.4. Examples**

#### **8.4.1. Getting the metaframe capability of the installed apps.**

REQUEST

```
 http://<Device IP>/stw
```

36 Open SDK


```
 cgi/opensdk.cgi?msubmenu=metaframecapability&action=view

```

JSON RESPONSE

```
 HTTP/1.0 200 OK
 Content-type: application/json
 <Body>

 {
 "MetaFrameCapability": [
 {
 "Channel": 0,
 "AppCapabilities": [
 {
 "AppID": "SampleAIApp",
 "Capabilities": [
 {
 "xpath":
 "//tt:VideoAnalytics/tt:Frame/tt:Object/tt:Appearance/tt:LicensePlateInfo/tt
 :CountryCode",
 "type": "xs:string",
 "enum": [
 "KR",
 "US",
 "CN",
 "FN",
 "IN"
 ]
 },
 {
 "xpath":
 "//tt:VideoAnalytics/tt:Frame/tt:Object/tt:Appearance/tt:LicensePlateInfo/tt
 :PlateType",
 "type": "xs:string",
 "enum": [
 "Normal",
 "Police",
 "Diplomat",
 "Temporary"
 ]
 },

```

SUNAPI 37


```
 {
 "xpath":
 "//tt:VideoAnalytics/tt:Frame/tt:Object/tt:Appearance/tt:Class/tt:Type",
 "type": "xs:string",
 "enum": [
 "Vehicle",
 "Bicycle"
 ]
 },
 {
 "xpath":
 "//tt:VideoAnalytics/tt:Frame/tt:Object/tt:Appearance/tt:VehicleInfo/tt:Type
 ",
 "type": "xs:string",
 "enum": [
 "Car",
 "Bus"
 ]
 },
 {
 "xpath":
 "//tt:VideoAnalytics/tt:Frame/tt:Object/tt:Appearance/tt:VehicleInfo/tt:Bran
 d",
 "type": "xs:string",
 "enum": [
 "Kia",
 "Hyundai",
 "Volvo"
 ],
 "Dependency": [
 {
 "Condition":
 "//tt:VideoAnalytics/tt:Frame/tt:Object/tt:Appearance/tt:VehicleInfo/tt:Type
 [text()='Car']",
 "enum": [
 "Kia",
 "Hyundai"
 ]
 },
 {
 "Condition":

```

38 Open SDK


```
 "//tt:VideoAnalytics/tt:Frame/tt:Object/tt:Appearance/tt:VehicleInfo/tt:Type
 [text()='Bus']",
 "enum": [
 "Volvo"
 ]
 }
 ]
 },
 {
 "xpath":
 "//tt:VideoAnalytics/tt:Frame/tt:Object/tt:Appearance/tt:VehicleInfo/tt:Mode
 l",
 "type": "xs:string",
 "enum": [
 "K7",
 "Sonata",
 "Accent",
 "Soul"
 ],
 "Dependency": [
 {
 "Condition":
 "//tt:VideoAnalytics/tt:Frame/tt:Object/tt:Appearance/tt:VehicleInfo/tt:Type
 [text()='Car'] and
 //tt:VideoAnalytics/tt:Frame/tt:Object/tt:Appearance/tt:VehicleInfo/tt:Brand
 [text()='Kia']",
 "enum": [
 "K7",
 "Soul"
 ]
 },
 {
 "Condition":
 "//tt:VideoAnalytics/tt:Frame/tt:Object/tt:Appearance/tt:VehicleInfo/tt:Type
 [text()='Car'] and
 //tt:VideoAnalytics/tt:Frame/tt:Object/tt:Appearance/tt:VehicleInfo/tt:Brand
 [text()='Hyundai']",
 "enum": [
 "Sonata",
 "Accent"
 ]

```

SUNAPI 39


```
 }
 ]
 },
 {
 "xpath":
 "//tt:VideoAnalytics/tt:Frame/tt:Object/tt:Appearance/tt:Class/tt:Type/@Like
 lihood",
 "type": "xs:float",
 "minimum": 0,
 "maximum": 1
 },
 {
 "xpath":
 "//tt:VideoAnalytics/tt:Frame/tt:Object/tt:Appearance/tt:Color/tt:ColorClust
 er/tt:ColorString",
 "type": "xs:string",
 "enum": [
 "RED",
 "BLUE",
 "GREEN",
 "BLACK",
 "WHITE"
 ]
 }
 ]
 }
 ]
 }
 ]
 }

```

40 Open SDK


