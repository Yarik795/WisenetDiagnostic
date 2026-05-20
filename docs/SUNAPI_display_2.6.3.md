# Display


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

2. Decoder Board Info. . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . 4

2.1. Description . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . 4

2.2. Syntax . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . 4

2.3. Parameters . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . 4

2.4. Examples . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . 4

2.4.1. Getting connected board information . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . 4

2.4.2. Setting max allowed board counts . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . 6

3. Wall . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . 8

3.1. Description . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . 8

3.2. Syntax . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . 8

3.3. Parameters . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . 8

3.4. Examples . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . 11

3.4.1. Getting wall configuration information . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . 11

3.4.2. Adding wall (1 monitor, 1 layout) configuration information . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . 14

3.4.3. Updating (1 monitor, 1 layout) configuration information . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . 15

3.4.4. Updating (1 monitor, 1 layout) current layout index . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . 16

3.4.5. Removing wall configuration information . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . 16

3.4.6. Control wall mode register . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . 17

3.4.7. Control wall mode show . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . 18

4. Encoder video out layout . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . 19

4.1. Description . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . 19

4.2. Syntax . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . 19

4.3. Parameters . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . 19

4.4. Examples . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . 19

4.4.1. Getting the current layout mode . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . 19

4.4.2. Setting the layout mode to 4x4 . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . 20

5. SpotOut. . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . 21

5.1. Description . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . 21

5.2. Syntax . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . 21

5.3. Parameters . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . 21

5.4. Examples . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . 21

5.4.1. Getting spotout configuration information . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . 21

5.4.2. Setting spotout configuration information . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . 22


2 Display


## **Chapter 1. Overview**
### **1.1. Description**

**display.cgi** is used for changing the monitor layout configuration.


The following submenus are used for the monitor layout functionalities:


 - **decoderboardinf** : Requests the connected board information and configures the maximum allowed

bord count.


 - **wall** : Adds, updates, controls, and removes the monitor layout for each connected board.


 - **videooutlayout** : Configures layout modes for encoder models.


 - **spotout** : Configures the layout of analog video output.


**NOTE** This chapter applies to decoders (NVR) only.


SUNAPI 3


## **Chapter 2. Decoder Board Info**
### **2.1. Description**

The **decoderboardinfo** submenu gets connected decoder board information and configures the

maximum allowed board count.


**Access level**

|Action|Camera|NVR|Decoder|
|---|---|---|---|
|view|-|-|User|
|set|-|-|User|


### **2.2. Syntax**

```
 http://<Device IP>/stw-cgi/display.cgi?msubmenu=
 decoderboardinfo &action=<value>[&<parameter>=<value>]

### **2.3. Parameters**

```








|Action|Parameters|Request/<br>Response|Type/<br>Value|Description|
|---|---|---|---|---|
|view|Index.#.Inserted|RES|<int>|Inserted board number|
||Index.#.IsReady|RES|<bool>|Board enable status|
|set|AllowedBoardsCount|RES, REQ|<int>|Max. allowed board count|

### **2.4. Examples**

#### **2.4.1. Getting connected board information**

REQUEST

```
 http://<Device IP>/stw-cgi/display.cgi?msubmenu= decoderboardinfo &action=view

```

TEXT RESPONSE

```
 AllowedBoardsCount=8
 Index.1.Inserted=True
 Index.1.IsReady=True
 Index.2.Inserted=True
 Index.2.IsReady=True
 Index.3.Inserted=False

```

4 Display


```
 Index.3.IsReady=False
 Index.4.Inserted=False
 Index.4.IsReady=False
 Index.5.Inserted=False
 Index.5.IsReady=False
 Index.6.Inserted=False
 Index.6.IsReady=False
 Index.7.Inserted=False
 Index.7.IsReady=False
 Index.8.Inserted=False
 Index.8.IsReady=False

```

JSON RESPONSE

```
 HTTP/1.0 200 OK
 Content-type: application/json
 <Body>

 {
 "AllowedBoardsCount": 8,
 "DecoderBoards": [
 {
 "Index": 1,
 "Inserted": true,
 "IsReady": true
 },
 {
 "Index": 2,
 "Inserted": true,
 "IsReady": true
 },
 {
 "Index": 3,
 "Inserted": false,
 "IsReady": false
 },
 {
 "Index": 4,
 "Inserted": false,
 "IsReady": false
 },

```

