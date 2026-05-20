### **Wisenet Open Platform v4.01**

# **Web Page Development Guide**



**v4.01**


**2021-05-31**



**Copyright**


© 2021 Hanwha Techwin Co., Ltd. All rights reserved.


**Trademark**


is logo of Hanwha Techwin Co., Ltd.

All other trademarks and trade names presented in this
document are the property of their respective holders.


**Restriction**


Copyright 2020 © Hanwha Techwin Co., Ltd. All rights
reserved. Do not copy, distribute, or reproduce any part of
this document without written approval from Hanwha
Techwin Co., Ltd.


**Disclaimer**


Hanwha Techwin Co., Ltd. has made every effort to ensure
the completeness and accuracy of this document, but
makes no guarantees regarding the information contained
herein. All responsibility for proper and safe use of the
information in this document lies with users. Hanwha
Techwin Co., Ltd. may revise or update this document
without prior notice.


**Contact Information**


HANWHA TECHWIN Co., LTD.

Hanwhatechwin R&D Center, 701, Sampyeong-dong,
Bundang-gu, Seongnam-si, Gyeonggi-do, Korea, 463-400

TEL: +82-70-7147-8740~60  FAX: +82-31-8018-3745

[https://step.hanwha-security.com/](https://step.hanwha-security.com/)


HANWHA TECHWIN AMERICA Inc.

100 Challenger Road Ridgefield Park, New Jersey, 07660
U.S.A.


HANWHA TECHWIN EUROPE LTD.

2nd Floor, No. 5 The Heights, Brooklands, Weybridge,
Surrey, KT13 0NY, U.K.


## **Revision History**

The table below provides the version information and revision history of this document.

Please refer to 2.0x documents for checking revision history before 3.00.


Wisenet Open Platform v4.01 Web Page Development Guide | 2


## **Table of Contents**

**Requirements ................................................................................................................................................................... 4**


**Functions ........................................................................................................................................................................... 4**


RequestAjaxMsg ............................................................................................................................................................................ 4


startApplication ............................................................................................................................................................................. 5


stopApplication ............................................................................................................................................................................. 7


getApplicationStatus ................................................................................................................................................................... 7


getApplicationSettings ............................................................................................................................................................... 8


updateApplicationSettings ....................................................................................................................................................... 9


sendCommandToServer ........................................................................................................................................................... 10


**Commands ...................................................................................................................................................................... 10**


SDK Command ............................................................................................................................................................................ 11


SDK_APP Command .................................................................................................................................................................. 12


SDK_APP_DATA Command ..................................................................................................................................................... 14


**References ....................................................................................................................................................................... 17**


**Limitations ...................................................................................................................................................................... 17**


Wisenet Open Platform v4.01 Web Page Development Guide | 3


## **Requirements**

To create an application using the SDK, a developer needs the following software and hardware.


ㆍ Linux, or Windows


ㆍ Wisenet Open Platform SDK


ㆍ Hanwha IP camera that supports Wisenet Open Platform

## **Functions**


These functions are defined in the camera to request information or to control 3 [rd] -party

applications. Please download home/js/SDKApi.js for the details on functions.

#### **RequestAjaxMsg**


**Define**


**RequestAjaxMsg function**


Wisenet Open Platform v4.01 Web Page Development Guide | 4


**Description**


This is the basic function to request/control the functions of the 3 [rd] -party application. This function

is defined in the main server of the camera, so it can be used only for starting/stopping the

application.


**Parameters**

|Members|Description|
|---|---|
|Msg|The string to start/stop the application*|
|alertMsg|To alert when the function call is failed<br>Use of this message is up to developer|
|reqUrl|The URL processes all request message|
|Command|SDK/SDK_APP/SDK_APP_DATA<br>See 3. Commands|
|asyncVal|For most cases, use “undefined”|



**Return**


This function returns no string when the request is processed successfully. If not, it returns the

“alertMsg” set by developer.


**Note**


*The format of “msg” is xml. Please see the following chapter.

#### **startApplication**


**Define**


**startApplication function**

|Method|Parameters|
|---|---|
|startApplication|paramJSON|



**Description**


This function is used for starting the application. This function is the same as when the SDK

command is used.


Wisenet Open Platform v4.01 Web Page Development Guide | 5


**Parameters**


Wisenet Open Platform v4.01 Web Page Development Guide | 6


**Return**


paramJSON parameter is updated without returning anything.

#### **stopApplication**


**Define**


**stopApplication function**

|Method|Parameters|
|---|---|
|stopApplication|paramJSON|



**Description**


This function is used for stopping the application. This function is the same as when the SDK

command is used.


**Parameters**

|Members|Description|
|---|---|
|paramJSON|JSON String that contains the following information:<br>appname: Name of the application.<br>success: Callback function when the application stops<br>successfully.<br>error: Callback function when the application doesn’t stop.|



**Return**


paramJSON parameter is updated without returning anything.

#### **getApplicationStatus**


**Define**


**getApplicationStatus function**


Wisenet Open Platform v4.01 Web Page Development Guide | 7


|Method|Parameters|
|---|---|
|getApplicationStatus|paramJSON|


**Description**


This function is used to fetch application status information. This function returns the status of an

application, such as running, stopped, etc.


**Parameters**

|Members|Description|
|---|---|
|paramJSON|JSON String that contains the following information:<br>appname: Name of the application.<br>success: Callback function when the application status<br>information is fetched successfully.|



**Return**


paramJSON parameter is updated without returning anything.

#### **getApplicationSettings**


**Define**


**getApplicationSettings function**

|Method|Parameters|
|---|---|
|getApplicationSettings|paramJSON|



**Description**


This function is used for fetching application settings information. This function is the same as

when the SDK_APP command is used.


**Parameters**

|Members|Description|
|---|---|
|paramJSON|JSON String that contains the following information:|



Wisenet Open Platform v4.01 Web Page Development Guide | 8


**Return**


paramJSON parameter is updated without returning anything.

#### **updateApplicationSettings**


**Define**


**updateApplicationSettings function**

|Method|Parameters|
|---|---|
|updateApplicationSettings|paramJSON|



**Description**


This function is used for updating the application settings information. This function is the same as

when the SDK_APP command is used.


**Parameters**

|Members|Description|
|---|---|
|paramJSON|JSON String that contains following information:<br>appname : Name of the application.<br>appconfig : Application configuration data.<br>success: Callback function called when settings information<br>is updated successfully.<br>error : Callback function when there is an error.|



**Return**


paramJSON parameter is updated without returning anything.


Wisenet Open Platform v4.01 Web Page Development Guide | 9


#### **sendCommandToServer**

**Define**


**sendCommandToServer function**

|Method|Parameters|
|---|---|
|sendCommandToServer|paramJSON|



**Description**


This function is used for sending requests to the server. This function is the same as when

SDK_APP_DATA command is used.


**Parameters**

|Members|Description|
|---|---|
|paramJSON|JSON String that contains the following information :<br>appname: Name of the application.<br>requestMessage: message String containing request.<br><GetSDK_APP_DATA><br><AppName>application_name</AppName><br><Data>…</Data><br></GetSDK_APP_DATA><br>success: Callback function called with response from the<br>server.<br>error: Callback function in case of error.|



**Return**


paramJSON parameter is updated without returning anything.

## **Commands**


Wisenet Open Platform v4.01 Web Page Development Guide | 10


The following commands provide a way to communicate with the application and main server.


**Parameters**


**Web communication commands**

|Command|Description|
|---|---|
|SDK|To control the application, such as start/stop|
|SDK_APP|To set/get the setting of the application|
|SDK_APP_DATA|To communicate with the application, use this command|


#### **SDK Command**


This command is used to start/stop the application using the 3 [rd] -party application’s own web page.


**Syntax:**

|Usage|Syntax|
|---|---|
|Start the app|<StartSDK><br><AppName>application_name</AppName><br></StartSDK>|
|Stop the app|<StopSDK><br><AppName>application_name</AppName><br></StopSDK>|



**Description**


Syntax is the message used as a parameter(“msg”) for RequestAjaxMsg function. Developer should

use the whole application name for “application_name” as defined in IPCameraManifest.xml file.


**Return**


After the function RequesAjaxMsg is called, the web page is reloaded regardless of success. If the

function fails to start/stop the application, the web page shows the alert message(“alertMsg”) as a

popup.


Wisenet Open Platform v4.01 Web Page Development Guide | 11


#### **SDK_APP Command**

This command is used to set/get the settings of the application, especially the setting values

defined in IPCameraManifest.xml


**Syntax:**

|Usage|Syntax|
|---|---|
|Set the settings|<SetSDK_APP><br><AppName>application_name</AppName><br><VideoEncoding>…</VideoEncoding><br><rawVideo>…</rawVideo><br><appConfigData>…</appConfigData><br><vaEvent>…</vaEvent><br><rawAudio>…</rawAudio><br></SetSDK_APP>|
|Get the settings|<GetSDK_APP><br><AppName>application_name</AppName><br></GetSDK_APP>|



**Description**


Syntax is the message used as a parameter for request function(request function will be defined).

Developer should put the whole application name in “application_name” as defined in

IPCameraManifest.xml file.


**Function Define**


**Request function**

|Method|Parameters|
|---|---|
|(up to developer)|msg, alertMsg, reqUrl, command, asyncVal|



**Function Description**


This is the function to set/get the basic information defined in IPCameraManifest.xml file. This

function is defined based on RequestAjaxMsg function.


Wisenet Open Platform v4.01 Web Page Development Guide | 12


**Function Parameters**

|Members|Description|
|---|---|
|Msg|The string to set/get the IPCameraManifest.xml|
|alertMsg|To alert when the function call is failed<br>The use of this message is up to the developer|
|reqUrl|The URL processes all request messages|
|Command|SDK_APP|
|asyncVal|In most cases, use “undefined”|



**Function Return**

|Usage|Syntax|
|---|---|
|Success to set|<Results><br><Status>OK</Status><br></Results>|
|Success to get|IPCameraManifest.xml in xml format|
|Fail to set/get|<Error><br><ErrorString>ERROR: Configuration file not found<br></ErrorString><br></Error>|



**Function Example:**

























Wisenet Open Platform v4.01 Web Page Development Guide | 13


#### **SDK_APP_DATA Command**

This command is used to communicate with the application. The sequence diagram of this

command is as shown in the picture below.


When the camera receives “SDK_APP_DATA” messages from the web, it sends the message to the

application, especially “recv_data(void*, void*)”.


The function(recv_data()) has 2 parameters to receive and send messages; the first parameter (void

*payload_request) is to receive the message from the camera(from the web) and the second (void

*payload_response) is to send the message to the camera(to the web).


See the main source code when you make a project in Docker.


Wisenet Open Platform v4.01 Web Page Development Guide | 14


**sd SDK_APP_DATA**


User







**Application**





process_msg_in_app()


|con|Col2|
|---|---|
|||
||recv_data(payload_response)|





**Syntax:**



|Usage|Syntax|
|---|---|
|Send the message to<br>application|<SetSDK_APP_DATA><br><AppName>application_name</AppName><br><Data>…</Data><br></SetSDK_APP_DATA><br> <br><GetSDK_APP_DATA><br><AppName>application_name</AppName><br><Data>…</Data><br></GetSDK_APP_DATA>|


**Description**





Syntax is the message used as a parameter for request function (see the example below). The

developer should put the whole application name in “application_name” as defined in

IPCameraManifest.xml file.


**Function Example**

```
function GetSettings()

```

Wisenet Open Platform v4.01 Web Page Development Guide | 15


All messages to get/set data (SDK_APP_DATA command) will be sent to recv_data(void *, void *) in

the application.


Wisenet Open Platform v4.01 Web Page Development Guide | 16


## **References**

Please refer to ServerPushMJPEGApp/html/index.html for examples on the use of functions.

## **Limitations**


Recommended to use the functions of 3.50 or higher version.


Wisenet Open Platform v4.01 Web Page Development Guide | 17


