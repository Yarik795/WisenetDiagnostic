# AI


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

2. Metaattributesearch . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . 5

2.1. Description . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . 5

2.2. Syntax . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . 5

2.3. Parameters . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . 5

2.4. Examples . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . 9

2.4.1. Meta attribute search . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . 9

2.4.2. Viewing search result status. . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . 10

2.4.3. Viewing search result. . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . 11

3. OCR (Optical Character Recognition) search . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . 15

3.1. Description . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . 15

3.2. Syntax . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . 15

3.3. Parameters . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . 15

3.4. Examples . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . 17

3.4.1. OCR search . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . 17

3.4.2. Viewing search result status. . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . 18

3.4.3. Viewing search result. . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . 19

4. Object Detection from Image . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . 22

4.1. Description . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . 22

4.2. Syntax . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . 22

4.3. Parameters . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . 22

4.4. Examples . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . 23

4.4.1. Object detected from image. . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . 23

5. Image library management. . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . 25

5.1. Description . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . 25

5.2. Syntax . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . 25

5.3. Parameters . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . 25

5.4. Examples . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . 27

5.4.1. Viewing image library . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . 27

5.4.2. Adding a new group . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . 28

5.4.3. Adding a new image . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . 29

5.4.4. Updating an action. . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . 30

5.4.5. Removing an action . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . 30

5.4.6. Making a backup and restoring . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . 31

6. AI Timeline . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . 33


2 AI


6.1. Description . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . 33

6.2. Syntax . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . 33

6.3. Parameters . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . 33

6.4. Examples . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . 34

6.4.1. AI timeline search for a duration . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . 34

7. AI Engine. . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . 36

7.1. Description . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . 36

7.2. Syntax . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . 36

7.3. Parameters . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . 36

7.4. Examples . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . 37

7.4.1. Viewing AI engine stats . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . 37

7.4.2. Enabling AI engine . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . 38

8. Face Recognition Search . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . 40

8.1. Description . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . 40

8.2. Syntax . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . 40

8.3. Parameters . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . 40

8.4. Examples . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . 43

8.4.1. Starting search . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . 43

8.4.2. Viewing the search result . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . 44


SUNAPI 3


## **Chapter 1. Overview**
### **1.1. Description**

**ai.cgi** configures AI-related features in the device.


The following submenus are used for AI functionalities:


 - **metaattributesearch** : Used to search recordings with metadata attributes.


 - **ocrsearch** : Used to search recordings for OCR text.


 - **objectdetectfromimage** : Used to detect the requested object type from images.


 - **imagelibrary** : Used to manage images on the device that is used for recognition/training.


 - **facerecognitionsearch** : Search recording for the provided face image


 - **aiengine** : Used to configure AI engine on the device


 - **aitimeline** : Used to view AI timeline for the requested time duration


4 AI


## **Chapter 2. Metaattributesearch**
### **2.1. Description**

The **metaattributesearch** submenu is used to search recordings with metadata attributes.


**NOTE** This submenu is applicable to NVR only


**Access level**

|Action|NVR|
|---|---|
|view|User|
|control|User|


### **2.2. Syntax**

```
 http://<Device IP>/stw-cgi/ai.cgi?msubmenu=
 metaattributesearch &action=<value>[&<parameter>=<value>...]

### **2.3. Parameters**

```










|Action|Parameters|Request/<br>Response|Type/<br>Value|Description|
|---|---|---|---|---|
|view|Type|REQ|<enum><br>Results,<br>Status|If Type is passed as Status, search<br>status is informed.<br>If Type is passed as Result, search<br>result is provided.|
||SearchToken|REQ|<string>|Search session token|
||ResultFromIndex|REQ|<int>|Index from which search results are<br>fetched|
||ResultFromTime|REQ|<string>|Time from which search results are<br>fetched.<br>Time in UTC format.<br>YYYY-MM-DDTHH:MM::SSZ|
||ResultToTime|REQ|<string>|Time to which search results are<br>fetched.<br>Time in UTC format.<br>YYYY-MM-DDTHH:MM::SSZ|


SUNAPI 5


|Action|Parameters|Request/<br>Response|Type/<br>Value|Description|
|---|---|---|---|---|
||MaxResults|REQ|<int>|Maximum number of search results to<br>return|
||Status|RES|<enum><br>Completed,<br>NotComple<br>ted|Search status|
||TotalResultsFound|RES|<int>|Total results|
||TotalCount|RES|<int>|Total count of result|
||TimedOut|RES|<bool><br>True, False|Asynchronous search timeout.|
||ResultFromDate|RES|<string>|Start time of search result.<br>Time in UTC format.<br>YYYY-MM-DDTHH:MM::SSZ|
||ResultToDate|RES|<string>|End time of search result.<br>Time in UTC format.<br>YYYY-MM-DDTHH:MM::SSZ|
||SearchTokenExpiryTime|RES|<string>|Time when the search token expires<br>Time in UTC format<br>YYYY-MM-DDTHH:MM:SSZ|
||Result.#.DateTime|RES|<string>|Time in UTC format<br>YYYY-MM-DDTHH:MM:SSZ|
||Result.#.Channel|RES|<int>|Result channel ID|
||Result.#.Attributes|RES|<string>|Attribute text|
||Result.#.ImageURL|RES|<string>|Image URL|
||Result.#.Resolution|RES|<string>|Image resolution<br>format=width x height|
||Result.#.BkID|RES|<string>|Bookmark ID|
||Result.#.ObjectID|RES|<int>|Object ID|
||Result.#.BoundingBox|RES|<csv>|Bounding box information of the<br>object in the following format:<br>left, top, right, bottom|


6 AI


|Action|Parameters|Request/<br>Response|Type/<br>Value|Description|
|---|---|---|---|---|
|control|Mode|REQ|<enum><br>Start,<br>Cancel,<br>Renew,<br>Stop|Search mode|
||ClassType|REQ|<enum><br>Person,<br>Vehicle,<br>Face|Search type|
||ChannelIDList|REQ|<csv>|Search channel ID list|
||OverlappedID|REQ|<int>|Overlapped number|
||SearchAttributes.Person.<br>Gender|REQ|<csv><br>Any, Male,<br>Female|Gender type|
||SearchAttributes.Person.<br>Clothing.Tops.ColorStrin<br>g|REQ|<csv><br>Any, Black,<br>Gray,<br>White, Red,<br>Orange,<br>Yellow,<br>Green,<br>Blue, Purple|Color of top (clothing)|
||SearchAttributes.Person.<br>Clothing.Tops.Length|REQ|<csv><br>Any, Long,<br>Short|Length of top (clothing)|
||SearchAttributes.Person.<br>Clothing.Bottoms.ColorSt<br>ring|REQ|<csv><br>Any, Black,<br>Gray,<br>White, Red,<br>Orange,<br>Yellow,<br>Green,<br>Blue, Purple|Color of bottom (clothing)|
||SearchAttributes.Person.<br>Clothing.Bottoms.Length|REQ|<csv><br>Any, Long,<br>Short|Length of bottom (clothing)|
||SearchAttributes.Person.<br>Clothing.Hat|REQ|<csv><br>Any, Wear,<br>No|Wearing a hat or not|



