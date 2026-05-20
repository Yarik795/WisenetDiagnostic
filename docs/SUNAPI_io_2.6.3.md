# I/O


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

2. Alarm Output . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . 5

2.1. Description . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . 5

2.2. Syntax . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . 5

2.3. Parameters . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . 5

2.4. Examples . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . 6

2.4.1. Getting the current alarm output settings . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . 6

2.4.2. Turning on Alarm Output 1 with continuous output . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . 9

2.4.3. Setting the duration of Alarm Output 1 to 10 seconds. . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . 9

3. Auxiliary Devices . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . 10

3.1. Description . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . 10

3.2. Syntax . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . 10

3.3. Parameters . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . 10

3.4. Examples . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . 10

3.4.1. Getting the current auxiliary device settings . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . 10

3.4.2. Deactivating the auxiliary device 1 . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . 11

4. User Input State . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . 12

4.1. Description . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . 12

4.2. Syntax . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . 12

4.3. Parameters . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . 12

4.4. Examples . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . 12

4.4.1. Getting the current User Input state. . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . 12

4.4.2. Deactivating the User Input . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . 13

5. Alarm Reset . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . 14

5.1. Description . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . 14

5.2. Syntax . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . 14

5.3. Parameters . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . 14

5.4. Examples . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . 14

5.4.1. Getting the current User Input state. . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . 14

6. IO Ports Configuration . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . 15

6.1. Description . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . 15

6.2. Syntax . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . 15

6.3. Parameters . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . 15

6.4. Examples . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . 15

6.4.1. Getting the configurable alarm IO settings . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . 15


2 I/O


6.4.2. Setting the operation mode of the configurable alarm IO port 1 to "Output" . . . . . . . . . . . . . . . 16

7. LED Control . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . 17

7.1. Description . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . 17

7.2. Syntax . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . 17

7.3. Parameters . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . 17

7.4. Examples . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . 18

7.4.1. Getting the current LED Status . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . 18

7.4.2. Turn off LEDUsageIndex 1 . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . 18


SUNAPI 3


## **Chapter 1. Overview**
### **1.1. Description**

**io.cgi** configures the alarm output settings. It gives manual control to the end user to perform control

operations on alarm output at any time.


The following submenus are used for I/O functionalities:


 - **alarmoutput** : Sets and controls the alarm output, state and duration.


 - **aux** : Controls the auxiliary equipment state.


 - **userinput** : Controls the on/off state of the manual trigger event.


 - **alarmreset** : Resets the alarm.


 - **ioport** : Sets the configurable alarm IO modes.


 - **ledcontrol** : It can check current LED’s status or turn off LED.


4 I/O


## **Chapter 2. Alarm Output**
### **2.1. Description**

The **alarmoutput** submenu configures the alarm output settings.


Attribute to check for alarm outputs support: "attributes/IO/Support/AlarmOutput"
**NOTE**

Attribute to check for maximum alarm outputs: "attributes/IO/Limit/MaxAlarmOutput"


**Access level**

|Action|Camera|NVR|
|---|---|---|
|view|Suser|User|
|control|Suser|User|
|set|Suser|User|


### **2.2. Syntax**

```
 http://<Device IP>/stw-cgi/io.cgi?msubmenu=
 alarmoutput &action=<value>[&<parameter>=<value>...]

### **2.3. Parameters**

```





















|Action|Parameters|Request/<br>Response|Type/<br>Value|Description|
|---|---|---|---|---|
|view||||Reads the alarm output values.|
||AlarmOutput.#.Type|RES|<enum><br>Alarmout,<br>Beep|Alarm output type<br>(read-only)|
||AlarmOutput.#.IOPortIn<br>dex|RES|<int>|IO port index<br>It shows the real index of IO port.<br>User can match logical and real index<br>with this parameter..<br>**CAMERA ONLY**<br>|
|control|AlarmOutput.#.State|REQ|<enum><br>On, Off|Turns the alarm on or off.<br>**Note**<br>**AlarmOutput.#.State** must be<br>sent together with the**control**<br>action.|



SUNAPI 5