SUNAPI 5


```
 {
 "Index": 5,
 "Inserted": false,
 "IsReady": false
 },
 {
 "Index": 6,
 "Inserted": false,
 "IsReady": false
 },
 {
 "Index": 7,
 "Inserted": false,
 "IsReady": false
 },
 {
 "Index": 8,
 "Inserted": false,
 "IsReady": false
 }
 ]
 }

#### **2.4.2. Setting max allowed board counts**
```

REQUEST

```
 http://<Device IP>/stw-cgi/display.cgi?msubmenu=
 decoderboardinfo &action=set&AllowedBoardsCount=2

```

TEXT RESPONSE

```
 OK

```

JSON RESPONSE

```
 HTTP/1.0 200 OK
 Content-type: application/json
 <Body>

 {

```

6 Display


```
 "Response": "Success"
 }

```

SUNAPI 7


## **Chapter 3. Wall**
### **3.1. Description**

The **wall** submenu adds, updates, controls, and removes the monitor layout for each connected board.


In SPD-150/151 decoder models, this submenu is not supported when DeviceMode is
**NOTE**

configured as Stand Alone mode.


**Access level**

|Action|Camera|NVR|Decoder|
|---|---|---|---|
|view|-|User|User|
|add/update|-|User|User|
|control|-|User|User|
|remove|-|User|User|


### **3.2. Syntax**

```
 http://<Device IP>/stw-cgi/display.cgi?msubmenu=
 wall &action=<value>[&<parameter>=<value>]

### **3.3. Parameters**

```













|Action|Parameters|Request/<br>Response|Type/<br>Value|Description|
|---|---|---|---|---|
|view|Index|REQ|<csv>|Wall index|
|add/update|Index.#.Name|REQ,RES|<string>|Inserted board number|
||Index.#.SplitMode|REQ,RES|<string>|Format=NoOfRowsxNoOfColumns<br>1X1…|
||Index.#.MonitorOut|REQ,RES|<csv>|Display monitor index|
||Index.#.Coordinates|REQ,RES|<string>|Format=x1,y1,x2,y2|
||Index.#.EnableSequence|REQ,RES|<bool><br>True, False|Enable wall sequence|



8 Display


|Action|Parameters|Request/<br>Response|Type/<br>Value|Description|
|---|---|---|---|---|
||Index.#.Layout.#.Name|REQ,RES|<string>|Layout name<br>**Note**<br>Layout Name**Update** action<br>doesn’t work, if that layout is in<br>use.|
||Index.#.Layout.#.IsCurre<br>ntLayout|REQ,RES|<bool><br>True, False|Current layout|
||Index.#.Layout.#.Enable<br>Sequence|REQ,RES|<bool>|Monitor display sequence enabled|
||Index.#.Layout.#.Sequen<br>ceTime|REQ,RES|<int>|Display sequence time|
||Index.#.Layout.#.Monito<br>rOut.#.SplitMode|REQ,RES|<enum><br>1x1, 2x2,<br>3x3, 4x4|Each monitor split mode|
||Index.#.Layout.#.Monito<br>rOut.#.Tile.#.SourceType|REQ,RES|<enum><br>Stream,<br>MonitorIn,<br>None|Display source type|
||Index.#.Layout.#.Monito<br>rOut.#.Tile.#.MonitorIn|RES|<int>|If SourceType=MonitorIn|
||Index.#.Layout.#.Monito<br>rOut.#.Tile.#.Channel|REQ,RES|<int>|Channel number<br>This parameter is only valid if<br>**SourceType** is set to Stream.|
||Index.#.Layout.#.Monito<br>rOut.#.Tile.#.Profile|REQ,RES|<Int>|If SourceType=Stream|
||Index.#.Layout.#.Monito<br>rOut.#.Tile.#.Coordinates|REQ,RES|<string>|Format=x1,y1,x2,y2|
||Index.#.Layout.#.Monito<br>rOut.#.Tile.#.Location|REQ,RES|<string>|Format=RowxColumn|
||Index.#.Layout.#.Monito<br>rOut.#.Tile.#.MergeID|REQ,RES|<int>|Tile merge id|
||Index.#.Layout.#.Monito<br>rOut.#.Tile.#.Merge|REQ,RES|<string>|Format=NoOfRowsxNoOfColumns|
||Index.#.Layout.#.Monito<br>rOut.#.Tile.#.ImageLocat<br>ion|REQ,RES|<string>|Format=RowxColumn|