SUNAPI 7


|Action|Parameters|Request/<br>Response|Type/<br>Value|Description|
|---|---|---|---|---|
||SearchAttributes.Person.<br>Belonging.Bag|REQ|<csv><br>Any, Wear,<br>No|Carrying a bag or not|
||SearchAttributes.Face.Ge<br>nder|REQ|<csv><br>Any, Male,<br>Female|Gender|
||SearchAttributes.Face.Ag<br>eType|REQ|<csv><br>Any, Young,<br>Adult,<br>Middle,<br>Senior|Age group|
||SearchAttributes.Face.Ha<br>t|REQ|<csv><br>Any, Wear,<br>No|Wearing a hat or not|
||SearchAttributes.Face.Op<br>ticals|REQ|<csv><br>Any, Wear,<br>No|Wearing glasses or not|
||SearchAttributes.Vehicle.<br>Type|REQ|<csv><br>Any, Car,<br>Bus, Truck,<br>Motorcycle,<br>Bicycle,<br>Train|Vehicle type|
||SearchAttributes.Vehicle.<br>ColorString|REQ|<csv><br>Any, Black,<br>Gray,<br>White, Red,<br>Orange,<br>Yellow,<br>Green,<br>Blue, Purple|Vehicle color|
||FromDate|REQ|<string>|Time in UTC format<br>YYYY-MM-DDTHH:MM:SSZ|
||ToDate|REQ|<string>|Time in UTC format<br>YYYY-MM-DDTHH:MM:SSZ|
||Async|REQ|<bool>+<br>True, False|Asynchronous search option|
||WaitTime|REQ|<int>|Timeout second.(Default:60 sec.)|


8 AI


|Action|Parameters|Request/<br>Response|Type/<br>Value|Description|
|---|---|---|---|---|
||SearchToken|RES|<string>|Search token given as response, which<br>can be used for view operation.|
||TotalCount|RES|<int>|Total count|
||ResultFromDate|RES|<string>|Result of ‘from’ date<br>Time in UTC format<br>YYYY-MM-DDTHH:MM:SSZ|
||ResultToDate|RES|<string>|Result of ‘to’ date<br>Time in UTC format<br>YYYY-MM-DDTHH:MM:SSZ|

### **2.4. Examples**

#### **2.4.1. Meta attribute search**

REQUEST

```
 http://<Device IP>/stw cgi/ai.cgi?msubmenu=metaattributesearch&action=control&Mode=Start&Async=True
 &ClassType=Person&ChannelIDList=0,1,2,3,63&OverlappedID=-1&FromDate=1970-01 01T01:02:03Z&ToDate=2021-01 26T01:02:03Z&SearchAttributes.Person.Gender=Male&SearchAttributes.Person.Clo
 thing.Tops.ColorString=Black,Red&SearchAttributes.Person.Clothing.Bottoms.Co
 lorString=Gray,White&SearchAttributes.Person.Belonging.Bag=Wear

```

TEXT RESPONSE

```
 HTTP/1.0 200 OK
 Content-type: text/plain
 <Body>

 SearchToken=35833

```

JSON RESPONSE

```
 HTTP/1.0 200 OK
 Content-type: application/json

```

SUNAPI 9


```
 <Body>

 {
 "SearchToken": "35833"
 }

#### **2.4.2. Viewing search result status**
```

REQUEST

```
 http://<Device IP>/stw cgi/ai.cgi?msubmenu=metaattributesearch&action=view&Type=Status&SearchToken=
 35833

```

TEXT RESPONSE

```
 HTTP/1.0 200 OK
 Content-type: text/plain
 <Body>

 SearchTokenExpiryTime=2019-06-16T00:28:29Z
 Status=Completed
 TotalResultsFound=0
 TotalCount=1547
 TimedOut=False
 ResultFromDate=2019-06-15T05:38:11Z
 ResultToDate=2019-06-16T00:26:49Z

```

JSON RESPONSE

```
 HTTP/1.0 200 OK
 Content-type: application/json
 <Body>

 {
 "SearchTokenExpiryTime": "2019-06-16T00:28:29Z",
 "Status": "Completed",
 "TotalResultsFound": 0,
 "TotalCount": 1547,

```

10 AI


```
 "TimedOut": "False",
 "ResultFromDate": "2019-06-15T05:38:11Z",
 "ResultToDate": "2019-06-16T00:26:49Z"
 }

#### **2.4.3. Viewing search result**
```

REQUEST

```
 http://<Device IP>/stw cgi/ai.cgi?msubmenu=metaattributesearch&action=view&Type=Results&ResultFromI
 ndex=1&MaxResults=100&SearchToken=35833

```

TEXT RESPONSE

```
 HTTP/1.0 200 OK
 Content-type: text/plain
 <Body>

 SearchTokenExpiryTime=2019-06-15T23:14:45Z
 Status=Completed
 TotalResultsFound=100
 TotalCount=1414
 TimedOut=False
 Result.0.DateTime=2019-06-15T23:13:32Z
 Result.0.Channel=2
 Result.0.Attributes.Person.Gender=Male
 Result.0.Attributes.Person.Clothing.Tops.ColorString=Black
 Result.0.Attributes.Person.Clothing.Bottoms.ColorString=Gray
 Result.0.Attributes.Person.Belonging.Bag=Wear
 Result.0.ImageURL=/stw cgi/ai.cgi?msubmenu=imageget&action=view&type=metaattributesearch&ID=0000000
 000000000_10_0_2_1560640412_298530
 Result.0.Resolution=208x336
 Result.0.Channel=2
 Result.0.ObjectID=298530
 Result.0.Coordinate_Del=1372,160,1579,497
 Result.0.BoundingBox=-0.285231,-0.851852,-0.17739,-0.539815
 Result.0.BkID=00000000000000000000000000000000
 ...
 Result.99.DateTime=2019-06-15T22:32:27Z

```

SUNAPI 11


```
 Result.99.Channel=2
 Result.99.Attributes.Person.Gender=Male
 Result.99.Attributes.Person.Clothing.Tops.ColorString=Red
 Result.99.Attributes.Person.Clothing.Bottoms.ColorString=Gray
 Result.99.Attributes.Person.Belonging.Bag=Wear
 Result.99.ImageURL=/stw cgi/ai.cgi?msubmenu=imageget&action=view&type=metaattributesearch&ID=0000000
 000000000_10_0_2_1560637947_286642
 Result.99.Resolution=160x256
 Result.99.Channel=2
 Result.99.ObjectID=286642
 Result.99.Coordinate_Del=1221,0,1382,262
 Result.99.BoundingBox=-0.363897,-1,-0.280021,-0.757407
 Result.99.BkID=00000000000000000000000000000000

```

JSON RESPONSE