|Action|Parameters|Request/<br>Response|Type/<br>Value|Description|
|---|---|---|---|---|
||AlarmOutput.#.ManualD<br>uration|REQ|<enum><br>Always, 1s,<br>2s, 3s, 4s,<br>5s, 6s, 7s,<br>8s, 9s, 10s,<br>11s, 12s,<br>13s, 14s,<br>15s|Alarm output duration<br>**AlarmOutput.#.ManualDuration** is<br>only valid if**AlarmOutput.#.State** is<br>set as On.<br>**CAMERA ONLY**<br>|
|set|AlarmOutput.#.IdleState|REQ, RES|<enum><br>NormallyO<br>pen,<br>NormallyCl<br>ose|Alarm output state (read only for NVR)|
||AlarmOutput.#.<dddh>|REQ, RES|<enum><br>Off, On,<br>EventSync|Alarm output time<br><dddh> stands for the day of the week<br>and time in hours. e.g. SUN1 means<br>1:00 AM on Sunday. and MON2 means<br>2:00 AM on Monday.<br>**NVR ONLY**<br>|
||AlarmOutput.#.ManualD<br>uration|REQ, RES|<enum><br>Always, 1s,<br>2s, 3s, 4s,<br>5s, 6s, 7s,<br>8s, 9s, 10s,<br>11s, 12s,<br>13s, 14s,<br>15s|Alarm output default duration|



**NOTE** # represents the index number of the alarm output.

### **2.4. Examples**

#### **2.4.1. Getting the current alarm output settings**

REQUEST

```
 http://<Device IP>/stw-cgi/io.cgi?msubmenu=alarmoutput&action=view

```

CAMERA TEXT RESPONSE

```
 HTTP/1.0 200 OK

```

6 I/O


```
 Content-type: text/plain
 <Body>

 AlarmOutput.1.Type=Alarmout
 AlarmOutput.1.IdleState=NormallyOpen
 AlarmOutput.1.ManualDuration=Always
 AlarmOutput.1.IOPortIndex=2

```

CAMERA JSON RESPONSE

```
 HTTP/1.0 200 OK
 Content-type: application/json
 <Body>

 {
 "AlarmOutputs": [
 {
 "AlarmOutput": 1,
 "Type": "Alarmout",
 "IdleState": "NormallyOpen",
 "ManualDuration": "Always",
 "IOPortIndex": 2
 }
 ]
 }

```

NVR TEXT RESPONSE

```
 HTTP/1.0 200 OK
 Content-type: text/plain
 <Body>

 AlarmOutput.1.Type=Alarmout
 AlarmOutput.1.IdleState=NormallyOpen
 AlarmOutput.1.SUN0=EventSync
 AlarmOutput.1.SUN1=EventSync
 AlarmOutput.1.SUN2=EventSync
 AlarmOutput.1.SUN3=EventSync

```

SUNAPI 7


```
 ...

```

NVR JSON RESPONSE

```
 HTTP/1.0 200 OK
 Content-type: application/json
 <Body>

 {
 "AlarmOutputs": [
 {
 "AlarmOutput": 1,
 "Type": "Alarmout",
 "IdleState": "NormallyOpen",
 "SUN": [
 "Off",
 "Off",
 "Off",
 "Off",
 "Off",
 "Off",
 "Off",
 "Off",
 "Off",
 "On",
 "On",
 "On",
 "On",
 "On",
 "On",
 "On",
 "On",
 "EventSync",
 "EventSync",
 "EventSync",
 "EventSync",
 "EventSync",
 "EventSync",
 "EventSync"
 ],
 "MON": [

```

8 I/O


```
 ...
 ],
 ...
 "FRI": [...]
 }
 ]
 }

#### **2.4.2. Turning on Alarm Output 1 with continuous output**
```

REQUEST

```
 http://<Device IP>/stw cgi/io.cgi?msubmenu=alarmoutput&action=control&AlarmOutput.1.State=On&AlarmO
 utput.1.ManualDuration=Always

```

The following request example is for NVR only.


REQUEST

```
 http://<Device IP>/stw cgi/io.cgi?msubmenu=alarmoutput&action=control&AlarmOutput.1.State=On

#### **2.4.3. Setting the duration of Alarm Output 1 to 10 seconds**
```

REQUEST

```
 http://<Device IP>/stw cgi/io.cgi?msubmenu=alarmoutput&action=set&AlarmOutput.1.IdleState=NormallyO
 pen&AlarmOutput.1.ManualDuration=10s

```

SUNAPI 9


## **Chapter 3. Auxiliary Devices**
### **3.1. Description**

The **aux** submenu controls the auxiliary device on/off state.


This chapter applies to the network cameras only.



**NOTE**


**Access level**



Attribute to check for auxiliary devices support: "attributes/IO/Support/Aux"