SUNAPI 9


|Action|Parameters|Request/<br>Response|Type/<br>Value|Description|
|---|---|---|---|---|
|update|Index.#.MonitorOut.\#.C<br>urrentLayoutIndex=\#|REQ|<int>|The index of the layout depends on<br>the current wall’s index. Index.# : Wall<br>index MonitorOut.# : Monitor<br>index(number) CurrentLayoutIndex :<br>LayoutIndex<br>**NOTE**<br>CurrentLayoutIndex:<br>main monitor layout<br>index (the index is<br>smaller than the<br>number of layouts).|
|control|Mode|REQ|<enum><br>Register,<br>Show|Control action is possible only when<br>the decoder is in vms mode.|
||IsStreamServerPassword<br>Encrypted|REQ|<bool><br>True, False|If SourceType=Stream|
||CommonUserID|REQ|<string>|Each camera (channel) RTSP account|
||CommonPassword|REQ|<string>|Rtsp password|
||MonitorOut.#.SplitMode|REQ|<enum><br>1x1, 2x1,<br>2x2, 3x1,<br>3x3, 4x4,<br>1+5, 1+7,<br>1+12|Each monitor split mode|
||MonitorOut.#.Tile.#.Sour<br>ceType|REQ|<enum><br>Stream,<br>MonitorIn|Display source type|
||MonitorOut.#.Tile.#.Actio<br>nType|REQ|<enum><br>MediaOpen<br>,<br>MediaClose|Stream control|
||MonitorOut.#.Tile.#.High<br>ProfileRTSPURL|REQ|<string>|If SourceType=Stream|
||MonitorOut.#.Tile.#.Low<br>ProfileRTSPURL|REQ|<string>|If SourceType=Stream|
||MonitorOut.#.Tile.#.Stre<br>amServerUserID|REQ|<string>|If SourceType=Stream|
||MonitorOut.#.Tile.#.Stre<br>amServerPassword|REQ|<string>|If SourceType=Stream|



10 Display


|Action|Parameters|Request/<br>Response|Type/<br>Value|Description|
|---|---|---|---|---|
||MonitorOut.#.Tile.#.Cam<br>eraIP|REQ|<string>|If SourceType=Stream|
||MonitorOut.#.Tile.#.Cam<br>eraName|REQ|<string>|If SourceType=Stream|
||MonitorOut.#.Tile.#.Coor<br>dinates|REQ|<string>|Format=x1,y1,x2,y2|
||MonitorOut.#.Tile.#.Mer<br>ge|REQ|<string>|Format=NoOfRowsxNoOfColumns|
||MonitorOut.#.Tile.#.Ima<br>geCoordinates|REQ|<string>|Format=x1,y1,x2,y2|
|remove|Index|REQ|<csv>|Wall index number|
||Index.#.Layout|REQ|<csv>|Wall attached layout number|

### **3.4. Examples**

#### **3.4.1. Getting wall configuration information**

REQUEST

```
 http://<Device IP>/stw-cgi/display.cgi?msubmenu= wall &action=view&index=2

```

TEXT RESPONSE

```
 Index.2.Name=Wall 02
 Index.2.SplitMode=1x1
 Index.2.MonitorOut=2
 Index.2.Coordinates=13.4348,0,11,11
 Index.2.EnableSequence=False
 Index.2.Layout.1.Name=Layout 01
 Index.2.Layout.1.IsCurrentLayout=True
 Index.2.Layout.1.EnableSequence=True
 Index.2.Layout.1.SequenceTime=10
 Index.2.Layout.1.MonitorOut.2.SplitMode=2x2
 Index.2.Layout.1.MonitorOut.2.Tile.1.SourceType=Stream
 Index.2.Layout.1.MonitorOut.2.Tile.1.MonitorIn=1
 Index.2.Layout.1.MonitorOut.2.Tile.1.Channel=0
 Index.2.Layout.1.MonitorOut.2.Tile.1.Profile=2
 Index.2.Layout.1.MonitorOut.2.Tile.1.Location=1x1
 Index.2.Layout.1.MonitorOut.2.Tile.1.MergeID=

```