```
 HTTP/1.0 200 OK
 Content-type: application/json
 <Body>

 {
 "SearchTokenExpiryTime": "2019-06-15T23:14:45Z",
 "Status": "Completed",
 "TotalResultsFound": 100,
 "TotalCount": 1414,
 "TimedOut": "False",
 "Results": [
 {
 "Result": 0,
 "DateTime": "2019-06-15T23:13:32Z",
 "Channel": 2,
 "Attributes": {
 "Person": {
 "Gender": ["Male"],
 "Clothing": {
 "Tops": {
 "ColorString": ["Black"]
 },
 "Bottoms": {
 "ColorString": ["Gray"]

```

12 AI


```
 }
 },
 "Belonging": {
 "Bag": ["Wear"]
 }
 }
 },
 "ImageURL": "/stw cgi/ai.cgi?msubmenu=imageget&action=view&type=metaattributesearch&ID=0000000
 000000000_10_0_2_1560640412_298530",
 "Resolution": "208x336",
 "ObjectID": 298530,
 "Coordinate_Del": "1372,160,1579,497",
 "BoundingBox": [
 {
 "left": -0.285231,
 "top": -0.851852,
 "right": -0.177390,
 "bottom": -0.539815
 }],
 "BkID": "00000000000000000000000000000000"
 },
 ...
 {
 "Result": 99,
 "DateTime": "2019-06-15T22:32:27Z",
 "Channel": 2,
 "Attributes": {
 "Person": {
 "Gender": ["Male"],
 "Clothing": {
 "Tops": {
 "ColorString": ["Red"]
 },
 "Bottoms": {
 "ColorString": ["Gray"]
 }
 },
 "Belonging": {
 "Bag": ["Wear"]
 }

```

SUNAPI 13


```
 }
 },
 "ImageURL": "/stw cgi/ai.cgi?msubmenu=imageget&action=view&type=metaattributesearch&ID=0000000
 000000000_10_0_2_1560637947_286642",
 "Resolution": "160x256",
 "ObjectID": 286642,
 "Coordinate_Del": "1221,0,1382,262",
 "BoundingBox": [
 {
 "left": -0.363897,
 "top": -1,
 "right": -0.280021,
 "bottom": -0.757407
 }
 ],
 "BkID": "00000000000000000000000000000000"
 }
 ]
 }

```

14 AI


## **Chapter 3. OCR (Optical Character Recognition)** **search**
### **3.1. Description**

The **ocrsearch** submenu is used to search a video that matches an input string.


**NOTE** This submenu is applicable to NVR only


**Access level**

|Action|NVR|
|---|---|
|view|User|
|control|User|


### **3.2. Syntax**

```
 http://<Device IP>/stw-cgi/ai.cgi?msubmenu=
 ocrsearch &action=<value>[&<parameter>=<value>...]

### **3.3. Parameters**

```










|Action|Parameters|Request/<br>Response|Type/<br>Value|Description|
|---|---|---|---|---|
|view|Type|REQ|<enum><br>Results,<br>Status|If Type is passed as Status, search<br>status is informed.<br>If Type is passed as Result, search<br>result is provided.|
||SearchToken|REQ|<string>|Search session token|
||ResultFromIndex|REQ|<int>|Index from which search results are<br>fetched|
||ResultFromTime|REQ|<string>|Time from which search results are<br>fetched.<br>Time in UTC format.<br>YYYY-MM-DDTHH:MM::SSZ|


SUNAPI 15


|Action|Parameters|Request/<br>Response|Type/<br>Value|Description|
|---|---|---|---|---|
||ResultToTime|REQ|<string>|Time to which search results are<br>fetched.<br>Time in UTC format.<br>YYYY-MM-DDTHH:MM::SSZ|
||MaxResults|REQ|<int>|Maximum number of search results to<br>return|
||Status|RES|<enum>|Search status|
||TotalResultsFound|RES|<int>|Total results|
||TotalCount|RES|<int>|Total result count|
||TimedOut|RES|<bool><br>True, False|Asynchronous search timeout.|
||ResultFromDate|RES|<string>|Start time of search result.<br>Time in UTC format.<br>YYYY-MM-DDTHH:MM::SSZ|
||ResultToDate|RES|<string>|End time of search result.<br>Time in UTC format.<br>YYYY-MM-DDTHH:MM::SSZ|
||SearchTokenExpiryTime|RES|<string>|Time when the search token expires<br>Time in UTC format<br>YYYY-MM-DDTHH:MM:SSZ|
||Result.#.DateTime|RES|<string>|Time in UTC format<br>YYYY-MM-DDTHH:MM:SSZ|
||Result.#.Channel|RES|<int>|Result channel ID|
||Result.#.Text|RES|<string>|Text found matching the search<br>keyword|
||Result.#.ImageURL|RES|<string>|Image URL|
||Result.#.Resolution|RES|<string>|Image resolution|
||Result.#.BkID|RES|<string>|Bookmark ID|


16 AI


|Action|Parameters|Request/<br>Response|Type/<br>Value|Description|
|---|---|---|---|---|
||Result.#.BoundingBox|RES|<csv>|Bounding box information of the<br>object in the following format:<br>left, top, right, bottom|
|control|Mode|REQ|<enum><br>Start,<br>Cancel,<br>Renew,<br>Stop|Used to start, cancel, or renew search|
||ChannelIDList|REQ|<csv>|On which channel search has to be<br>performed|
||OverlappedID|REQ|<int>|Recording overlapped id|
||SearchText|REQ|<string>|Text to search in the recording|
||FromDate|REQ|<string>|Time in UTC format<br>YYYY-MM-DDTHH:MM:SSZ|
||ToDate|REQ|<string>|Time in UTC format<br>YYYY-MM-DDTHH:MM:SSZ|
||Async|REQ|<bool>+<br>True, False|Asynchronous search option|
||WaitTime|REQ|<int>|Timeout second.(Default:60 sec.)|
||SearchToken|RES|<string>|Search token given as response, which<br>can be used for view operation.|
||TotalCount|RES|<int>|Total result count|
||ResultFromDate|RES|<string>|Time in UTC format<br>YYYY-MM-DDTHH:MM:SSZ|
||ResultToDate|RES|<string>|Time in UTC format<br>YYYY-MM-DDTHH:MM:SSZ|

### **3.4. Examples**

#### **3.4.1. OCR search**

REQUEST

```
 http://<Device IP>/stw cgi/ai.cgi?msubmenu=ocrsearch&action=control&Mode=Start&Async=True&ChannelID
 List=0,1,2,3,4&OverlappedID=-1&FromDate=1970-01-01T01-02-03&ToDate=2021-01
```

SUNAPI 17


```
 01T01-02-03&SearchText=*nu*

```

TEXT RESPONSE

```
 HTTP/1.0 200 OK
 Content-type: text/plain
 <Body>

 SearchToken=48928

```

JSON RESPONSE

```
 HTTP/1.0 200 OK
 Content-type: application/json
 <Body>

 {
 "SearchToken": "48928",
 }

#### **3.4.2. Viewing search result status**
```

REQUEST

```
 http://<Device IP>/stw cgi/ai.cgi?msubmenu=ocrsearch&action=view&Type=Status&SearchToken=48928

```

TEXT RESPONSE