Attribute to check for maximum auxiliary devices: "attributes/IO/Limit/MaxAux"



|Action|Camera|
|---|---|
|view|Suser|
|control|Suser|

### **3.2. Syntax**

```
 http://<Device IP>/stw-cgi/io.cgi?msubmenu=
 aux &action=<value>[&<parameter>=<value>...]

### **3.3. Parameters**

```













|Action|Parameters|Request/<br>Response|Type/<br>Value|Description|
|---|---|---|---|---|
|view||||Reads the auxiliary device settings.|
||Aux.#.State|RES|<enum><br>On, Off|Auxiliary device state|
|control|Aux.#.State|REQ|<enum><br>On, Off|Auxiliary device state<br>**Note**<br>**Aux.#.State** must be sent<br>together with the**control** action.|



**NOTE** # represents the index number of the auxiliary device.

### **3.4. Examples**

#### **3.4.1. Getting the current auxiliary device settings**


10 I/O


REQUEST

```
 http://<Device IP>/stw-cgi/io.cgi?msubmenu=aux&action=view

```

TEXT RESPONSE

```
 HTTP/1.0 200 OK
 Content-type: text/plain
 <Body>

 Aux.1.State=On
 Aux.2.State=Off

```

JSON RESPONSE

```
 HTTP/1.0 200 OK
 Content-type: application/json
 <Body>

 {
 "AuxDevices": [
 {
 "Aux": 1,
 "State": "On"
 },
 {
 "Aux": 2,
 "State": "Off"
 }
 ]
 }

#### **3.4.2. Deactivating the auxiliary device 1**
```

REQUEST

```
 http://<Device IP>/stw cgi/io.cgi?msubmenu=aux&action=control&Aux.1.State=Off

```

SUNAPI 11


## **Chapter 4. User Input State**
### **4.1. Description**

The **userinput** submenu controls the User Input on/off state. When User Input is ‘on’, an event can be

manually triggered by a user.


This chapter applies to the network cameras only.
**NOTE**

Attribute to check for User Input support: "attributes/Eventsource/Support/UserInput"


**Access level**

|Action|Camera|
|---|---|
|view|Admin|
|control|Admin|


### **4.2. Syntax**

```
 http://<Device IP>/stw-cgi/io.cgi?msubmenu=
 userinput &action=<value>[&<parameter>=<value>...]

### **4.3. Parameters**

```










|Action|Parameters|Request/<br>Response|Type/<br>Value|Description|
|---|---|---|---|---|
|view||||Reads the user input state.|
||State|RES|<enum><br>On, Off|User input state|
|control|State|REQ|<enum><br>On, Off|User input state<br>**Note**<br>**State** must be sent together with<br>the**control** action.|

### **4.4. Examples**

#### **4.4.1. Getting the current User Input state**

REQUEST




```
 http://<Device IP>/stw-cgi/io.cgi?msubmenu=userinput&action=view

```

12 I/O


TEXT RESPONSE

```
 HTTP/1.0 200 OK
 Content-type: text/plain
 <Body>

 State=On

```

JSON RESPONSE

```
 HTTP/1.0 200 OK
 Content-type: application/json
 <Body>

 {
 "State": "On"
 }

#### **4.4.2. Deactivating the User Input**
```

REQUEST

```
 http://<Device IP>/stw cgi/io.cgi?msubmenu=userinput&action=control&State=Off

```

SUNAPI 13


## **Chapter 5. Alarm Reset**
### **5.1. Description**

The **alarmreset** submenu resets the alarm.


**NOTE** This chapter applies to NVR only.


**Access level**

|Action|NVR|
|---|---|
|control|User|


### **5.2. Syntax**

```
 http://<Device IP>/stw-cgi/io.cgi?msubmenu=
 alarmreset &action=<value>[&<parameter>=<value>...]

### **5.3. Parameters**

```








|Action|Parameters|Request/<br>Response|Type/<br>Value|Description|
|---|---|---|---|---|
|control|Reset|REQ||Alarm reset<br>No value is required for this<br>parameter.|

### **5.4. Examples**

#### **5.4.1. Getting the current User Input state**

REQUEST

```
 http://<Device IP>/stw-cgi/io.cgi?msubmenu=alarmreset&action=control

```

14 I/O


## **Chapter 6. IO Ports Configuration**
### **6.1. Description**

The **ioport** submenu configures the configurable alarm IO port.