SUNAPI 11


```
 Index.2.Layout.1.MonitorOut.2.Tile.1.Merge=
 Index.2.Layout.1.MonitorOut.2.Tile.1.ImageLocation=
 Index.2.Layout.1.MonitorOut.2.Tile.2.SourceType=Stream
 Index.2.Layout.1.MonitorOut.2.Tile.2.MonitorIn=1
 Index.2.Layout.1.MonitorOut.2.Tile.2.Channel=2
 Index.2.Layout.1.MonitorOut.2.Tile.2.Profile=2
 Index.2.Layout.1.MonitorOut.2.Tile.2.Location=1x2
 Index.2.Layout.1.MonitorOut.2.Tile.2.MergeID=
 Index.2.Layout.1.MonitorOut.2.Tile.2.Merge=
 Index.2.Layout.1.MonitorOut.2.Tile.2.ImageLocation=
 Index.2.Layout.1.MonitorOut.2.Tile.3.SourceType=Stream
 Index.2.Layout.1.MonitorOut.2.Tile.3.MonitorIn=1
 Index.2.Layout.1.MonitorOut.2.Tile.3.Channel=1
 Index.2.Layout.1.MonitorOut.2.Tile.3.Profile=2
 Index.2.Layout.1.MonitorOut.2.Tile.3.Location=2x1
 Index.2.Layout.1.MonitorOut.2.Tile.3.MergeID=
 Index.2.Layout.1.MonitorOut.2.Tile.3.Merge=
 Index.2.Layout.1.MonitorOut.2.Tile.3.ImageLocation=
 Index.2.Layout.1.MonitorOut.2.Tile.4.SourceType=Stream
 Index.2.Layout.1.MonitorOut.2.Tile.4.MonitorIn=1
 Index.2.Layout.1.MonitorOut.2.Tile.4.Channel=3
 Index.2.Layout.1.MonitorOut.2.Tile.4.Profile=2
 Index.2.Layout.1.MonitorOut.2.Tile.4.Location=2x2
 Index.2.Layout.1.MonitorOut.2.Tile.4.MergeID=
 Index.2.Layout.1.MonitorOut.2.Tile.4.Merge=
 Index.2.Layout.1.MonitorOut.2.Tile.4.ImageLocation=

```

JSON RESPONSE

```
 HTTP/1.0 200 OK
 Content-type: application/json
 <Body>

 {
 "Wall": [
 {
 "Index": 2,
 "Name": "Wall 02",
 "SplitMode": "1x1",
 "MonitorOut": [
 "2"

```

12 Display


```
 ],
 "Coordinates": [
 {
 "x": 13.434783,
 "y": 0
 },
 {
 "x": 11,
 "y": 11.0
 }
 ],
 "EnableSequence": false,
 "Layout": [
 {
 "Index": 1,
 "Name": "Layout 01",
 "IsCurrentLayout": true,
 "EnableSequence": true,
 "SequenceTime": 10,
 "MonitorOut": [
 {
 "Index": 2,
 "SplitMode": "2x2",
 "Tile": [
 {
 "Index": 1,
 "SourceType": "Stream",
 "MonitorIn": 1,
 "Channel": 0,
 "Profile": 2,
 "Location": "1x1",
 "MergeID": null,
 "Merge": "",
 "ImageLocation": ""
 },
 {
 "Index": 2,
 "SourceType": "Stream",
 "MonitorIn": 1,
 "Channel": 2,
 "Profile": 2,

```

SUNAPI 13


```
 "Location": "1x2",
 "MergeID": null,
 "Merge": "",
 "ImageLocation": ""
 },
 {
 "Index": 3,
 "SourceType": "Stream",
 "MonitorIn": 1,
 "Channel": 1,
 "Profile": 2,
 "Location": "2x1",
 "MergeID": null,
 "Merge": "",
 "ImageLocation": ""
 },
 {
 "Index": 4,
 "SourceType": "Stream",
 "MonitorIn": 1,
 "Channel": 3,
 "Profile": 2,
 "Location": "2x2",
 "MergeID": null,
 "Merge": "",
 "ImageLocation": ""
 }
 ]
 }
 ]
 }
 ]
 }
 ]
 }

#### **3.4.2. Adding wall (1 monitor, 1 layout) configuration information**
```