```
 HTTP/1.0 200 OK
 Content-type: text/plain
 <Body>

 SearchTokenExpiryTime=
 Status=Completed
 TotalResultsFound=0
 TotalCount=68
 TimedOut=False
 ResultFromDate=2019-06-15T05:43:29Z

```

18 AI


```
 ResultToDate=2019-06-16T00:27:06Z

```

JSON RESPONSE

```
 HTTP/1.0 200 OK
 Content-type: application/json
 <Body>

 {
 "SearchTokenExpiryTime": "",
 "Status": "Completed",
 "TotalResultsFound": 0,
 "TotalCount": 68,
 "TimedOut": "False",
 "ResultFromDate": "2019-06-15T05:43:29Z",
 "ResultToDate": "2019-06-16T00:27:06Z"
 }

#### **3.4.3. Viewing search result**
```

REQUEST

```
 http://<Device IP>/stw cgi/ai.cgi?msubmenu=ocrsearch&action=view&Type=Results&ResultFromIndex=1&Max
 Results=5&SearchToken=48928

```

TEXT RESPONSE

```
 HTTP/1.0 200 OK
 Content-type: text/plain
 <Body>

 SearchTokenExpiryTime=2019-06-15T23:21:12Z
 Status=Completed
 TotalResultsFound=51
 TotalCount=55
 TimedOut=False
 Result.0.DateTime=2019-06-15 23:17:07
 Result.0.Channel=0
 Result.0.Text=ulnu8

```

SUNAPI 19


```
 Result.0.ImageURL=/stw cgi/ai.cgi?msubmenu=imageget&action=view&type=ocrsearch&ID=0000000000000000_
 10_4_0_1560640627_3078
 Result.0.Resolution=96x40
 Result.0.BoundingBox=-0.534375,-0.0296296,-0.429167,0.0518519
 Result.0.BkID=00000000000000000000000000000000
 ...
 Result.50.DateTime=2019-06-15 06:01:17
 Result.50.Channel=0
 Result.50.Text=ulnu8
 Result.50.ImageURL=/stw cgi/ai.cgi?msubmenu=imageget&action=view&type=ocrsearch&ID=0000000000000000_
 10_4_0_1560578477_194
 Result.50.Resolution=72x24
 Result.50.BoundingBox=-0.322917,0.172222,-0.246875,0.22963
 Result.50.BkID=00000000000000000000000000000000

```

JSON RESPONSE

```
 HTTP/1.0 200 OK
 Content-type: application/json
 <Body>

 {
 "SearchTokenExpiryTime": "2019-06-15T23:21:12Z",
 "Status": "Completed",
 "TotalResultsFound": 51,
 "TotalCount": 55,
 "TimedOut": "False",
 "Results": [
 {
 "Result": 0,
 "DateTime": "2019-06-15 23:17:07",
 "Channel": 0,
 "Text": "ulnu8",
 "ImageURL": "/stw cgi/ai.cgi?msubmenu=imageget&action=view&type=ocrsearch&ID=0000000000000000_
 10_4_0_1560640627_3078",
 "Resolution": "96x40",
 "BoundingBox": [
 {

```

20 AI


```
 "left": -0.534375,
 "top": -0.029630,
 "right": -0.429167,
 "bottom": 0.051852
 }
 ],
 "BkID": "00000000000000000000000000000000"
 },
 ...
 {
 "Result": 50,
 "DateTime": "2019-06-15 06:01:17",
 "Channel": 0,
 "Text": "ulnu8",
 "ImageURL": "/stw cgi/ai.cgi?msubmenu=imageget&action=view&type=ocrsearch&ID=0000000000000000_
 10_4_0_1560578477_194",
 "Resolution": "72x24",
 "BoundingBox": [
 {
 "left": -0.322917,
 "top": 0.172222,
 "right": -0.246875,
 "bottom": 0.229630
 }
 ],
 "BkID": "00000000000000000000000000000000"
 }
 ]
 }

```

SUNAPI 21


## **Chapter 4. Object Detection from Image**
### **4.1. Description**

The **objectdetectfromimage** submenu is used to detect the requested object type from images.


**NOTE** This submenu is applicable to NVR only


**Access level**

|Action|NVR|
|---|---|
|control|User|


### **4.2. Syntax**

```
 http://<Device IP>/stw-cgi/ai.cgi?msubmenu=
 objectdetectfromimage &action=<value>[&<parameter>=<value>...]

### **4.3. Parameters**

```
















|Action|Parameters|Request/<br>Response|Type/<br>Value|Description|
|---|---|---|---|---|
|control|ObjectType|REQ|<enum><br>Face|Object type to be detected in the past<br>image|
||Result.#.TempGroupID|RES|<string>|Temporary group ID|
||Result.#.TempImageID|RES|<int>|Temporary image ID|
||Result.#.ImageURL|RES|<int>|Image URL of the detected image|
||Result.#.Resolution|RES|<string><br>widthxheig<br>ht|Resolution of the detected object<br>image|
||Result.#.Coordinates|RES|<string>|Coordinates of the detected object in<br>the original image|


22 AI


|Action|Parameters|Request/<br>Response|Type/<br>Value|Description|
|---|---|---|---|---|
||Response|RES|<enum><br>Success,<br>Fail (No<br>Face<br>Detected),<br>Fail (Too<br>Many Face<br>Detected),<br>Fail<br>(Unknown)|Response code|

### **4.4. Examples**

#### **4.4.1. Object detected from image**

REQUEST

```
 http://<Device IP>/stw
```



```
 cgi/ai.cgi?msubmenu=objectdetectfromimage&action=control&ObjectType=Face

 Image sent as POST Content

 Base64(image)

```

JSON RESPONSE

```
 HTTP/1.0 200 OK
 Content-type: application/json
 <Body>

 {
 "Response": "Success",
 "Results": [
 {
 "Result": 0,
 "TempGroupID": 1000,
 "TempImageID": 168,
 "ImageURL": "/stw
```

SUNAPI 23


```
 cgi/ai.cgi?msubmenu=imageget&action=view&type=objectdetetfromimage&ID=168",
 "Resolution": "64x72",
 "Coordinates": [
 {
 "x": 538,
 "y": 349
 },
 {
 "x": 602,
 "y": 349
 },
 {
 "x": 602,
 "y": 421
 },
 {
 "x": 538,
 "y": 421
 }
 ]
 }
 ]
 }

```

24 AI


## **Chapter 5. Image library management**
### **5.1. Description**

The **imagelibrary** submenu is used to manage a collection of images in a device.


**NOTE** This submenu is applicable to NVR only


**Access level**

|Action|NVR|
|---|---|
|view|User|
|add|User|
|update|User|
|remove|User|
|control|User|


### **5.2. Syntax**

```
 http://<Device IP>/stw-cgi/ai.cgi?msubmenu=
 imagelibrary &action=<value>[&<parameter>=<value>...]

### **5.3. Parameters**

```




