This chapter applies to network cameras only.

Attribute to check for configurable alarm IO support:



**NOTE**


**Access level**



"attributes/IO/Support/ConfigurableIO"

Attribute to check for maximum configurable alarm IO:

"attributes/IO/Limit/MaxConfigurableIO"



|Action|Camera|
|---|---|
|view|Admin|
|set|Admin|

### **6.2. Syntax**

```
 http://<Device IP>/stw-cgi/io.cgi?msubmenu=
 ioport &action=<value>[&<parameter>=<value>...]

### **6.3. Parameters**

```










|Action|Parameters|Request/<br>Response|Type/<br>Value|Description|
|---|---|---|---|---|
|view||||Reads the configurable alarm IO<br>settings|
||Port|REQ|<csv>|Physical port number|
|set|Port.#.Mode|REQ, RES|<enum><br>Input,<br>Output|Port operation mode|

### **6.4. Examples**

#### **6.4.1. Getting the configurable alarm IO settings**

REQUEST




```
 http://<Device IP>/stw-cgi/io.cgi?msubmenu=ioport&action=view

```

SUNAPI 15


TEXT RESPONSE

```
 HTTP/1.0 200 OK
 Content-type: text/plain
 <Body>

 Port.1.Mode=Input
 Port.2.Mode=Output

```

JSON RESPONSE

```
 HTTP/1.0 200 OK
 Content-type: application/json
 <Body>

 {
 "Ports": [
 {
 "Port": 1,
 "Mode": "Input"
 },
 {
 "Port": 2,
 "Mode": "Output"
 }
 ]
 }

#### **6.4.2. Setting the operation mode of the configurable alarm IO port 1 to** **"Output"**
```

REQUEST

```
 http://<Device IP>/stw cgi/io.cgi?msubmenu=ioport&action=set&Port.1.Mode=Output

```

16 I/O


## **Chapter 7. LED Control**
### **7.1. Description**

The **ledcontrol** submenu controls LED Mode(turning off) and checks LED status.


**Access level**

|Action|Camera|LEDBox|
|---|---|---|
|check|Admin|Admin|
|control|Admin|Admin|


### **7.2. Syntax**

```
 http://<Device IP>/stw-cgi/io.cgi?msubmenu=
 ledcontrol &action=<value>[&<parameter>=<value>...]

### **7.3. Parameters**

```



















|Action|Parameters|Request/<br>Response|Type/<br>Value|Description|
|---|---|---|---|---|
|check||||Reads the LED status.|
||LED.#.Color|RES|<enum><br>Green,<br>Blue, Red,<br>Pink,<br>SkyBlue,<br>Purple|User input state|
||LED.#.LightMode|RES|<enum><br>On, Off||
||LED.#.LEDPresetIndex|RES|<int>|By using "eventrules"cgi "ledpreset"<br>submenu "control" action, you can<br>apply LEDPresetIndex to LED. It Shows<br>which index is being used. * 0: Not<br>set, * #: Being used preset index|
|control|LightMode|REQ|<enum><br>Off|Control Light Mode * Off: Turn off|



SUNAPI 17


|Action|Parameters|Request/<br>Response|Type/<br>Value|Description|
|---|---|---|---|---|
||LEDIndex|REQ|<csv>|Select which<br>LEDUsageIndex(eventrules.cgi<br>ledpreset submenu) to apply. If<br>hardware has 1 LED, only 1 is<br>available.|

### **7.4. Examples**

#### **7.4.1. Getting the current LED Status**

REQUEST

```
 http://<Device IP>/stw-cgi/io.cgi?msubmenu=ledcontrol&action=check

```

JSON RESPONSE

```
 HTTP/1.0 200 OK
 Content-type: application/json
 <Body>

 {
 "ledcontrol": [
 {
 "LED": 1,
 "LightMode": "Off",
 "LEDPresetIndex": 0
 },
 {
 "LED": 2,
 "LightMode": "Off",
 "LEDPresetIndex": 0
 }
 ]
 }

#### **7.4.2. Turn off LEDUsageIndex 1**
```

REQUEST

```
 http://<Device IP>/stw
```

18 I/O


```
 cgi/io.cgi?msubmenu=ledcontrol&action=control&LightMode=Off&LEDIndex=1

```

JSON RESPONSE

```
 HTTP/1.0 200 OK
 Content-type: application/json
 <Body>

 {
 "Response": "Success"
 }

```

SUNAPI 19