REQUEST

```
 http://<Device IP>/stw cgi/display.cgi?msubmenu=wall&action=add&Index.1.Name=Wall01&Index.1.SplitMo

```

14 Display


```
 de=1x1&Index.1.MonitorOut=1&Index.1.Coordinates=0,0,11,11&Index.1.EnableSequ
 ence=False&Index.1.Layout.1.Name=Layout01&Index.1.Layout.1.IsCurrentLayout=T
 rue&Index.1.Layout.1.EnableSequence=True&Index.1.Layout.1.SequenceTime=10&In
 dex.1.Layout.1.MonitorOut.1.SplitMode=1x1&Index.1.Layout.1.MonitorOut.1.Tile
 .1.SourceType=Stream&Index.1.Layout.1.MonitorOut.1.Tile.1.MonitorIn=1&Index.
 1.Layout.1.MonitorOut.1.Tile.1.Channel=0&Index.1.Layout.1.MonitorOut.1.Tile.
 1.Profile=2&Index.1.Layout.1.MonitorOut.1.Tile.1.Location=1x1&Index.1.Layout
 .1.MonitorOut.1.Tile.1.MergeID=1&Index.1.Layout.1.MonitorOut.1.Tile.1.Merge=
 False&Index.1.Layout.1.MonitorOut.1.Tile.1.ImageLocation=1x1

```

TEXT RESPONSE

```
 OK

```

JSON RESPONSE

```
 HTTP/1.0 200 OK
 Content-type: application/json
 <Body>

 {
 "Response": "Success"
 }

#### **3.4.3. Updating (1 monitor, 1 layout) configuration information**
```

REQUEST

```
 http:// <Device IP>/stw cgi/display.cgi?msubmenu=wall&action=update&Index.1.Name=Wall02

```

TEXT RESPONSE

```
 OK

```

JSON RESPONSE

```
 HTTP/1.0 200 OK
 Content-type: application/json
 <Body>

```

SUNAPI 15


```
 {
 "Response": "Success"
 }

#### **3.4.4. Updating (1 monitor, 1 layout) current layout index**
```

REQUEST

```
 http:// <Device IP>/stw cgi/display.cgi?msubmenu=wall&action=update&Index.1.MonitorOut.1.CurrentLayo
 utIndex=1

```

TEXT RESPONSE

```
 OK

```

JSON RESPONSE

```
 HTTP/1.0 200 OK
 Content-type: application/json
 <Body>

 {
 "Response": "Success"
 }

#### **3.4.5. Removing wall configuration information**
```

REQUEST

```
 http://<Device IP>/stw-cgi/display.cgi?msubmenu= wall &action=remove&index=2

```

TEXT RESPONSE

```
 OK

```

JSON RESPONSE

```
 HTTP/1.0 200 OK
 Content-type: application/json

```

16 Display


```
 <Body>

 {
 "Response": "Success"
 }

#### **3.4.6. Control wall mode register**

```

Control is supported only in VMS mode (Please refer to system.cgi deviceinfo submenu for
**NOTE**

mode selection).


REQUEST

```
 http://<device-ip>/stw cgi/display.cgi?msubmenu=wall&action=control&Mode=Register&IsStreamServerPas
 swordEncrypted=False&CommonUserID=admin&CommonPassword=000ppp[[[&MonitorOut.
 1.SplitMode=1x1&MonitorOut.1.Tile.1.SourceType=Stream&MonitorOut.1.Tile.1.Ac
 tionType=MediaOpen&MonitorOut.1.Tile.1.HighProfileRTSPURL=rtsp://192.168.71.
 144/profile1/media.smp&MonitorOut.1.Tile.1.LowProfileRTSPURL=rtsp://192.168.
 71.144/profile2/media.smp&MonitorOut.1.Tile.1.StreamServerUserID=admin&Monit
 orOut.1.Tile.1.StreamServerPassword=5tkatjd!&MonitorOut.1.Tile.1.CameraIP=19
 2.168.71.144&MonitorOut.1.Tile.1.CameraName=TestCamera&MonitorOut.1.Tile.1.C
 oordinates=0,0,1920,1080&MonitorOut.1.Tile.1.Merge=1x1

```