|Action|Parameters|Request/<br>Response|Type/<br>Value|Description|
|---|---|---|---|---|
|view|GroupID|REQ,RES|<int>|Group ID|
||GroupID.#.Type|RES|<enum><br>Face|Group type|
||GroupID.#.GroupName|RES|<string>|Group name|
||GroupID.#.ImageID.#.Im<br>ageURL|RES|<string>|Image URL|
||GroupID.#.ImageID.#.Re<br>solution|RES|<string>|Resolution in format "widthxheight"|
||GroupID.#.ImageID.#.Na<br>me|RES|<string>|Name of image|
|add|GroupID|REQ|<int>|Group ID (if a group ID already exists,<br>a new image will be added to it)|


SUNAPI 25


|Action|Parameters|Request/<br>Response|Type/<br>Value|Description|
|---|---|---|---|---|
||Type|REQ|<enum><br>Face|Type of image|
||GroupName|REQ|<string>|Group name|
||Name|REQ|<string>|Image name|
||ImageRef|REQ|<string>|Image reference to add in the<br>following format:<br>{MetaType}_{Channel}_{UTC}_{ObjectI<br>D}<br>ex) 1_0_45545454_1234|
||TempGroupID|REQ|<int>|Temporary group ID from object<br>detection submenu|
||TempImageID|REQ|<int>|Temporary image ID from object<br>detection submenu|
||GroupID|RES|<int>|Response group ID|
||ImageID|RES|<int>|Response image ID|
||Response|RES|<enum><br>Success,<br>Fail (No<br>Face<br>Detected),<br>Fail (Too<br>Many Face<br>Detected),<br>Fail<br>(Unknown)|Response message|
|update|GroupID|REQ|<int>|Group ID which needs to be updated|
||Type|REQ|<enum><br>Face|Type of image|
||GroupName|REQ|<string>|New group name|
||ImageID|REQ|<int>|Image ID|
||Name|REQ|<string>|New name to be updated|
|remove|GroupID|REQ|<int>|Remove image from group ID|
||ImageIDList|REQ|<csv>|List of image IDs to be removed|
||ImageID|REQ|<int>|Image ID to be removed|


26 AI


|Action|Parameters|Request/<br>Response|Type/<br>Value|Description|
|---|---|---|---|---|
|control|Function|REQ|<enum><br>Backup,<br>Restore|Back up or restore images|
||GroupID|REQ|<int>|Group ID to back up or restore|
||GroupName|REQ|<string>|Group name to back up or restore|
||Password|REQ|<string>|Password for the backup file|
||IsPasswordEncrypted|REQ|<bool><br>True, False|When password is sent as encrypted<br>text|

### **5.4. Examples**

#### **5.4.1. Viewing image library**

REQUEST




```
 http://<Device IP>/stw-cgi/ai.cgi?msubmenu=imagelibrary&action=view

```

TEXT RESPONSE

```
 HTTP/1.0 200 OK
 Content-type: text/plain
 <Body>

 Group.0.GroupID=1001
 Group.0.GroupName=tete
 Group.0.Image.0.ImageID=127
 Group.0.Image.0.Name=hgg
 Group.0.Image.0.ImageURL=/stw cgi/ai.cgi?msubmenu=imageget&action=view&type=imagelibrary&ID=face_1001_127
 Group.0.Image.0.Resolution=24x24
 Group.1.GroupID=1002
 Group.1.GroupName=i

```

JSON RESPONSE

```
 HTTP/1.0 200 OK
 Content-type: application/json
 <Body>

```

SUNAPI 27


```
 {
 "Groups": [
 {
 "GroupID": 1001,
 "GroupName": "tete",
 "Images": [
 {
 "ImageID": 127,
 "Name": "hgg",
 "ImageURL": "/stw cgi/ai.cgi?msubmenu=imageget&action=view&type=imagelibrary&ID=face_1001_127"
,
 "Resolution": "24x24"
 }
 ]
 },
 {
 "GroupID": 1002,
 "GroupName": "i",
 "Images": []
 }
 ]
 }

#### **5.4.2. Adding a new group**
```

REQUEST

```
 http://<Device IP>/stw cgi/ai.cgi?msubmenu=imagelibrary&action=add&GroupName=sample

```

TEXT RESPONSE

```
 HTTP/1.0 200 OK
 Content-type: text/plain
 <Body>

 GroupID=1003
 ImageID=0

```

28 AI


JSON RESPONSE

```
 HTTP/1.0 200 OK
 Content-type: application/json
 <Body>

 {
 "GroupID": 1003,
 "ImageID": 0
 }

#### **5.4.3. Adding a new image**
```

REQUEST

```
 http://<Device IP>/stw cgi/ai.cgi?msubmenu=imagelibrary&action=add&GroupID=1003&TempImageID=180&Tem
 pGroupID=1000&Name=sampleImage

```

TEXT RESPONSE

```
 HTTP/1.0 200 OK
 Content-type: text/plain
 <Body>

 GroupID=1003
 ImageID=186

```

JSON RESPONSE

```
 HTTP/1.0 200 OK
 Content-type: application/json
 <Body>

 {
 "GroupID": 1003,
 "ImageID": 186
 }

```

SUNAPI 29


#### **5.4.4. Updating an action**

REQUEST

```
 http://<Device IP>/stw cgi/ai.cgi?msubmenu=imagelibrary&action=update&GroupID=1003&GroupName=sample
 2

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
 "Response": "Success"
 }

#### **5.4.5. Removing an action**
```

REQUEST

```
 http://<Device IP>/stw cgi/ai.cgi?msubmenu=imagelibrary&action=remove&GroupID=1003

```

TEXT RESPONSE

```
 HTTP/1.0 200 OK
 Content-type: text/plain
 <Body>

 OK

```

30 AI


JSON RESPONSE

```
 HTTP/1.0 200 OK
 Content-type: application/json
 <Body>

 {
 "Response": "Success"
 }

#### **5.4.6. Making a backup and restoring**
```

REQUEST

```
 http://<Device IP>/stw cgi/ai.cgi?msubmenu=imagelibrary&action=control&Function=Backup&GroupID=1004
 &IsPasswordEncrypted=True&Password=Shd/DVG1Y+vLVpTnSTbj8aOW3xd1e7eGSlM/lGjY/
 ju5JB67OTET+YvdNxzNog3ZtUS/ssxAPVm24O2vCQt4CJFz8MfpzfPf7ucQy3QIaivgvm4pwRM1b
 PksdUe4Ec3KpyhV+sJWvmWUP+3Hd0hsztOVEXI7Fd5CtZERilV0vtTRc5DZ6nuY1Vhe+KSDIzJc4
 TOSoWNEA9Sv3yUSmZjWprJ4EnlWuZzs3Fdi7l7Xpruq7StRG50myAsu9v6bpoUVaE/ZdM+V1JfDR
 xD0ooxVuQDhFY9N0ek0j/JaV1OJq8rb/A4dBhwr59JvdwKgJwoMmQRp/Rt0+4+hGz4fSihbPg==

```

TEXT/ JSON RESPONSE

```
 HTTP/1.0 200 OK
 Content-type: text/plain
 <Body>

 EncryptFileFormat

```

REQUEST

```
 http://<Device IP>/stw cgi/ai.cgi?msubmenu=imagelibrary&action=control&Function=Restore&IsPasswordE
 ncrypted=True&Password=P182w74Fk394fSftxjHvBR4V3zcMkqXzcRUW0zrLpOMkcoMSeDduS
 bt3NP1TkCUfOJbP/olPmu42ha84Azj52rJdF3P8jNPCFuHHsiQUAsk0S/5UlSwcuc2lCQkQmMwQz
 M4mLgHxS1+ZgUtBFy9FA/PKvgqvOeOm6hLywxT/nHT/Aj+ObeDcr5t17rB2n1dWlP5v1cipBbJaA
 mmLk1SFwZnhilHJ0gE8mDuX8VmQ4WouCuuvsKjRFYZESLhzYCrjoQFX+xZObxrwqrdLuWaoJiWH6
 JYr1+o75nsQoWJW7RpiJqbfgl0aJDvjvuOl8/YKtb0+J5m4sH5pdSzQk4e3+Q==&GroupName=te
 st

```

SUNAPI 31


```
 File sent in POST Content
 <Backup File>

```

JSON RESPONSE

```
 HTTP/1.0 200 OK
 Content-type: text/plain
 <Body>

 SamsungTechwin
 Content-type:application/json
 {
 "Status": "DownloadAck"
 }
 --SamsungTechwin
 Content-type:application/json
 {
 "Progress": 0
 }
 --SamsungTechwin
 Content-type:application/json
 {
 "Progress": 100
 }
 --SamsungTechwin
 Content-type:application/json
 {
 "Status": "DownloadOK"
 }
 HTTP/1.1 200 OK
 Content-type:application/json;charset=utf-8

```

32 AI


## **Chapter 6. AI Timeline**
### **6.1. Description**

The **aitimeline** submenu is used to view the AI details for the requested time duration.


**NOTE** This submenu is applicable to NVR only


**Access level**

|Action|NVR|
|---|---|
|view|User|


### **6.2. Syntax**

```
 http://<Device IP>/stw-cgi/ai.cgi?msubmenu=
 aitimeline &action=<value>[&<parameter>=<value>...]

### **6.3. Parameters**

```














|Action|Parameters|Request/<br>Response|Type/<br>Value|Description|
|---|---|---|---|---|
|view|ChannelIDList|REQ|<csv>|Requested channel list|
||ClassType|REQ|<enum><br>Person,<br>Vehicle,<br>Face,<br>FaceRecogn<br>ition,<br>LicensePlat<br>e|Class type to search|
||FromDate|REQ|<string>|‘From’ date in UTC format:<br>YYYY-MM-DDTHH:MM:SSZ|
||ToDate|REQ|<string>|‘To’ date in UTC format:<br>YYYY-MM-DDTHH:MM:SSZ|
||OverlappedID|REQ|<int>|Recording overlapped id|
||TotalCount|RES|<int>|Total result count|
||Result.#.Channel|RES|<int>|Result channel number|


SUNAPI 33


|Action|Parameters|Request/<br>Response|Type/<br>Value|Description|
|---|---|---|---|---|
||Result.#.Type|RES|<enum><br>Person,<br>Vehicle,<br>Face,<br>FaceRecogn<br>ition,<br>LicensePlat<br>e|Result classification type|
||Result.#.FromDate|RES|<string>|UTC format<br>YYYY-MM-DDTHH:MM:SSZ|
||Result.#.ToDate|RES|<string>|UTC format<br>YYYY-MM-DDTHH:MM:SSZ|
||Result.#.BkID|RES|<string>|Bookmark ID|

### **6.4. Examples**

#### **6.4.1. AI timeline search for a duration**

REQUEST

```
 http://<Device IP>/stw cgi/ai.cgi?&msubmenu=aitimeline&action=view&ClassType=Face&FromDate=1970-01 01T01:02:03Z&ToDate=2021-01-26T01:02:03Z&OverlappedID=-1

```

TEXT RESPONSE

```
 HTTP/1.0 200 OK
 Content-type: text/plain
 <Body>

 TotalCount=5000
 Result.0.Channel=12
 Result.0.Type=Face
 Result.0.FromDate=2020-06-12T15:24:43Z
 Result.0.ToDate=2020-06-12T15:24:43Z
 Result.0.BkID=00000000000000000000000000000000
 Result.1.Channel=12
 Result.1.Type=Face

```

34 AI


```
 Result.1.FromDate=2020-06-12T15:24:43Z
 Result.1.ToDate=2020-06-12T15:24:43Z
 Result.1.BkID=00000000000000000000000000000000
 ...

```

JSON RESPONSE

```
 HTTP/1.0 200 OK
 Content-type: application/json
 <Body>

 {
 "TotalCount": 5000,
 "Results": [
 {
 "Channel": 12,
 "Type": "Face",
 "FromDate": "2020-06-12T15:24:43Z",
 "ToDate": "2020-06-12T15:24:43Z",
 "BkID": "00000000000000000000000000000000"
 },
 {
 "Channel": 12,
 "Type": "Face",
 "FromDate": "2020-06-12T15:24:43Z",
 "ToDate": "2020-06-12T15:24:43Z",
 "BkID": "00000000000000000000000000000000"
 },
 ...
 ]
 }

```

SUNAPI 35


## **Chapter 7. AI Engine**
### **7.1. Description**

The **aiengine** submenu is used to manage and view AI engine stats.


**NOTE** This submenu is applicable to NVR only


**Access level**

|Action|NVR|
|---|---|
|view|User|
|set|User|


### **7.2. Syntax**

```
 http://<Device IP>/stw-cgi/ai.cgi?msubmenu=
 aiengine &action=<value>[&<parameter>=<value>...]

### **7.3. Parameters**

```

















|Action|Parameters|Request/<br>Response|Type/<br>Value|Description|
|---|---|---|---|---|
|view|ChannelIDList|REQ|<csv>|Requested channel list|
||TotalEngineUsage.Object<br>EngineUsage|RES|<int>|Total engine usage rate of object<br>detection|
||TotalEngineUsage.Recog<br>nitionEngineUsage|RES|<int>|Total engine usage rate of recognition|
||EngineStatus.Channel.#.<br>CamType|RES|<enum><br>Unknown,<br>MetaDataC<br>am,<br>AIMetaData<br>Cam,<br>NoneMetaC<br>am|Used to notify if the camera is<br>connected to the channel; determines<br>whether to send metadata or not.|
||EngineStatus.Channel.#.<br>ObjectEngine|RES|<bool><br>True, False|Enable or disable state of the object<br>engine|
||EngineStatus.Channel.#.<br>RecognitionEngine|RES|<bool><br>True, False|Enable or disable state of the<br>recognition engine|



36 AI


|Action|Parameters|Request/<br>Response|Type/<br>Value|Description|
|---|---|---|---|---|
||EngineStatus.Channel.#.<br>ObjectEngineUsage|RES|<int>|Each usage rate of object detection|
||EngineStatus.Channel.#.<br>RecognitionEngineUsage|RES|<int>|Each usage rate of recognition|
||FaceRecognitionAgreem<br>entTime|RES|<string>|Face recognition agreement time in<br>UTC format.<br>UTCFormat=YYYY-MM-<br>DDTHH:MM:SSZ|
|set|Channel.#.ObjectEngine|REQ|<bool><br>True, False|Enable or disable object detection<br>engine|
||Channel.#.RecognitionEn<br>gine|REQ|<bool><br>True, False|Enable or disable recognition engine|
||AgreementStatus.FaceRe<br>cognition|REQ|<bool><br>True, False|Agreement to run face recognition<br>algorithm.|