TEXT RESPONSE

```
 OK

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

SUNAPI 17


#### **3.4.7. Control wall mode show**

REQUEST

```
 http://192.168.71.48/stw cgi/display.cgi?msubmenu=wall&action=control&Mode=show

```

TEXT RESPONSE

```
 OK

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

18 Display


## **Chapter 4. Encoder video out layout**
### **4.1. Description**

The **videooutlayout** submenu configures layout modes for encoder models.


**NOTE** This chapter applies to 16 channel encoder only.


**Access level**

|Action|Camera|NVR|Encoder|
|---|---|---|---|
|view|-|-|Admin|
|set|-|-|Admin|


### **4.2. Syntax**

```
 http://<Device IP>/stw-cgi/display.cgi?msubmenu=
 videooutlayout &action=<value>[&<parameter>=<value>]

### **4.3. Parameters**

```






|Action|Parameters|Request/<br>Response|Type/<br>Value|Description|
|---|---|---|---|---|
|view|||||
|set|LayoutMode|REQ, RES|<enum><br>1x1, 2x2,<br>3x3, 4x4|Layout modes|

### **4.4. Examples**

#### **4.4.1. Getting the current layout mode**

REQUEST




```
 http://<Device IP>/stw-cgi/display.cgi?msubmenu= videooutlayout &action=view

```

TEXT RESPONSE

```
 LayoutMode=3x3

```

SUNAPI 19


JSON RESPONSE

```
 HTTP/1.0 200 OK
 Content-type: application/json
 <Body>

 {
 "LayoutMode": "3x3"
 }

#### **4.4.2. Setting the layout mode to 4x4**
```

REQUEST

```
 http://<Device IP>/stw-cgi/display.cgi?msubmenu=
 videolayoutmode &action=set&LayoutMode=4x4

```

TEXT RESPONSE

```
 OK

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

20 Display


## **Chapter 5. SpotOut**
### **5.1. Description**

The **spotout** submenu configures the layout of analog video output.


This chapter applies to NVR only.
**NOTE**

Attribute to check for **spotout** support: "attributes/System/Limit/MaxAnalogSpotCount"


**Access level**

|Action|Camera|NVR|Decoder|
|---|---|---|---|
|view|-|User|-|
|set|-|User|-|


### **5.2. Syntax**

```
 http://<Device IP>/stw-cgi/display.cgi?msubmenu=
 spotout &action=<value>[&<parameter>=<value>]

### **5.3. Parameters**

```










|Action|Parameters|Request/<br>Response|Type/<br>Value|Description|
|---|---|---|---|---|
|view|||||
|set|Enable|REQ, RES|<bool><br>True, False|Enables or disables analog monitor<br>spotout|
||LayoutMode|REQ, RES|<enum><br>1, 2, 4, 9, 16|Layout mode<br>Check whether spotout is supported<br>or not on<br>System/Limit/MaxAnalogSpotCount<br>under attributes.cgi|
||SequenceMode|REQ, RES|<bool><br>True, False|Enables or disables sequence mode|
||ChannelList|REQ, RES|<csv>|Monitoring channels|

### **5.4. Examples**

#### **5.4.1. Getting spotout configuration information**

SUNAPI 21


REQUEST

```
 http://<Device IP> /stw-cgi/display.cgi?msubmenu=spotout&action=view

```

JSON RESPONSE

```
 HTTP/1.0 200 OK
 Content-type: application/json
 <Body>

 {
 "Enable": true,
 "LayoutMode": 9,
 "SequenceMode": true,
 "ChannelList": ["0", "0", "0", "0", "0", "0", "0", "0", "0", "0", "0", "0",
 "0", "0", "0", "0", "0", "0"]
 }

#### **5.4.2. Setting spotout configuration information**
```

REQUEST

```
 http://<Device IP>/stw cgi/display.cgi?msubmenu=spotout&action=set&Enable=True&LayoutMode=16&Sequen
 ceMode=True&ChannelList=1,1,1,1,1,1,1,1,1,1,1

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

22 Display