### **7.4. Examples**

#### **7.4.1. Viewing AI engine stats**

REQUEST






```
 http://<Device IP>/stw-cgi/ai.cgi?&msubmenu=aiengine&action=view

```

TEXT RESPONSE

```
 HTTP/1.0 200 OK
 Content-type: text/plain
 <Body>

 TotalEngineUsage.ObjectEngineUsage=46.875
 TotalEngineUsage.RecognitionEngineUsage=6.25
 EngineStatus.Channel.0.CamType=Unknown
 EngineStatus.Channel.0.ObjectEngine=False
 EngineStatus.Channel.0.RecognitionEngine=False
 EngineStatus.Channel.0.ObjectEngineUsage=0
 EngineStatus.Channel.0.RecognitionEngineUsage=0
 EngineStatus.Channel.1.CamType=Unknown
 EngineStatus.Channel.1.ObjectEngine=False

```

SUNAPI 37


```
 EngineStatus.Channel.1.RecognitionEngine=False
 EngineStatus.Channel.1.ObjectEngineUsage=0
 EngineStatus.Channel.1.RecognitionEngineUsage=0
 ...

```

JSON RESPONSE

```
 HTTP/1.0 200 OK
 Content-type: application/json
 <Body>

 {
 "TotalEngineUsage": {
 "ObjectEngineUsage": 46.875000,
 "RecognitionEngineUsage": 6.250000
 },
 "EngineStatus": [
 {
 "Channel": 0,
 "CamType": "Unknown",
 "ObjectEngine": false,
 "RecognitionEngine": false,
 "ObjectEngineUsage": 0,
 "RecognitionEngineUsage": 0
 },
 {
 "Channel": 1,
 "CamType": "Unknown",
 "ObjectEngine": false,
 "RecognitionEngine": false,
 "ObjectEngineUsage": 0,
 "RecognitionEngineUsage": 0
 },
 ...
 ]
 }

#### **7.4.2. Enabling AI engine**

```

38 AI


REQUEST

```
 http://<Device IP>/stw cgi/ai.cgi?&msubmenu=aiengine&action=set&Channel.0.ObjectEngine=True&Channel
 .0.RecognitionEngine=True

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
 "Response": "Success"
 }

```

SUNAPI 39


## **Chapter 8. Face Recognition Search**
### **8.1. Description**

The **facerecognitionsearch** submenu is used to search face recognition information from the recordings

on channels with face recognition enabled.


**NOTE** This submenu is applicable to NVR only


**Access level**

|Action|NVR|
|---|---|
|view|User|
|control|User|
|remove|User|


### **8.2. Syntax**

```
 http://<Device IP>/stw-cgi/ai.cgi?msubmenu=
 facerecognitionsearch &action=<value>[&<parameter>=<value>...]

### **8.3. Parameters**

```










|Action|Parameters|Request/<br>Response|Type/<br>Value|Description|
|---|---|---|---|---|
|view|Type|REQ|<enum><br>SearchImag<br>es, Results,<br>Status|Changes according to the type<br>information provided|
||SearchToken|REQ|<string>|Search token received in control<br>operation|
||ResultFromIndex|REQ|<int>|From which result index the results<br>need to be displayed.|
||ResultFromTime|REQ|<string>|Time from which search results are<br>fetched.<br>Time in UTC format.<br>YYYY-MM-DDTHH:MM::SSZ|


40 AI


|Action|Parameters|Request/<br>Response|Type/<br>Value|Description|
|---|---|---|---|---|
||ResultToTime|REQ|<string>|Time to which search results are<br>fetched.<br>Time in UTC format.<br>YYYY-MM-DDTHH:MM::SSZ|
||MaxResults|REQ|<int>|Maximum results needed in view|
||Status|RES|<enum><br>Completed,<br>NotComple<br>ted|When Type is set to Status, search<br>status is provided|
||TotalResultsFound|RES|<int>|Total results|
||TotalCount|RES|<int>|Total count|
||TimedOut|RES|<bool><br>True, False|Asynchronous search timeout.|
||ResultFromDate|RES|<string>|Start time of search result.<br>Time in UTC format.<br>YYYY-MM-DDTHH:MM::SSZ|
||ResultToDate|RES|<string>|End time of search result.<br>Time in UTC format.<br>YYYY-MM-DDTHH:MM::SSZ|
||SearchTokenExpiryTime|RES|<string>|Search token expiry date in UTC<br>format<br>YYYY-MM-DDTHH:MM:SSZ|
||Result.#.DateTime|RES|<string>|Date time in UTC format<br>YYYY-MM-DDTHH:MM:SSZ|
||Result.#.Channel|RES|<int>|Result channel id|
||Result.#.ObjectID|RES|<int>|Object id|
||Result.#.ImageURL|RES|<string>|Image URL can be used to download<br>image|
||Result.#.Resolution|RES|<string><br>widthxheig<br>ht|Result image resolution|
||Result.#.BkID|RES|<string>|Bookmark ID|


SUNAPI 41


|Action|Parameters|Request/<br>Response|Type/<br>Value|Description|
|---|---|---|---|---|
||Result.#.BoundingBox|RES|<csv>|Bounding box information in the<br>following format:<br>left, top, right, bottom|
||Result.#.SearchImage.#.<br>Type|RES|<enum><br>Library, File|When Type is set to SearchImages|
||Result.#.SearchImage.#.<br>GroupName|RES|<int>|Group name|
||Result.#.SearchImage.#.I<br>mageName|RES|<int>|Image name|
||Result.#.SearchImage.#.I<br>mageURL|RES|<string>|Image URL|
||Result.#.SearchImage.#.<br>Similarity|RES|<int>|Similarity score 1-100|
|control|Mode|REQ|<enum><br>Start,<br>Cancel,<br>Renew,<br>Stop|Search mode|
||ChannelIDList|REQ|<csv>|Channels on which search is<br>performed|
||OverlappedID|REQ|<int>|Recording overlapped id|
||FromDate|REQ|<string>|Time in UTC format "YYYY-MM-<br>DDTHH:MM:SSZ"|
||ToDate|REQ|<string>|Time in UTC format "YYYY-MM-<br>DDTHH:MM:SSZ"|
||Async|REQ|<bool>+<br>True, False|Asynchronous search option|
||WaitTime|REQ|<int>|Timeout second.(Default:60 sec.)|
||SearchImage.#.Type|REQ|<enum><br>Library|Search image type|
||SearchImage.#.GroupID|REQ|<int>|Group ID from image library|
||SearchImage.#.ImageID|REQ|<int>|Image ID from image library|
||Similarity|REQ|<int>|Similarity threshold for filtering results<br>above this value|
||SearchToken|RES|<string>|Seach token for the requested search<br>query|


42 AI


|Action|Parameters|Request/<br>Response|Type/<br>Value|Description|
|---|---|---|---|---|
||TotalCount|RES|<int>|Total result count|
||ResultFromDate|RES|<string>|Result of ‘from’ date in UTC format<br>YYYY-MM-DDTHH:MM:SSZ|
||ResultToDate|RES|<string>|Result of ‘to’ date in UTC format<br>YYYY-MM-DDTHH:MM:SSZ|
|remove|SearchImage|REQ|<int>|Search image index|
||SearchToken|REQ|<string>|Search token|

### **8.4. Examples**

#### **8.4.1. Starting search**

REQUEST

```
 http://<Device IP>/stw cgi/ai.cgi?msubmenu=facerecognitionsearch&action=control&Mode=Start&Async=Tr
 ue&ChannelIDList=0,1,2,3,4,5,6,7,8&OverlappedID=-1&FromDate=2000-03 01T10:59:23Z&ToDate=2021-03 11T11:59:23Z&SearchImage.0.Type=Library&SearchImage.0.GroupID=1001&SearchIma
 ge.0.ImageID=3

```

TEXT RESPONSE

```
 HTTP/1.0 200 OK
 Content-type: text/plain
 <Body>

 SearchToken=97923

```

JSON RESPONSE

```
 HTTP/1.0 200 OK
 Content-type: application/json
 <Body>

 {

```

SUNAPI 43


```
 "SearchToken": "97923"
 }

#### **8.4.2. Viewing the search result**
```

REQUEST

```
 http://<Device IP>/stw cgi/ai.cgi?msubmenu=facerecognitionsearch&action=view&Type=Status&SearchToke
 n=97923

```

TEXT RESPONSE

```
 HTTP/1.0 200 OK
 Content-type: text/plain
 <Body>

 Status=Completed
 TotalResultsFound=0
 TotalCount=48
 TimedOut=False
 SearchTokenExpiryTime=2020-06-15T19:30:13Z
 ResultFromDate=2020-06-12T11:34:41Z
 ResultToDate=2020-06-12T15:24:43Z

```

JSON RESPONSE

```
 HTTP/1.0 200 OK
 Content-type: application/json
 <Body>

 {
 "Status": "Completed",
 "TotalResultsFound": 0,
 "TotalCount": 48,
 "TimedOut": "False",
 "SearchTokenExpiryTime": "2020-06-15T19:26:12Z"
 "ResultFromDate": "2020-06-12T11:34:41Z"
 "ResultToDate": "2020-06-12T15:24:43Z"

```

44 AI


```
 }

```

REQUEST

```
 http://<Device IP>/stw cgi/ai.cgi?msubmenu=facerecognitionsearch&action=view&Type=Results&ResultFro
 mIndex=1&MaxResults=100&SearchToken=97923

```

TEXT RESPONSE

```
 HTTP/1.0 200 OK
 Content-type: text/plain
 <Body>

 Status=Completed
 TotalResultsFound=48
 TotalCount=48
 TimedOut=False
 SearchTokenExpiryTime=2020-06-16T08:13:57Z
 Result.0.DateTime=2020-06-12T15:24:43Z
 Result.0.Channel=2
 Result.0.ObjectID=3745
 Result.0.ImageURL=/stw cgi/ai.cgi?msubmenu=imageget&action=view&type=frsearch&ID=000918E1A14D0000_1
 0_1_2_1591975483_3745
 Result.0.Resolution=288x392
 Result.0.BoundingBox=-1,-0.261111,-0.848398,0.103704
 Result.0.BkID=00000000000000000000000000000000
 Result.0.SearchImage.0.Type=Library
 Result.0.SearchImage.0.GroupName=sample2
 Result.0.SearchImage.0.ImageName=sampleImage
 Result.0.SearchImage.0.ImageURL=/stw cgi/ai.cgi?msubmenu=imageget&action=view&type=imagelibrary&ID=face_1003_186
 Result.0.SearchImage.0.Similarity=54
 ...
 Result.47.DateTime=2020-06-12T11:34:41Z
 Result.47.Channel=3
 Result.47.ObjectID=63
 Result.47.ImageURL=/stw cgi/ai.cgi?msubmenu=imageget&action=view&type=frsearch&ID=000918E1A14D0000_1
 0_1_3_1591961681_63

```

SUNAPI 45


```
 .Result.47.Resolution=80x72
 Result.47.BoundingBox=-0.952083,-0.131481,-0.861458,0.0111111
 Result.47.BkID=00000000000000000000000000000000
 Result.47.SearchImage.0.Type=Library
 Result.47.SearchImage.0.GroupName=sample2
 Result.47.SearchImage.0.ImageName=sampleImage
 Result.47.SearchImage.0.ImageURL=/stw cgi/ai.cgi?msubmenu=imageget&action=view&type=imagelibrary&ID=face_1003_186
 Result.47.SearchImage.0.Similarity=54

```

JSON RESPONSE

```
 HTTP/1.0 200 OK
 Content-type: application/json
 <Body>

 {
 "Status": "Completed",
 "TotalResultsFound": 48,
 "TotalCount": 48,
 "TimedOut": "False",
 "SearchTokenExpiryTime": "2020-06-16T08:14:07Z",
 "Results": [
 {
 "DateTime": "2020-06-12T15:24:43Z",
 "Channel": 2,
 "ObjectID": 3745,
 "ImageURL": "/stw cgi/ai.cgi?msubmenu=imageget&action=view&type=frsearch&ID=000918E1A14D0000_1
 0_1_2_1591975483_3745",
 "Resolution": "288x392",
 "BoundingBox": [
 {
 "left": -1,
 "top": -0.261111,
 "right": -0.848398,
 "bottom": 0.103704
 }
 ],
 "BkID": "00000000000000000000000000000000",
 "SearchImages": [

```

46 AI


```
 {
 "Type": "Library",
 "GroupName": "sample2",
 "ImageName": "sampleImage",
 "ImageURL": "/stw cgi/ai.cgi?msubmenu=imageget&action=view&type=imagelibrary&ID=face_1003_186"
,
 "Similarity": 54
 }
 ]
 },
 ...
 {
 "DateTime": "2020-06-12T11:34:41Z",
 "Channel": 3,
 "ObjectID": 63,
 "ImageURL": "/stw cgi/ai.cgi?msubmenu=imageget&action=view&type=frsearch&ID=000918E1A14D0000_1
 0_1_3_1591961681_63",
 "Resolution": "80x72",
 "BoundingBox": [
 {
 "left": -0.952083,
 "top": -0.131481,
 "right": -0.861458,
 "bottom": 0.011111
 }
 ],
 "BkID": "00000000000000000000000000000000",
 "SearchImages": [
 {
 "Type": "Library",
 "GroupName": "sample2",
 "ImageName": "sampleImage",
 "ImageURL": "/stw cgi/ai.cgi?msubmenu=imageget&action=view&type=imagelibrary&ID=face_1003_186"
,
 "Similarity": 54
 }
 ]
 }

```

SUNAPI 47


```
 ]
 }

```

48 AI


