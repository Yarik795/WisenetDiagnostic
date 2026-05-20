# Recording


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

1. Overview . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . 7

1.1. Description . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . 7

2. Storage . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . 8

2.1. Description . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . 8

2.2. Syntax . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . 8

2.3. Parameters . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . 8

2.4. Examples . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . 8

2.4.1. Getting the current information . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . 9

2.4.2. Enabling video storage . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . 11

2.4.3. Enabling overwriting . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . 11

3. General . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . 12

3.1. Description . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . 12

3.2. Syntax . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . 12

3.3. Parameters . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . 12

3.4. Examples . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . 14

3.4.1. Getting the current information . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . 14

3.4.2. Setting the normal record mode to Full . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . 19

3.4.3. Setting the event record mode to I-Frame. . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . 19

3.4.4. Setting the duration of pre-event recording to 3 seconds . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . 19

3.4.5. Setting the recording video file format to AVI . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . 19

3.4.6. Setting the source profile . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . 19

4. Recording Schedule . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . 20

4.1. Description . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . 20

4.2. Syntax . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . 20

4.3. Parameters . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . 20

4.4. Examples . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . 24

4.4.1. Getting the current information . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . 24

4.4.2. Setting the device to always record. . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . 28

4.4.3. Setting the recording schedule . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . 28

5. Overlapped Recording . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . 30

5.1. Description . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . 30

5.2. Syntax . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . 30

5.3. Parameters . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . 30

5.4. Examples . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . 31

5.4.1. Getting the overlapped recording between 12:00 AM and 12:00 PM on Aug. 1, 2014 . . . . . . . . . 31

6. Manual Recording . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . 33


2 Recording


6.1. Description . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . 33

6.2. Syntax . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . 33

6.3. Parameters . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . 33

6.4. Examples . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . 33

6.4.1. Getting the current manual recording status . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . 33

6.4.2. Starting the manual recording. . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . 34

6.4.3. Stopping the manual recording . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . 34

7. Calendar Search . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . 35

7.1. Description . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . 35

7.2. Syntax . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . 35

7.3. Parameters . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . 35

7.4. Examples . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . 36

7.4.1. Searching for recordings from February 2013. . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . 36

8. Timeline . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . 38

8.1. Description . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . 38

8.2. Syntax . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . 38

8.3. Parameters . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . 38

8.4. Examples . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . 41

8.4.1. Getting the timeline . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . 41

9. Recording Period. . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . 45

9.1. Description . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . 45

9.2. Syntax . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . 45

9.3. Parameters . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . 45

9.4. Examples . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . 45

9.4.1. Searching the recording period . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . 45

10. Heat Map Search . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . 47

10.1. Description . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . 47

10.2. Syntax . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . 47

10.3. Parameters . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . 47

10.4. Examples . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . 51

10.4.1. Heat map search color . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . 51

10.4.2. Heat map search . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . 52

10.4.3. Getting the status of searching . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . 54

10.4.4. Getting the result . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . 55

10.4.5. Cancelling the search . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . 56

11. People Count Search . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . 57

11.1. Description . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . 57

11.2. Syntax . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . 57

11.3. Parameters . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . 57

11.4. Examples . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . 59


SUNAPI 3


11.4.1. People Count Search . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . 59

11.4.2. Getting the status of searching . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . 60

11.4.3. Getting the result . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . 61

11.4.4. Cancelling the search . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . 62

12. Vehicle Count Search . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . 63

12.1. Description . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . 63

12.2. Syntax . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . 63

12.3. Parameters . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . 63

12.4. Examples . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . 65

12.4.1. Vehicle Count Search . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . 66

12.4.2. Getting the status of searching . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . 66

12.4.3. Getting the result . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . 67

12.4.4. Cancelling the search . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . 69

13. POS Configuration . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . 70

13.1. Description . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . 70

13.2. Syntax . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . 70

13.3. Parameters . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . 70

13.4. Examples . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . 72

14. POS Event Configuration . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . 76

14.1. Description . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . 76

14.2. Syntax . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . 76

14.3. Parameters . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . 76

14.4. Examples . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . 77

15. POS Data. . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . 78

15.1. Description . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . 78

15.2. Syntax . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . 78

15.3. Parameters . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . 78

15.4. Examples . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . 78

16. POS Calendar . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . 81

16.1. Description . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . 81

16.2. Syntax . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . 81

16.3. Parameters . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . 81

16.4. Examples . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . 81

17. Meta Data Search . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . 83

17.1. Description . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . 83

17.2. Syntax . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . 83

17.3. Parameters . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . 83

17.4. Examples . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . 86

17.4.1. Start search for POS data . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . 86

17.4.2. Cancel Search . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . 88


4 Recording


17.4.3. To get search status. . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . 89

17.4.4. To renew search token (For 1 minute) . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . 89

17.4.5. To get the results of search (First 100 results) . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . 90

17.4.6. To get the results of search (Next 100 results) . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . 93

18. Smart Search . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . 94

18.1. Description . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . 94

18.2. Syntax . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . 94

18.3. Parameters . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . 94

18.4. Examples . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . 96

18.4.1. Start smart search for selected area . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . 96

18.4.2. Check the status of smart search . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . 97

18.4.3. To get results of smart search . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . 97

18.4.4. Start Smart search for the lines . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . 99

19. Queue Search . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . 100

19.1. Description . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . 100

19.2. Syntax . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . 100

19.3. Parameters . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . 100

19.4. Examples. . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . 103

19.4.1. Queue Search . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . 103

19.4.2. Getting the status of Queue search . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . 105

19.4.3. Getting Queue search result . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . 105

19.4.4. Cancelling Queue search . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . 113

20. Disk Utility . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . 114

20.1. Description . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . 114

20.2. Syntax . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . 114

20.3. Parameters . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . 114

20.4. Examples. . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . 114

20.4.1. Getting the disk information . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . 114

21. Bookmark . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . 118

21.1. Description . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . 118

21.2. Syntax . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . 118

21.3. Parameters . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . 118

21.4. Examples. . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . 120

21.4.1. Adding a bookmark . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . 120

21.4.2. Removing a bookmark . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . 121

21.4.3. Updating a bookmark . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . 121

21.4.4. Viewing a bookmark . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . 122

22. Event Search . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . 124

22.1. Description . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . 124

22.2. Syntax . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . 124


SUNAPI 5


22.3. Parameters . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . 124

22.4. Examples. . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . 127

22.4.1. Event search . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . 127

22.4.2. Viewing search result status. . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . 127

22.4.3. Viewing search result . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . 128


6 Recording


## **Chapter 1. Overview**
### **1.1. Description**

This document explains recording.cgi.


**recording.cgi** configures video recording settings so that video can be recorded at a scheduled time or

when an event occurs. It also provides submenus for configuring storage and searching recorded videos.


The following submenus of recording.cgi are used:


 - **storage** : Sets the storage configuration, including whether to overwrite or auto-delete.


 - **general** : Sets the recording mode and the duration of pre/post-event recording.


 - **recordingschedule** : Sets the specific schedule for recording.


 - **overlapped** : Requests the recordings are overlapped within the given time range


 - **manualrecording** : Starts or stops the manual recording.


 - **calendarsearch** : Requests for recording information from a month.


 - **timeline** : Requests for recording information from a given time period.


 - **searchrecordingperiod** : Requests a given recording period.


 - **heatmapsearch** : Requests recording information using heat map search function and controls the

heat map search settings.


 - **peoplecountsearch** : Requests recording information using people count search function, and

controls the people count search settings.


 - **posconf** : Used for configuring POS device.


 - **posevntconf** : Used to configure POS event in the device.


 - **posdata** : Used to receive the live POS data from the device.


 - **poscalendar** : Used to get the availability of POS data in a given month.


 - **metadata** : Used to search POS data for some given search criteria.


 - **smartsearch** : Used to search video analytics information for given search criteria.


 - **queuesearch** : Requests statistical analysis and measurement of average dwell time and number of

people in queues based on given search criteria.


 - **diskutility** : Requests information on the NVR’s disk array and smart attributes of HDD.


 - **bookmark** : Used to manage bookmarks in NVR.


 - **eventsearch** : Used to search event data for some given search criteria.


 - **vehiclecountsearch** : Requests recording information using vehicle count search function, and

controls the vehicle count search settings.


SUNAPI 7


## **Chapter 2. Storage**
### **2.1. Description**

The **storage** submenu requests and configures storage settings.


**Access level**

|Action|Camera|NVR|
|---|---|---|
|view|Admin|User|
|set|Admin|User|


### **2.2. Syntax**

```
 http://<Device IP>/stw-cgi/recording.cgi?msubmenu=
 storage &action=<value>[&<parameter>=<value>]

### **2.3. Parameters**

```














|Action|Parameters|Request/<br>Response|Type/<br>Value|Description|
|---|---|---|---|---|
|view||||Reads the storage settings.|
|set|Channel|REQ,RES|<int>|Channel ID<br>**NVR ONLY**<br>|
||Enable|REQ, RES|<bool><br>True, False|Enables or disables video storage|
||OverWrite|REQ, RES|<bool><br>True, False|Enables or disables overwriting|
||DiskEndBeep|REQ, RES|<bool><br>True, False|Whether to beep when the disk ends<br>**NVR ONLY**<br>|
||AutoDeleteEnable|REQ, RES|<bool><br>True, False|Whether to delete videos older than<br>the specified number of days|
||AutoDeleteDays|REQ, RES|<int>|Days before auto deletion<br>This parameter is valid only when<br>**AutoDeleteEnable** is set to True.|

### **2.4. Examples**

8 Recording


#### **2.4.1. Getting the current information**

REQUEST

```
 http://<Device IP>/stw-cgi/recording.cgi?msubmenu=storage&action=view

```

TEXT RESPONSE

```
 HTTP/1.0 200 OK
 Content-type: text/plain
 <Body>

 Enable=True
 OverWrite=False
 AutoDeleteEnable=False
 AutoDeleteDays=180

```

JSON RESPONSE

```
 HTTP/1.0 200 OK
 Content-type: application/json
 <Body>

 {
 "Enable": true,
 "OverWrite": false,
 "AutoDeleteEnable": false,
 "AutoDeleteDays": 180
 }

```

The following request example is for NVR only.


REQUEST

```
 http://<Device IP>/stw-cgi/recording.cgi?msubmenu=storage&action=view

```

TEXT RESPONSE

```
 HTTP/1.0 200 OK
 Content-type: text/plain

```

SUNAPI 9


```
 <Body>

 Enable=True
 OverWrite=True
 DiskEndBeep=False
 AutoDeleteEnable=True
 Channel.0.AutoDeleteDays=400
 Channel.1.AutoDeleteDays=400
 Channel.2.AutoDeleteDays=400
 Channel.3.AutoDeleteDays=400
 Channel.4.AutoDeleteDays=400
 ...

```

JSON RESPONSE

```
 HTTP/1.0 200 OK
 Content-type: application/json
 <Body>

 {
 "Enable": true,
 "OverWrite": true,
 "DiskEndBeep": false,
 "AutoDeleteEnable": true,
 "ChannelwiseAutoDeleteDays": [
 {
 "Channel": 0,
 "AutoDeleteDays": 400
 },
 {
 "Channel": 1,
 "AutoDeleteDays": 400
 },
 {
 "Channel": 2,
 "AutoDeleteDays": 400
 },
 {
 "Channel": 3,
 "AutoDeleteDays": 400

```

10 Recording


```
 },
 {
 "Channel": 4,
 "AutoDeleteDays": 400
 }
 ]
 }

#### **2.4.2. Enabling video storage**
```

REQUEST

```
 http://<Device IP>/stw cgi/recording.cgi?msubmenu=storage&action=set&Enable=True

#### **2.4.3. Enabling overwriting**
```

REQUEST

```
 http://<Device IP>/stw cgi/recording.cgi?msubmenu=storage&action=set&OverWrite=True

```

SUNAPI 11


## **Chapter 3. General**
### **3.1. Description**

The **general** submenu requests and configures general recording settings.


**NOTE** Attribute to check for Recording Support: "attributes/Recording/Support/Recording"


**Access level**

|Action|Camera|NVR|
|---|---|---|
|view|Admin|User|
|set|Admin|User|


### **3.2. Syntax**

```
 http://<Device IP>/stw-cgi/recording.cgi?msubmenu=
 general &action=<value>[&<parameter>=<value>]

### **3.3. Parameters**

```













|Action|Parameters|Request/<br>Response|Type/<br>Value|Description|
|---|---|---|---|---|
|view||||Reads the general recording<br>settings.|
||Channel|REQ, RES|<csv>|Channel ID|
||FullFrameBandwidth|RES|<float>|Full frame bandwidth<br>**NVR ONLY**<br>|
||FullFrameRate|RES|<float>|Full frame rate<br>**NVR ONLY**<br>|
||KeyFrameBandWidth|RES|<float>|Key frame bandwidth<br>**NVR ONLY**<br>|
||KeyFrameRate|RES|<float>|Key frame rate<br>**NVR ONLY**<br>|
||Codec|RES|<enum><br>MJPEG, MPEG4, H264,<br>H265|Codec<br>**NVR ONLY**<br>|



12 Recording


|Action|Parameters|Request/<br>Response|Type/<br>Value|Description|
|---|---|---|---|---|
||RecordOverlap|RES|<csv><br>AudioDetection,<br>VideoAnalysis,<br>AlarmInput, Normal,<br>MotionDetection,<br>Manual,<br>DefocusDetection,<br>Tracking,<br>FogDetection,<br>AudioAnalysis,<br>EmergencyTrigger,<br>GSensorEvent,<br>MaskDetection|Record overlap<br>**NVR ONLY**<br>|
||Resolution|RES|<string>|Resolution<br>**NVR ONLY**<br>|
||FrameRate|RES|<int>|Frame rate<br>**NVR ONLY**<br>|
||CompressionLevel|RES|<int>|Compression level<br>**NVR ONLY**<br>|
||SubStreamCodec|RES|<enum><br>MJPEG, MPEG4, H264,<br>H265|Substream codec<br>**NVR ONLY**<br>|
||SubStreamResolution|RES|<string>|Substream resolution<br>**NVR ONLY**<br>|
||SubStreamFrameRate|RES|<int>|SubStream framerate<br>**NVR ONLY**<br>|
|set|Channel|REQ, RES|<int>|Channel ID|
||SourceProfile|REQ, RES|<string>|Source profile<br>**NVR ONLY**<br>|
||NormalMode|REQ, RES|<enum><br>I-Frame, Full, Off|Recording type for normal mode<br>(continuous recording)|
||EventMode|REQ, RES|<enum><br>I-Frame, Full, Off|Recording type for the occurrence<br>of an event|
||PreEventDuration|REQ, RES|<enum>|Duration of pre-event recording|
||PostEventDuration|REQ, RES|<enum>|Duration of post-event recording|


SUNAPI 13


|Action|Parameters|Request/<br>Response|Type/<br>Value|Description|
|---|---|---|---|---|
||RecordedVideoFileTyp<br>e|REQ, RES|<enum><br>STW, AVI|Recording file format<br>• STW: Hanwha Vision’s<br>proprietary file format played<br>with Web viewer and SD<br>memory player<br>• AVI: General AVI video file<br>format played with Web<br>viewer and Windows Media<br>Player.<br>**CAMERA ONLY**<br>|
||AudioEnable|REQ, RES|<bool><br>True, False|Enables or disables audio<br>**NVR ONLY**<br>|
||BitrateLimit|REQ, RES|<float>|Bitrate limit<br>**NVR ONLY**<br>|
||SubStreamEnable|REQ, RES|<bool><br>True, False|Enables or disables substream<br>recording on a channel.<br>**NVR ONLY**<br>|
||SubStreamSourceProf<br>ile|REQ, RES|<string>|Substream sourceprofile<br>**NVR ONLY**<br>|

### **3.4. Examples**




#### **3.4.1. Getting the current information**

REQUEST

```
 http://<Device IP>/stw-cgi/recording.cgi?msubmenu=general&action=view

```

TEXT RESPONSE

```
 HTTP/1.0 200 OK
 Content-type: text/plain
 <Body>

 Channel=0
 NormalMode=Off
 EventMode=Full

```

14 Recording


```
 PreEventDuration=3s
 PostEventDuration=5s
 RecordedVideoFileType=AVI

```

JSON RESPONSE

```
 HTTP/1.0 200 OK
 Content-type: application/json
 <Body>

 {
 "RecordSetup": [
 {
 "Channel": 0,
 "NormalMode": "Off",
 "EventMode": "Full",
 "PreEventDuration": "3s",
 "PostEventDuration": "5s",
 "RecordedVideoFileType": "AVI"
 }
 ]
 }

```

The following request example is for NVR only.


REQUEST

```
 http://<Device IP>/stw-cgi/recording.cgi?msubmenu=general&action=view

```

TEXT RESPONSE

```
 HTTP/1.0 200 OK
 Content-type: text/plain
 <Body>

 Channel.0.FullFrameBandWidth=3.965550
 Channel.0.FullFrameRate=23.500000
 Channel.0.KeyFrameBandWidth=0.850044
 Channel.0.KeyFrameRate=0.500000
 Channel.0.Codec=H264

```

SUNAPI 15


```
 Channel.0.RecordOverlap=Normal
 Channel.0.SourceProfile=H.264
 Channel.0.NormalMode=Full
 Channel.0.EventMode=Full
 Channel.0.PreEventDuration=5s
 Channel.0.PostEventDuration=30s
 Channel.0.Resolution=2560x1920
 Channel.0.FrameRate=30
 Channel.0.CompressionLevel=10
 Channel.0.AudioEnable=False
 Channel.0.BitrateLimit=2.300000
 Channel.0.SubStreamEnable=True
 Channel.0.SubStreamSourceProfile=Live4NVR
 Channel.0.SubStreamCodec=H264
 Channel.0.SubStreamResolution=800x600
 Channel.0.SubStreamFrameRate=30
 Channel.1.FullFrameBandWidth=1.157300
 Channel.1.FullFrameRate=19.960000
 Channel.1.KeyFrameBandWidth=0.359871
 Channel.1.KeyFrameRate=0.500000
 Channel.1.Codec=H264
 Channel.1.RecordOverlap=Normal
 Channel.1.SourceProfile=Rec4NVR1
 Channel.1.NormalMode=Full
 Channel.1.EventMode=Full
 Channel.1.PreEventDuration=5s
 Channel.1.PostEventDuration=30s
 Channel.1.Resolution=1920x1080
 Channel.1.FrameRate=20
 Channel.1.CompressionLevel=10
 Channel.1.AudioEnable=False
 Channel.1.BitrateLimit=2.300000
 Channel.1.SubStreamEnable=True
 Channel.1.SubStreamSourceProfile=Live4NVR1
 Channel.1.SubStreamCodec=H264
 Channel.1.SubStreamResolution=800x600
 Channel.1.SubStreamFrameRate=20
 Channel.2.FullFrameBandWidth=0.780083
 Channel.2.FullFrameRate=25.000000
 Channel.2.KeyFrameBandWidth=0.671478
 Channel.2.KeyFrameRate=1.910000

```

16 Recording


```
 Channel.2.Codec=H264
 Channel.2.RecordOverlap=Normal
 Channel.2.SourceProfile=H.264
 Channel.2.NormalMode=Full
 Channel.2.EventMode=Full
 Channel.2.PreEventDuration=5s
 Channel.2.PostEventDuration=30s
 Channel.2.Resolution=320x240
 Channel.2.FrameRate=25
 Channel.2.CompressionLevel=16
 Channel.2.AudioEnable=False
 Channel.2.BitrateLimit=2.300000
 Channel.2.SubStreamEnable=True
 Channel.2.SubStreamSourceProfile=VideoProfile5
 Channel.2.SubStreamCodec=H265
 Channel.2.SubStreamResolution=3840x2160
 Channel.2.SubStreamFrameRate=25
 ...

```

JSON RESPONSE

```
 HTTP/1.0 200 OK
 Content-type: application/json
 <Body>

 {
 "RecordSetup": [
 {
 "Channel": 0,
 "FullFrameBandWidth": 3.416850,
 "FullFrameRate": 17.530000,
 "KeyFrameBandWidth": 1.058580,
 "KeyFrameRate": 0.350000,
 "Codec": "H264",
 "RecordOverlap": [
 "Normal"
 ],
 "SourceProfile": "H.264",
 "NormalMode": "Full",
 "EventMode": "Full",
 "PreEventDuration": "5s",

```

SUNAPI 17


```
 "PostEventDuration": "30s",
 "Resolution": "2560x1920",
 "FrameRate": 30,
 "CompressionLevel": 10,
 "AudioEnable": false,
 "BitrateLimit": 2.300000,
 "SubStreamEnable": true,
 "SubStreamSourceProfile": "Live4NVR",
 "SubStreamCodec": "H264",
 "SubStreamResolution": "800x600",
 "SubStreamFrameRate": "30"
 },
 {
 "Channel": 1,
 "FullFrameBandWidth": 1.157300,
 "FullFrameRate": 19.960000,
 "KeyFrameBandWidth": 0.359871,
 "KeyFrameRate": 0.500000,
 "Codec": "H264",
 "RecordOverlap": [
 "Normal"
 ],
 "SourceProfile": "Rec4NVR1",
 "NormalMode": "Full",
 "EventMode": "Full",
 "PreEventDuration": "5s",
 "PostEventDuration": "30s",
 "Resolution": "1920x1080",
 "FrameRate": 20,
 "CompressionLevel": 10,
 "AudioEnable": false,
 "BitrateLimit": 2.300000,
 "SubStreamEnable": true,
 "SubStreamSourceProfile": "Live4NVR1",
 "SubStreamCodec": "H264",
 "SubStreamResolution": "800x600",
 "SubStreamFrameRate": "20"
 },
 ...
 ]
 }

```

18 Recording


#### **3.4.2. Setting the normal record mode to Full**

REQUEST

```
 http://<Device IP>/stw cgi/recording.cgi?msubmenu=general&action=set&NormalMode=Full

#### **3.4.3. Setting the event record mode to I-Frame**
```

REQUEST

```
 http://<Device IP>/stw cgi/recording.cgi?msubmenu=general&action=set&EventMode=I-Frame

```

The following request example is for NVR only.


REQUEST

```
 http://<Device IP>/stw cgi/recording.cgi?msubmenu=general&action=set&Channel=1&EventMode=I-Frame

#### **3.4.4. Setting the duration of pre-event recording to 3 seconds**
```

REQUEST

```
 http://<Device IP>/stw cgi/recording.cgi?msubmenu=general&action=set&PreEventDuration=3s

#### **3.4.5. Setting the recording video file format to AVI**
```

REQUEST

```
 http://<Device IP>/stw cgi/recording.cgi?msubmenu=general&action=set&RecordedVideoFileType=AVI

#### **3.4.6. Setting the source profile**
```

The following request example is for NVR only.


REQUEST

```
 http://<Device IP>/stw cgi/recording.cgi?msubmenu=general&action=set&Channel=7&SourceProfile=Profil
 e2

```

SUNAPI 19


## **Chapter 4. Recording Schedule**
### **4.1. Description**

The **recordingschedule** submenu requests and configures recording schedule settings.


This submenu is only for normal recording, not for event recording. To set the recording schedule for

events, please refer to the 'Event' document.


**Access level**

|Action|Camera|NVR|
|---|---|---|
|view|Admin|User|
|set|Admin|User|


### **4.2. Syntax**

```
 http://<Device IP>/stw-cgi/recording.cgi?msubmenu=
 recordingschedule &action=<value>[&<parameter>=<value>]

### **4.3. Parameters**

```













|Action|Parameters|Request/<br>Response|Type/<br>Value|Description|
|---|---|---|---|---|
|view||||Reads the recording schedule<br>settings.|
||Channel|REQ|<csv>|Channel ID|
|set|Channel|REQ, RES|<int>|Channel ID|
||Activate|REQ, RES|<enum><br>Always,<br>Scheduled|Recording type.<br>• Always: Always records the video<br>• Scheduled: Records only at a<br>specific time on a specific day of<br>the week<br>**Note**<br>**Activate** must be sent together<br>with the**set** action.<br>**CAMERA ONLY**<br>|



20 Recording


|Action|Parameters|Request/<br>Response|Type/<br>Value|Description|
|---|---|---|---|---|
||<ddd>|REQ, RES|(For<br>Cameras)<br><bool><br>0, 1<br>(For NVR)<br><enum><br>0, 1, E, B|Enables or disables recording for the<br>selected day of week.<br>• 0: Disabled<br>• 1: Enabled<br>• E: Events<br>• B: Both<br><ddd> stands for week of the day and<br>should be specified in the short form<br>such as SUN, MON, TUE, WED, THU,<br>FRI, and SAT in uppercase.<br>e.g.) ‘**SUN**=1’ indicates that recording<br>is activated every Sunday from 12:00<br>AM to 11:59 PM, unless the specific<br>time is set using the <dddh><br>parameter such like SUN1=1, SUN2=1,<br>etc.<br>This parameter is valid only when<br>**Activate** is set to Scheduled.|
||EveryDay|REQ, RES|(For<br>Cameras)<br>(For<br>Cameras)<br><bool><br>0, 1<br>(For NVR)<br><enum><br>0, 1, E, B|Enables or disables recording for<br>every day<br>• 0: Disabled<br>• 1: Enabled<br>• E: Events<br>• B: Both<br>‘**EveryDay**=1’, indicating that the<br>recording is activated every day, has<br>the same effect as setting the<br>**ScheduleType** parameter to Always.<br>**EveryDay** is valid only when**Activate**<br>is set to Scheduled.|



SUNAPI 21


|Action|Parameters|Request/<br>Response|Type/<br>Value|Description|
|---|---|---|---|---|
||<dddh>|REQ, RES|(For<br>Cameras)<br><bool><br>0, 1<br>(For NVR)<br><enum><br>0, 1, E, B|Enables or disables recording for the<br>selected hour and day.<br>• 0: Disabled<br>• 1: Enabled<br>• E: Events<br>• B: Both<br><dddh> stands for the week of day<br>and time in hour. e.g. SUN1 means<br>1:00 AM on Sunday. MON2 means 2:00<br>AM on Monday.<br>This parameter is available if<br><corresponding weekday> = 1. ‘<br>**SUN**=1’ is required for SUN0 … SUN23.<br>e.g.) ‘SUN=1&SUN18=1’ indicates that<br>recording is enabled from 6:00 PM to<br>6:59 PM on every Sunday<br>This parameter is valid only when<br>**Activate** is set to Scheduled.|
||EveryDay<h>|REQ, RES|(For<br>Cameras)<br><bool><br>0, 1<br>(For NVR)<br><enum><br>0, 1, E, B|Enables or disables recording for<br>every day and hour<br>• 0: Disabled<br>• 1: Enabled<br>• E: Events<br>• B: Both<br>This parameter is available if<br>**EveryDay** =1. ‘EveryDay=1’ is required<br>for EveryDay0 … EveryDay23.<br>e.g.) ‘EveryDay=1&EveryDay18=1’<br>indicates that recording is enabled<br>from 6:00 PM to 6:59 PM every day.<br>This parameter is valid only when<br>**Activate** is set to Scheduled.|



22 Recording


|Action|Parameters|Request/<br>Response|Type/<br>Value|Description|
|---|---|---|---|---|
||<dddh>.FromTo|REQ, RES|<string>|Start time for recording for the<br>specific time and day of week<br>This parameter should be specified in<br>the format of <mm-mm> and the first<br>'mm' must be smaller than or equal to<br>the second 'mm'.<br>This is available if <corresponding<br>weekday><hour>=1. ‘**SUN0**=1’ is<br>required for SUN0.FromTo.<br>e.g.)<br>‘SUN=1&SUN18=1&SUN18.FromTo=12<br>-20’ indicates that recording is<br>activated from 6:12 PM to 6:20 PM on<br>every Sunday.<br>This parameter is valid only<br>whenwhen**Activate** is set to<br>Scheduled.<br>**CAMERA ONLY**<br>|
||EveryDay<h>.FromTo|REQ, RES|<string>|Start time for recording every day<br>This parameter should be specified in<br>the format of <mm-mm> and the first<br>'mm' must be smaller than or equal to<br>the second 'mm'.<br>This parameter is available if<br>EveryDay<hour>=1. ‘EveryDay0=1’ is<br>required for EveryDay0.FromTo.<br>e.g.) ‘EveryDay=1&EveryDay18=1&<br>EveryDay18.FromTo=12-20’ indicates<br>the recording is activated 6:12 PM to<br>6:20 PM every day.<br>This parameter is valid only when<br>**Activate** is set to Scheduled.<br>**CAMERA ONLY**<br>|


SUNAPI 23


### **4.4. Examples**

#### **4.4.1. Getting the current information**

REQUEST

```
 http://<Device IP>/stw-cgi/recording.cgi?msubmenu=
 recordingschedule &action=view

```

When Activate is set to Always


TEXT RESPONSE

```
 HTTP/1.0 200 OK
 Content-type: text/plain
 <Body>

 Channel=0
 Activate=Always
 SUN:0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0
 MON:0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0
 TUE:0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0
 WED:0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0
 THU:0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0
 FRI:0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0
 SAT:0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0

```

JSON RESPONSE

```
 HTTP/1.0 200 OK
 Content-type: application/json
 <Body>

 {
 "RecordSchedule": [
 {
 "Channel": 0,
 "Activate": "Always",
 "Schedule": {
 "SUN": [
 "0", "0", "0", "0", "0", "0", "0", "0", "0", "0", "0",

```

24 Recording


```
 "0",
 "0", "0", "0", "0", "0", "0", "0", "0", "0", "0", "0",
 "0"
 ],
 "MON": [
 "0", "0", "0", "0", "0", "0", "0", "0", "0", "0", "0",
 "0",
 "0", "0", "0", "0", "0", "0", "0", "0", "0", "0", "0",
 "0"
 ],
 "TUE": [
 "0", "0", "0", "0", "0", "0", "0", "0", "0", "0", "0",
 "0",
 "0", "0", "0", "0", "0", "0", "0", "0", "0", "0", "0",
 "0"
 ],
 "WED": [
 "0", "0", "0", "0", "0", "0", "0", "0", "0", "0", "0",
 "0",
 "0", "0", "0", "0", "0", "0", "0", "0", "0", "0", "0",
 "0"
 ],
 "THU": [
 "0", "0", "0", "0", "0", "0", "0", "0", "0", "0", "0",
 "0",
 "0", "0", "0", "0", "0", "0", "0", "0", "0", "0", "0",
 "0"
 ],
 "FRI": [
 "0", "0", "0", "0", "0", "0", "0", "0", "0", "0", "0",
 "0",
 "0", "0", "0", "0", "0", "0", "0", "0", "0", "0", "0",
 "0"
 ],
 "SAT": [
 "0", "0", "0", "0", "0", "0", "0", "0", "0", "0", "0",
 "0",
 "0", "0", "0", "0", "0", "0", "0", "0", "0", "0", "0",
 "0"
 ]
 }

```

SUNAPI 25


```
 }
 ]
 }

```

When Activate is set to Scheduled


TEXT RESPONSE

```
 HTTP/1.0 200 OK
 Content-type: text/plain
 <Body>

 Channel=0
 Activate=Scheduled
 SUN:1 1 1 1 1 1 1 1 1 1 1 1 1 1 1 1 1 1 1 1 1 1 1 1
 MON:1 1 1 1 1 1 1 1 1 1 1 1 1 1 1 1 1 1 1 1 1 1 1 1
 TUE:0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0
 WED:0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0
 THU:0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0
 FRI:0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0
 SAT:1 1 1 1 1 1 1 1 1 1 1 1 1 1 1 1 1 1 1 1 1 1 1 1

```

JSON RESPONSE

```
 HTTP/1.0 200 OK
 Content-type: application/json
 <Body>

 {
 "RecordSchedule": [
 {
 "Channel": 0,
 "Activate": "Scheduled",
 "Schedule": {
 "SUN": [
 "1", "1", "1", "1", "1", "1", "1", "1", "1", "1", "1",
 "1",
 "1", "1", "1", "1", "1", "1", "1", "1", "1", "1", "1",
 "1"
 ],

```

26 Recording


```
 "MON": [
 "1", "1", "1", "1", "1", "1", "1", "1", "1", "1", "1",
 "1",
 "1", "1", "1", "1", "1", "1", "1", "1", "1", "1", "1",
 "1"
 ],
 "TUE": [
 "0", "0", "0", "0", "0", "0", "0", "0", "0", "0", "0",
 "0",
 "0", "0", "0", "0", "0", "0", "0", "0", "0", "0", "0",
 "0"
 ],
 "WED": [
 "0", "0", "0", "0", "0", "0", "0", "0", "0", "0", "0",
 "0",
 "0", "0", "0", "0", "0", "0", "0", "0", "0", "0", "0",
 "0"
 ],
 "THU": [
 "0", "0", "0", "0", "0", "0", "0", "0", "0", "0", "0",
 "0",
 "0", "0", "0", "0", "0", "0", "0", "0", "0", "0", "0",
 "0"
 ],
 "FRI": [
 "0", "0", "0", "0", "0", "0", "0", "0", "0", "0", "0",
 "0",
 "0", "0", "0", "0", "0", "0", "0", "0", "0", "0", "0",
 "0"
 ],
 "SAT": [
 "1", "1", "1", "1", "1", "1", "1", "1", "1", "1", "1",
 "1",
 "1", "1", "1", "1", "1", "1", "1", "1", "1", "1", "1",
 "1"
 ]
 }
 }
 ]
 }

```

SUNAPI 27


#### **4.4.2. Setting the device to always record**

REQUEST

```
 http://<Device IP>/stw cgi/recording.cgi?msubmenu=recordingschedule&action=set&Activate=Always

#### **4.4.3. Setting the recording schedule**
```

To set the schedule (day and time), the **Activate** parameter must be set to Scheduled.


**To record every Saturday and Sunday**


REQUEST

```
 http://<Device IP>/stw cgi/recording.cgi?msubmenu=recordingschedule&action=set&Activate=Scheduled&S
 AT=1&SUN=1

```

**To not record every Saturday and Sunday**


REQUEST

```
 http://<Device IP>/stw cgi/recording.cgi?msubmenu=recordingschedule&action=set&Activate=Scheduled&S
 AT=0&SUN=0

```

**To record at 1:00 AM every day and disable the recording at 4:00 AM every day**


REQUEST

```
 http://<Device IP>/stw cgi/recording.cgi?msubmenu=recordingschedule&action=set&Activate=Scheduled&E
 veryDay=1&EveryDay1=1&EveryDay4=0

```

**To record from 3:58 AM to 3:59 AM on Sunday**


REQUEST

```
 http://<Device IP>/stw cgi/recording.cgi?msubmenu=recordingschedule&action=set&Activate=Scheduled&S
 UN=1&SUN3=1&SUN3.FromTo=58-59

```

**To record every day from 3:58 AM to 3:59 AM**


28 Recording


REQUEST

```
 http://<Device IP>/stw cgi/recording.cgi?msubmenu=recordingschedule&action=set&Activate=Scheduled&E
 veryDay=1&EveryDay3=1&EveryDay3.FromTo=58-59

```

SUNAPI 29


## **Chapter 5. Overlapped Recording**
### **5.1. Description**

The **overlapped** submenu requests that recordings are overlapped within a given time range.


In a case where the system time settings change, or DST is applied while recording the video, the

recording is overlapped for a certain period of time. A single digit number is assigned to the ID of the

overlapped recording. When it returns ‘OverlappedIDList=0,1’ this means that there are two overlapped

recordings.


**NOTE** Attribute to check for Feature Support: "attributes/Recording/Support/Overlapped"


**Access level**

|Action|Camera|NVR|
|---|---|---|
|view|User|User|


### **5.2. Syntax**

```
 http://<Device IP>/stw-cgi/recording.cgi?msubmenu=
 overlapped &action=<value>[&<parameter>=<value>]

### **5.3. Parameters**

```














|Action|Parameters|Request/<br>Response|Type/<br>Value|Description|
|---|---|---|---|---|
|view|OverlappedIDList|RES|<csv>|Overlapped recording ID list|
||Channel.#.OverlappedID<br>List|RES|<csv>|Overlapped recording ID list for the<br>given Channel<br>**MULTI DIRECTIONAL CAMERA ONLY**<br>|
||ChannelIDList|REQ|<csv>|Channel ID list|
||FromDate|REQ|<string>|The start date and time for when the<br>recording occurred The date must be<br>specified in the format of <YYYY-MM-<br>DD hh:mm:ss>.<br>**Note**<br>**FromDate** and**ToDate** must be<br>sent together for the**view** action.|


30 Recording


|Action|Parameters|Request/<br>Response|Type/<br>Value|Description|
|---|---|---|---|---|
||ToDate|REQ|<string>|The end date and time for when the<br>recording occurred The date must be<br>specified in the format of <YYYY-MM-<br>DD hh:mm:ss>.<br>**Note**<br>**FromDate** and**ToDate** must be<br>sent together for the**view** action.|

### **5.4. Examples**

#### **5.4.1. Getting the overlapped recording between 12:00 AM and 12:00 PM on Aug.** **1, 2014**

REQUEST

```
 http://<Device IP>/stw cgi/recording.cgi?msubmenu=overlapped&action=view&FromDate=2014-08-01
 00:00:00&ToDate=2014-08-01 23:59:59

```

TEXT RESPONSE

```
 HTTP/1.0 200 OK
 Content-type: text/plain
 <Body>

 OverlappedIDList=2,1,0

```

JSON RESPONSE

```
 HTTP/1.0 200 OK
 Content-type: application/json
 <Body>

 {
 "OverlappedIDList": [
 2,
 1,
 0

```

SUNAPI 31


```
 ]
 }

```

32 Recording


## **Chapter 6. Manual Recording**
### **6.1. Description**

The **manualrecording** submenu controls the manual recording status (start/stop).


This chapter applies to NVR only.

Attribute to check for Manual Recording start:



**NOTE**


**Access level**



"attributes/Recording/Support/ManualRecordingStart"

Attribute to check for Manual Recording stop:

"attributes/Recording/Support/ManualRecordingStop"



|Action|NVR|
|---|---|
|view|User|
|control|User|

### **6.2. Syntax**

```
 http://<Device IP>/stw-cgi/recording.cgi?msubmenu=
 manualrecording &action=<value>[&<parameter>=<value>]

### **6.3. Parameters**

```










|Action|Parameters|Request/<br>Response|Type/<br>Value|Description|
|---|---|---|---|---|
|view||||Reads manual recording status.|
|control|Mode|REQ|<enum><br>Start, Stop|Manual recording mode<br>**Note**<br>**Mode** must be sent together with<br>the**control** action.|

### **6.4. Examples**

#### **6.4.1. Getting the current manual recording status**

REQUEST

```
 http://<Device IP>/stw
```



```
 cgi/recording.cgi?msubmenu=manualrecording&action=view

```

SUNAPI 33


TEXT RESPONSE

```
 HTTP/1.0 200 OK
 Content-type: text/plain
 <Body>

 Mode=Start

```

JSON RESPONSE

```
 HTTP/1.0 200 OK
 Content-type: application/json
 <Body>

 {
 "Mode": "Start"
 }

#### **6.4.2. Starting the manual recording**
```

REQUEST

```
 http://<Device IP>/stw cgi/recording.cgi?msubmenu=manualrecording&action=control&Mode=Start

#### **6.4.3. Stopping the manual recording**
```

REQUEST

```
 http://<Device IP>/stw cgi/recording.cgi?msubmenu=manualrecording&action=control&Mode=Stop

```

34 Recording


## **Chapter 7. Calendar Search**
### **7.1. Description**

The **calendarsearch** submenu requests the recording information from a given month.


Attribute to check for Feature Support: "attributes/Recording/Support/SearchCalendar"



**NOTE**


**Access level**



Attribute to check for Failover feature support: "/stw
cgi/attributes.cgi/attributes/recording/Support/FailOverRecording"



|Action|Camera|NVR|
|---|---|---|
|view|User|User|

### **7.2. Syntax**

```
 http://<Device IP>/stw-cgi/recording.cgi?msubmenu=
 calendarsearch &action=<value>[&<parameter>=<value>]

### **7.3. Parameters**

```













|Action|Parameters|Request/<br>Response|Type/<br>Value|Description|
|---|---|---|---|---|
|view|Month|REQ|<string>|Target month for searching<br>Month must be specified in the <YYYY-<br>MM> format.<br>**Note**<br>**Month** must be sent together with<br>the**view** action.|
||ChannelIDList|REQ|<csv>|List of channels in which recordings to<br>be searched.|
||Channel.#.Result|RES|<string>|Search results|
||PrimaryDeviceIPAddress|REQ|<string><br>FormatInfo<br>=IPv4Addre<br>ss or<br>IPv6Addres<br>s|IP address of primary device to which<br>recording to be searched<br>Applicable only if FailOver feature is<br>supported.<br>**NVR ONLY**<br>|



SUNAPI 35


|Action|Parameters|Request/<br>Response|Type/<br>Value|Description|
|---|---|---|---|---|
||IgnoreChannelBasedRes<br>ults|REQ|<bool><br>True, False|If true, consolidated results will be<br>given for all channels<br>**NVR ONLY**<br>|
||Result|RES|<string>|Search results<br>**Note**<br>This parameter provides a<br>response only when<br>**IgnoreChannelBasedResults** is<br>set to**True** in the request.<br>**NVR ONLY**<br>|


**NOTE** represents the channel ID.

### **7.4. Examples**

#### **7.4.1. Searching for recordings from February 2013**

The response will be a string of 31 digits, each representing a day of the month. If a digit is ‘0’, it indicates

that there are no recordings for that day. If the digit is ‘1’, it indicates that a recording exists for that day.


The response code below means that there are recordings for the 6th, 7th and 13th of February 2013.


REQUEST

```
 http://<Device IP>/stw cgi/recording.cgi?msubmenu=calendarsearch&action=view&Month=2013 02&ChannelIDList=0

```

TEXT RESPONSE

```
 HTTP/1.0 200 OK
 Content-type: text/plain
 <Body>

 Channel.0.Result=0000011000001000000000000000000

```

JSON RESPONSE

```
 HTTP/1.0 200 OK

```

36 Recording


```
 Content-type: application/json
 <Body>

 {
 "CalenderSearchResults": [
 {
 "Channel": 0,
 "Result": "0000011000001000000000000000000"
 }
 ]
 }

```

REQUEST

```
 http://<Device IP>/stw cgi/recording.cgi?msubmenu=calendarsearch&action=view&Month=2013 02&ChannelIDList=0,1,2,3& &IgnoreChannelBasedResults=true

```

TEXT RESPONSE

```
 HTTP/1.0 200 OK
 Content-type: text/plain
 <Body>

 Result=0000011000001000000000000000000

```

JSON RESPONSE

```
 HTTP/1.0 200 OK
 Content-type: application/json
 <Body>

 {
 "Result": "0000011000001000000000000000000"
 }

```

SUNAPI 37


## **Chapter 8. Timeline**
### **8.1. Description**

The **timeline** submenu requests recording information from a given time period.


**NOTE** Attribute to check for Feature Support: "attributes/Recording/Support/SearchTimeline"


**Access level**

|Action|Camera|NVR|
|---|---|---|
|view|User|User|


### **8.2. Syntax**

```
 http://<Device IP>/stw-cgi/recording.cgi?msubmenu=
 timeline &action=<value>[&<parameter>=<value>]

### **8.3. Parameters**

```









|Action|Parameters|Request/<br>Response|Type/<br>Value|Description|
|---|---|---|---|---|
|view|Type|REQ|<enum><br>Refer to<br>**Recording**<br>**Types** for<br>supported<br>values|Recording type to search<br>Common Types<br>• All: All video recordings including<br>normal and event recordings.<br>• Normal: Continuous video<br>recordings.<br>• Event: Video recording for all<br>events.<br>**Note**<br>**Type**, **FromDate**, and**ToDate**<br>must be sent together with the<br>**view** action for the camera.|



38 Recording


|Action|Parameters|Request/<br>Response|Type/<br>Value|Description|
|---|---|---|---|---|
||FromDate|REQ|<string>|The start date and time for when the<br>recording occurred.<br>The time is specified in the format of<br><YYYY-MM-DD hh:mm:ss>.<br>**Note**<br>**Type**, **FromDate**, and**ToDate**<br>must be sent together with the<br>**view** action.|
||ToDate|REQ|<string>|The end date and time for when the<br>recording occurred.<br>The time is specified in the format of<br><YYYY-MM-DD hh:mm:ss>.<br>**Note**<br>**Type**, **FromDate**, and**ToDate**<br>must be sent together with the<br>**view** action.|
||OverlappedID|REQ|<int>|Overlapped recording ID<br>For more information about the<br>overlapped recording, please refer to<br>‘5 Overlapped Recording‘(page 22).|
||ChannelIDList|REQ|<csv>|Channel ID list<br>**Note**<br>**ChannelIDList**, **FromDate**, and<br>**ToDate** must be sent together<br>with the**view** action for NVR.|
||TotalCount|RES|<int>|Total number of results|
||Channel.#.Result.#.Start<br>Time|RES|<string>|Requested start date and time<br>The time is specified in the format of<br><YYYY-MM-DD hh:mm:ss DST> (DST<br>displays when supported).|
||Channel.#.Result.#.EndTi<br>me|RES|<string>|Requested end date and time<br>The time is specified in the format of<br><YYYY-MM-DD hh:mm:ss DST> (DST<br>displays when supported).|



SUNAPI 39


|Action|Parameters|Request/<br>Response|Type/<br>Value|Description|
|---|---|---|---|---|
||Channel.#.Result.#.Type|RES|<enum><br>Refer to<br>**Recording**<br>**Types** for<br>supported<br>values|Recording type for the requested<br>period|
||Channel.#.Result.#.BkID|RES|<string>|Bookmark ID<br>**NVR ONLY**<br>|
||PrimaryDeviceIPAddress|REQ|<string><br>FormatInfo<br>=IPv4Addre<br>ss or<br>IPv6Addres<br>s|IP address of primary device in which<br>recording data to be searched.<br>Applicable only if FailOver feature is<br>supported<br>**NVR ONLY**<br>|








|Recording Types|Col2|
|---|---|
|Type|All, Normal, Event, AlarmInput, VideoAnalysis, MotionDetection,<br>NetworkDisconnect, FaceDetection, TamperingDetection, AudioDetection, Tracking,<br>Manual, UserInput, DefocusDetection, FogDetection, AudioAnalysis, QueueEvent,<br>videoloss, EmergencyTrigger, InternalHDDWarmup, GSensorEvent, ShockDetection,<br>TemperatureChangeDetection, BoxTemperatureDetection,<br>BodyTemperatureDetection, MaskDetection, CallRequest, TamperingSwitch,<br>DTMFReceived, ProximitySensor|
|Channel.#.Result.#.<br>Type|Normal, AlarmInput, VideoAnalysis, MotionDetection, NetworkDisconnect,<br>FaceDetection, TamperingDetection, AudioDetection, Tracking, ManualRecording,<br>UserInput, DefocusDetection, FogDetection, AudioAnalysis, ShockDetection,<br>TemperatureChangeDetection, BoxTemperatureDetection,<br>BodyTemperatureDetection, MaskDetection, CallRequest, TamperingSwitch,<br>DTMFReceived, ProximitySensor|



**Recording Types in dynamicrules supported models**






|Type|All, Normal, Event, Rule1, Rule2,.., Rule32|
|---|---|
|Channel.#.Result.#.<br>Type|Normal, Rule1, Rule2,.., Rule32|



**NOTE**



Refer to attributes cgi, cgi section

**stw-cgi/attributes.cgi/recording/timeline**

For supported Type list.



40 Recording


### **8.4. Examples**

#### **8.4.1. Getting the timeline**

**Search for normal recording between 9:00 AM and 10:00 AM on Mar. 3, 2013**


**Type**, **FromDate**, and **ToDate** must be sent together with the **view** action for the camera.


REQUEST

```
 http://<Device IP>/stw cgi/recording.cgi?msubmenu=timeline&action=view&Type=Normal&FromDate=2013 03-03 09:00:00&ToDate=2013-03-03 10:00:00

```

The following request example is for NVR only. **ChannelIDList**, **FromDate**, and **ToDate** must be sent

together with the **view** action for NVR


REQUEST

```
 http://<Device IP>/stw cgi/recording.cgi?msubmenu=timeline&action=view&ChannelIDList=0&FromDate=201
 3-03-03 09:00:00&ToDate=2013-03-03 10:00:00

```

TEXT RESPONSE

```
 HTTP/1.0 200 OK
 Content-type: text/plain
 <Body>

 TotalCount=3
 Channel.0.Result.0.StartTime=2013-03-03 09:15:52
 Channel.0.Result.0.EndTime=2013-03-03 09:18:19
 Channel.0.Result.0.Type=Normal
 Channel.0.Result.1.StartTime=2013-03-03 09:10:56
 Channel.0.Result.1.EndTime=2013-03-03 09:15:51
 Channel.0.Result.1.Type=Normal
 Channel.0.Result.2.StartTime=2013-03-03 00:10:52
 Channel.0.Result.2.EndTime=2013-03-03 00:10:56
 Channel.0.Result.2.Type=Normal

```

JSON RESPONSE

```
 HTTP/1.0 200 OK

```

SUNAPI 41


```
 Content-type: application/json
 <Body>

 {
 "TimeLineSearchResults": [
 {
 "Channel": 0,
 "Results": [
 {
 "Result": 0,
 "StartTime": "2013-03-03 09:15:52",
 "EndTime": "2013-03-03 09:18:19",
 "Type": "Normal"
 },
 {
 "Result": 1,
 "StartTime": "2013-03-03 09:10:56",
 "EndTime": "2013-03-03 09:15:51",
 "Type": "Normal"
 },
 {
 "Result": 2,
 "StartTime": "2013-03-03 00:10:52",
 "EndTime": "2013-03-03 00:10:56",
 "Type": "FaceDetection"
 }
 ]
 }
 ]
 }

```

**Search for motion detection events between 9:00 AM and 10:00 AM on Mar. 3, 2013**


REQUEST

```
 http://<Device IP>/stw cgi/recording.cgi?msubmenu=timeline&action=view&Type=MotionDetection&FromDat
 e=2013-03-03 09:00:00&ToDate=2013-03-03 10:00:00

```

The following request example is for NVR only.


42 Recording


REQUEST

```
 http://<Device IP>/stw cgi/recording.cgi?msubmenu=timeline&action=view&ChannelIDList=0&FromDate=201
 4-02-10 00:00:01&ToDate=2014-02-10 23:59:59&Type=MotionDetection

```

TEXT RESPONSE

```
 HTTP/1.0 200 OK
 Content-type: text/plain
 <Body>

 TotalCount=2
 Channel.0.Result.0.StartTime=2013-03-03 18:16:33
 Channel.0.Result.0.EndTime=2013-03-03 18:16:44
 Channel.0.Result.0.Type=MotionDetection
 Channel.0.Result.1.StartTime=2013-03-03 18:08:36
 Channel.0.Result.1.EndTime=2013-03-03 18:11:36
 Channel.0.Result.1.Type=MotionDetection

```

JSON RESPONSE

```
 HTTP/1.0 200 OK
 Content-type: application/json
 <Body>

 {
 "TimeLineSearchResults": [
 {
 "Channel": 0,
 "Results": [
 {
 "Result": 0,
 "StartTime": "2013-03-03 18:16:33",
 "EndTime": "2013-03-03 18:16:44",
 "Type": "MotionDetection"
 },
 {
 "Result": 1,
 "StartTime": "2013-03-03 18:08:36",

```

SUNAPI 43


```
"EndTime": "2013-03-03 18:11:36",
"Type": "MotionDetection"
}
]
}
]
}

```

Please check if the video storage is enabled (recording.cgi > storage > Enable=True) and



**NOTE**



physically connected, if you receive the error code (STATUS_UNKNOWN_ERROR) in the

response message.



44 Recording


## **Chapter 9. Recording Period**
### **9.1. Description**

The **searchrecordingperiod** submenu requests the recording period.


This chapter applies to NVR only.
**NOTE**

Attribute to check for Feature Support: "attributes/Recording/Support/SearchPeriod"


**Access level**

|Action|NVR|
|---|---|
|view|User|


### **9.2. Syntax**

```
 http://<Device IP>/stw-cgi/recording.cgi?msubmenu=
 searchrecordingperiod &action=<value>[&<parameter>=<value>]

### **9.3. Parameters**

```










|Action|Parameters|Request/<br>Response|Type/<br>Value|Description|
|---|---|---|---|---|
|view||||Reads recording period|
||StartTime|RES|<string>|First recording start time|
||EndTime|RES|<string>|Last recording end time|
||ResultsInUTC|REQ|<bool><br>True, False|Enable or disable search result in UTC|

### **9.4. Examples**

#### **9.4.1. Searching the recording period**

REQUEST

```
 http://<Device IP>/stw
```



```
 cgi/recording.cgi?msubmenu=searchrecordingperiod&action=view

```

TEXT RESPONSE

```
 HTTP/1.0 200 OK
 Content-type: text/plain

```

SUNAPI 45


```
 <Body>

 StartTime=2014-09-22 16:05:34
 EndTime=2014-10-02 11:47:11

```

JSON RESPONSE

```
 HTTP/1.0 200 OK
 Content-type: application/json
 <Body>

 {
 "StartTime": "2014-09-22 16:05:34",
 "EndTime": "2014-10-02 11:47:11"
 }

```

46 Recording


## **Chapter 10. Heat Map Search**
### **10.1. Description**

The **heatmapsearch** submenu requests recording information using the heat map search function and

controls the heat map search settings.


Attribute to check for Feature Support in NVR:



**NOTE**


**Access level**



"attributes/Recording/Support/SearchHeatMap"

Attribute to check for Feature Support in Camera: "recording/heatmapsearch".



|Action|Camera|NVR|
|---|---|---|
|view|Admin|User|
|control|Admin|User|

### **10.2. Syntax**

```
 http://<Device IP>/stw-cgi/recording.cgi?msubmenu=
 heatmapsearch &action=<value>[&<parameter>=<value>]

### **10.3. Parameters**

```









|Action|Parameters|Request/<br>Response|Type/<br>Value|Description|
|---|---|---|---|---|
|view|Type|REQ|<enum><br>GridColor,<br>Results,<br>Status|Type<br>If**Type** is set to GridColor, the**view**<br>action must be sent together with<br>**ChannelIDList**, **FromDate**, **ToDate**,<br>**OverlappedID**, **MotionType**, and<br>**GridRegion**; and if**Type** is set to<br>Results or Status, the**view** action<br>must be sent together with<br>**SearchToken**.<br>**Note**<br>GridColor Type is supported only<br>for NVR.|



SUNAPI 47


|Action|Parameters|Request/<br>Response|Type/<br>Value|Description|
|---|---|---|---|---|
||ChannelIDList|REQ|<csv>|List of channels in which recordings<br>will be searched<br>**ChannelIDList** is valid only when<br>**Type** is set to Gridcolor.<br>**NVR ONLY**<br>|
||FromDate|REQ|<string>|The start date and time for when the<br>recording occurred.<br>**FromDate** is valid only when**Type** is<br>set to Gridcolor.<br>**NVR ONLY**<br>|
||ToDate|REQ|<string>|The end date and time for when the<br>recording occurred.<br>**ToDate** is valid only when**Type** is set<br>to Gridcolor.<br>**NVR ONLY**<br>|
||OverlappedID|REQ|<int>|Overlapped recording ID<br>For more information about the<br>overlapped recording, please refer to<br>‘5 Overlapped Recording‘(page 22).<br>**OverlappedID** is valid only when**Type**<br>is set to Gridcolor.<br>**NVR ONLY**<br>|
||MotionType|REQ|<enum><br>Person,<br>Vehicle,<br>Anything|Motion type<br>**MotionType** is valid only when**Type** is<br>set to Gridcolor.<br>**NVR ONLY**<br>|
||GridRegion|REQ|<string>|Grid area<br>**GridRegion** is valid only when**Type** is<br>set to Gridcolor.<br>**NVR ONLY**<br>|


48 Recording


|Action|Parameters|Request/<br>Response|Type/<br>Value|Description|
|---|---|---|---|---|
||SearchToken|REQ|<string>|Search Session token<br>**SearchToken** is valid only when**Type**<br>is set to Results or Status.|
||Channel.#.ResultGridCol<br>orLevel|RES|<string>|Grid color level result<br>**Channel.#.ResultGridColorLevel** is<br>valid only when**Type** is set to<br>Gridcolor.<br>**NVR ONLY**<br>|
||TotalCount|RES|<int>|Total count<br>**TotalCount** is valid only when**Type** is<br>set to Results.<br>**NVR ONLY**<br>|
||Channel.#.Result.#.Start<br>Time|RES|<string>|Start time for a search in the<br>corresponding results and channel<br>**Channel.#.Result.#.StartTime** is valid<br>only when**Type** is set to Results.<br>DST is shown when supported.<br>**NVR ONLY**<br>|
||Channel.#.Result.#.EndTi<br>me|RES|<string>|End time for search in the<br>corresponding results and channel<br>**Channel.#.Result.#.EndTime** is valid<br>only when**Type** is set to Results.<br>DST is shown when supported.<br>**NVR ONLY**<br>|
||Channel.#.Result.#.Type|RES|<enum><br>Person,<br>Vehicle,<br>Anything|Search type in the corresponding<br>results and channel<br>**Channel.#.Result.#.Type** is valid only<br>when**Type** is set to Results.<br>**NVR ONLY**<br>|
||Status|RES|<enum><br>Completed,<br>NotComple<br>ted|Search status<br>**Status** is valid only when**Type** is set<br>to Status.|



SUNAPI 49


|Action|Parameters|Request/<br>Response|Type/<br>Value|Description|
|---|---|---|---|---|
|control|Mode|REQ|<enum><br>Start,<br>Cancel|Mode|
||ChannelIDList|REQ|<csv>|Channel ID list|
||FromDate|REQ|<string><br><format=YY<br>YY-MM-<br>DDTHH:MM<br>:SSZ>|The start date and time for search|
||ToDate|REQ|<string><br><format=YY<br>YY-MM-<br>DDTHH:MM<br>:SSZ>|The end date and time for search|
||OverlappedID|REQ|<int>|Overlapped recording ID<br>**NVR ONLY**<br>|
||MotionType|REQ|<enum><br>Person,<br>Vehicle,<br>Anything|Type of motion to search<br>**NVR ONLY**<br>|
||GridRegion|REQ|<string>|Grid region for search<br>**NVR ONLY**<br>|
||SearchToken|REQ, RES|<string>|Search token<br>**SearchToken** is a request-only<br>parameter when**Mode** is set to<br>Cancel, but it will return data when<br>**Mode** is set to Start.|
||ResultImageType|REQ|<enum><br>WithBackgr<br>ound,<br>WithoutBac<br>kground|Type of Heat Map Result Image<br>**Note**<br>This parameter is valid only when<br>ResultAsImage is set to True.<br>**CAMERA ONLY**<br>|



50 Recording


|Action|Parameters|Request/<br>Response|Type/<br>Value|Description|
|---|---|---|---|---|
||ResultAsImage|REQ|<bool><br>True, False|HeatMap result as image<br>**CAMERA ONLY**<br> <br>**Note**<br>Currently, the camera supports<br>heat map results only in image<br>format. For this reason, the<br>**ResultAsImage** parameter should<br>be set to True for camera, and this<br>parameter should send along with<br>the**Mode** parameter when**Mode**<br>is set to Start.|

### **10.4. Examples**

#### **10.4.1. Heat map search color**





**Type** must be set to GridColor, and **ChannelIDList**, **FromDate**, **ToDate**, **OverlappedID**, **MotionType** must

be sent together with **view** action.


Heat map search color is supported only for NVR. The following example is for NVR only.


REQUEST

```
 http://<Device IP>/stw cgi/recording.cgi?msubmenu=heatmapsearch&action=view&Type=GridColor&ChannelI
 DList=0,1&FromDate=2013-12-01 10:11:12&ToDate=2014-06-04
 08:09:10&OverlappedId=52&MotionType=Person&GridRegion=0000011111100000000001
 1111100000000000000000000000000000000000000000000000000000000000000000000000
 0000000000000000000000000000000000000000000000000000000000000000000000000000
 0000000000000000000000000000000000000000000000000000000000000000000000000000
 000000

```

TEXT RESPONSE

```
 HTTP/1.0 200 OK
 Content-type: text/plain
 <Body>

 Channel.0.ResultGridColorLevel=000000000000000000000000000000000000000000000
 0000000000000000000000000000000000000000000000000000000000000000000000000000

```

SUNAPI 51


```
 0000000000000000000000000000000000000000000000000000000000000000000000000000
 00000000000000000000000000000000000000000000000000000000000
 Channel.1.ResultGridColorLevel=000000000000000000000000000000000000000000000
 0000000000000000000000000000000000000000000000000000000000000000000000000000
 0000000000000000000000000000000000000000000000000000000000000000000000000000
 00000000000000000000000000000000000000000000000000000000000

```

JSON RESPONSE

```
 HTTP/1.0 200 OK
 Content-type: application/json
 <Body>

 {
 "HeatmapGridColors": [
 {
 "Channel": 0,
 "ResultGridColorLevel":
 "000000000000000000000000000000000000000000000000000000000000000000000000000
 0000000000000000000000000000000000000000000000000000000000000000000000000000
 0000000000000000000000000000000000000000000000000000000000000000000000000000
 00000000000000000000000000000"
 },
 {
 "Channel": 1,
 "ResultGridColorLevel":
 "000000000000000000000000000000000000000000000000000000000000000000000000000
 0000000000000000000000000000000000000000000000000000000000000000000000000000
 0000000000000000000000000000000000000000000000000000000000000000000000000000
 00000000000000000000000000000"
 }
 ]
 }

#### **10.4.2. Heat map search**
```

REQUEST

```
 http://<Device IP>/stw cgi/recording.cgi?msubmenu=heatmapsearch&action=control&ChannelIDList=0&Mode
 =Start&FromDate=2016-09-24T00:00:00Z&ToDate=2016-09
```

52 Recording


```
 24T23:59:59Z&ResultAsImage=True&ResultImageType=WithBackground

```

TEXT RESPONSE

```
 HTTP/1.0 200 OK
 Content-type: text/plain
 <Body>

 SearchToken=HeatMap-2016-09-24T04:32:17-824

```

JSON RESPONSE

```
 HTTP/1.0 200 OK
 Content-type: application/json
 <Body>

 {
 "SearchToken": "HeatMap-2016-09-24T04:32:17-824"
 }

```

The following example is for NVR only.


REQUEST

```
 http://<Device IP>/stw cgi/recording.cgi?msubmenu=heatmapsearch&action=control&Mode=Start&ChannelID
 List=5&FromDate=2013-12-01T10:11:12Z&ToDate=2014-12 20T08:09:10Z&OverlappedId=10&MotionType=Person&GridRegion=111111111111111111
 1111111111111111111111111111111111111111111111111111111111111111111111111111
 1111111111111111111111111111111111111111111111111111111111111111111111111111
 1111111111111111111111111111111111111111111111111111111111111111111111111111
 1111111111

```

TEXT RESPONSE

```
 HTTP/1.0 200 OK
 Content-type: text/plain
 <Body>

```

SUNAPI 53


```
 SearchToken=0926800821074333

```

JSON RESPONSE

```
 HTTP/1.0 200 OK
 Content-type: application/json
 <Body>

 {
 "SearchToken": "0104700429062444"
 }

#### **10.4.3. Getting the status of searching**
```

**Type** must be set to Status, and **SearchToken** must be sent with **view** action.


REQUEST

```
 http://<Device IP>/stw cgi/recording.cgi?msubmenu=heatmapsearch&action=view&Type=Status&SearchToken
 =0926800821074333

```

TEXT RESPONSE

```
 HTTP/1.0 200 OK
 Content-type: text/plain
 <Body>

 Status=Completed

```

JSON RESPONSE

```
 HTTP/1.0 200 OK
 Content-type: application/json
 <Body>

 {
 "Status": "Completed"

```

54 Recording


```
 }

#### **10.4.4. Getting the result**
```

**Type** must be set to Results, and **SearchToken** must be sent with **view** action.


REQUEST

```
 http://<Device IP>/stw cgi/recording.cgi?msubmenu=heatmapsearch&action=view&Type=Results&SearchToke
 n=0926800821074333

```

RESPONSE

```
 HTTP/1.0 200 OK
 Content-type: text/plain
 <Body>

 <PNG Image>

```

The following response example is for NVR only.


TEXT RESPONSE

```
 HTTP/1.0 200 OK
 Content-type: text/plain
 <Body>

 TotalCount=2
 Channel.0.Result.1.StartTime=2014-11-02T05:16:12Z
 Channel.0.Result.1.EndTime=2014-11-02T05:16:42Z
 Channel.0.Result.1.Type=Person
 Channel.0.Result.2.StartTime=2014-11-02T06:25:53Z
 Channel.0.Result.2.EndTime=2014-11-02T06:26:23Z
 Channel.0.Result.2.Type=Person

```

JSON RESPONSE

```
 HTTP/1.0 200 OK
 Content-type: application/json

```

SUNAPI 55


```
 <Body>

 {
 "TotalCount": 2,
 "HeatmapSearchResults": [
 {
 "Channel": 0,
 "Results": [
 {
 "Result": 1,
 "StartTime": "2014-11-02T05:16:12Z",
 "EndTime": "2014-11-02T05:16:42Z",
 "Type": "Person"
 },
 {
 "Result": 2,
 "StartTime": "2014-11-02T06:25:53Z",
 "EndTime": "2014-11-02T06:26:23Z",
 "Type": "Person"
 }
 ]
 }
 ]
 }

#### **10.4.5. Cancelling the search**
```

REQUEST

```
 http://<Device IP>/stw cgi/recording.cgi?msubmenu=heatmapsearch&action=control&Mode=Cancel&SearchTo
 ken=0926800821074333

```

56 Recording


## **Chapter 11. People Count Search**
### **11.1. Description**

The **peoplecountsearch** submenu requests recording information using the people count search

function, and controls the people count search settings.


This chapter applies to Camera only.
**NOTE**

Attribute to check for Feature Support: "recording/peoplecountsearch"


**Access level**

|Action|Camera|
|---|---|
|view|Admin|
|control|Admin|


### **11.2. Syntax**

```
 http://<Device IP>/stw-cgi/recording.cgi?msubmenu=
 peoplecountsearch &action=<value>[&<parameter>=<value>]

### **11.3. Parameters**

```















|Action|Parameters|Request/<br>Response|Type/<br>Value|Description|
|---|---|---|---|---|
|view|Type|REQ|<enum><br>Results,<br>Status|Type<br>If**Type** is set to Results or Status, the<br>**view** action must be sent together<br>with**SearchToken**.|
||SearchToken|REQ|<string>|Search token|
||ResultInterval|RES|<enum><br>Hourly,<br>Daily,<br>Weekly,<br>Monthly|Search result interval|



SUNAPI 57


|Action|Parameters|Request/<br>Response|Type/<br>Value|Description|
|---|---|---|---|---|
||Camera.#.Line.#.Directio<br>n.#.Result|RES|<csv>|People Count Search Results.<br>If**ResultInterval** is Hourly, search<br>results are in terms of hours and the<br>number of results is fixed, i.e. 24.<br>Here, the first result in the array<br>represents the 0<br>th hour of the day, and<br>the last result in the array represents<br>the 23<br>rd hour of the day.<br>If**ResultInterval** is Daily, search<br>results are in terms of days and the<br>first result in the array represents the<br>first day of the month while the last<br>result in the array represents the last<br>day of the month.<br>If**ResultInterval** is Weekly, search<br>results are in terms of weeks.<br>If**ResultInterval** is Monthly, search<br>results are in terms of months and the<br>first result in the array represents the<br>first month of the year, while the last<br>result in the array represents the last<br>month of the year.<br>**Note**<br>**ResultInterval** is fixed by the<br>camera based on**FromDate** and<br>**ToDate** of the search|
||Status|RES|<enum><br>Completed,<br>NotComple<br>ted|Search status<br>**Status** is valid only when**Type** is set<br>to Status.|
|control|Mode|REQ|<enum><br>Start,<br>Cancel|Mode|
||Channel|REQ|<int>|Channel ID|


58 Recording


|Action|Parameters|Request/<br>Response|Type/<br>Value|Description|
|---|---|---|---|---|
||FromDate|REQ|<string><br><format=YY<br>YY-MM-<br>DDTHH:MM<br>:SSZ>|The start date and time for search|
||ToDate|REQ|<string><br><format=YY<br>YY-MM-<br>DDTHH:MM<br>:SSZ>|The end date and time for search|
||SearchToken|REQ, RES|<string>|Search token<br>**SearchToken** is a request-only<br>parameter when**Mode** is set to<br>Cancel, but it will return data when<br>**Mode** is set to Start.|
||Camera.#.Line.#.Directio<br>n|REQ|<csv><br>In,Out|People Count Line Direction to search|

### **11.4. Examples**

#### **11.4.1. People Count Search**

REQUEST

```
 http://<Device IP>/stw
```





```
 cgi/recording.cgi?msubmenu=peoplecountsearch&action=control&Channel=0&Mode=S
 tart&FromDate=2016-09-24T00:00:00Z&ToDate=2016-09 24T23:59:59Z&Camera.PeopleCount Master.Line.Gate1.Direction=In,Out&Camera.PeopleCount Master.Line.Gate2.Direction=In,Out

```

TEXT RESPONSE

```
 HTTP/1.0 200 OK
 Content-type: text/plain
 <Body>

```

SUNAPI 59


```
 SearchToken=PeopleCount-2016-09-24T02:32:51-614

```

JSON RESPONSE

```
 HTTP/1.0 200 OK
 Content-type: application/json
 <Body>

 {
 "SearchToken": " PeopleCount-2016-09-24T02:32:51-614"
 }

#### **11.4.2. Getting the status of searching**
```

**Type** must be set to Status, and **SearchToken** must be sent with **view** action.


REQUEST

```
 http://<Device IP>/stw-cgi/recording.cgi?msubmenu=peoplecountsearch
 &action=view&Type=Status&SearchToken=PeopleCount-2016-09-24T02:32:51-614

```

TEXT RESPONSE

```
 HTTP/1.0 200 OK
 Content-type: text/plain
 <Body>

 Status=Completed

```

JSON RESPONSE

```
 HTTP/1.0 200 OK
 Content-type: application/json
 <Body>

 {
 "Status": "Completed"
 }

```

60 Recording


#### **11.4.3. Getting the result**

**Type** must be set to Results, and **SearchToken** must be sent with **view** action.


REQUEST

```
 http://<Device IP>/stw-cgi/recording.cgi?msubmenu=peoplecountsearch
 &action=view&Type=Results&SearchToken=PeopleCount-2016-09-24T02:32:51-614

```

TEXT RESPONSE

```
 HTTP/1.0 200 OK
 Content-type: text/plain
 <Body>

 ResultInterval = Hourly
 Camera.PeopleCount-Master.Line.Gate1.Direction.In.Result =
 0,0,0,0,0,0,2,0,0,0,0,0,0,0,6,0,0,0,0,0,3,0,2,2
 Camera.PeopleCount-Master.Line.Gate1.Direction.Out.Result =
 0,0,0,0,0,0,1,0,0,0,0,0,0,0,2,0,0,0,0,0,2,0,5,3
 Camera.PeopleCount-Master.Line.Gate1.Direction.In.Result =
 0,0,0,0,0,0,0,0,0,0,0,0,0,1,1,0,0,0,0,0,11,0,0,0
 Camera.PeopleCount-Master.Line.Gate2.Direction.Out.Result =
 0,0,0,0,0,0,2,0,0,1,1,0,0,1,6,0,0,0,0,0,11,0,3,2

```

JSON RESPONSE

```
 HTTP/1.0 200 OK
 Content-type: application/json
 <Body>

 {
 "ResultInterval": "Hourly",
 "PeopleCountSearchResults": [
 {
 "Camera": "PeopleCount-Master",
 "LineResults": [
 {
 "Line": "Gate1",
 "DirectionResults": [
 {

```

SUNAPI 61


```
 "Direction": "In",
 "Result":
 "0,0,0,0,0,0,2,0,0,0,0,0,0,0,6,0,0,0,0,0,3,0,2,2"
 },
 {
 "Direction": "Out",
 "Result":
 "0,0,0,0,0,0,1,0,0,0,0,0,0,0,2,0,0,0,0,0,2,0,5,3"
 }
 ]
 },
 {
 "Line": "Gate2",
 "DirectionResults": [
 {
 "Direction": "In",
 "Result":
 "0,0,0,0,0,0,0,0,0,0,0,0,0,1,1,0,0,0,0,0,11,0,0,0"
 },
 {
 "Direction": "Out",
 "Result":
 "0,0,0,0,0,0,2,0,0,1,1,0,0,1,6,0,0,0,0,0,11,0,3,2"
 }
 ]
 }
 ]
 }
 ]
 }

#### **11.4.4. Cancelling the search**
```

REQUEST

```
 http://<Device IP>/stw-cgi/recording.cgi?msubmenu=peoplecountsearch
 &action=control&Mode=Cancel&SearchToken=PeopleCount-2016-09-24T02:32:51-614

```

62 Recording


## **Chapter 12. Vehicle Count Search**
### **12.1. Description**

The **vehiclecountsearch** submenu requests recording information using the vehicle count search

function, and controls the vehicle count search settings.


This chapter applies to Camera only.
**NOTE**

Attribute to check for Feature Support: "recording/vehiclecountsearch"


**Access level**

|Action|Camera|
|---|---|
|view|Admin|
|control|Admin|


### **12.2. Syntax**

```
 http://<Device IP>/stw-cgi/recording.cgi?msubmenu=
 vehiclecountsearch &action=<value>[&<parameter>=<value>]

### **12.3. Parameters**

```















|Action|Parameters|Request/<br>Response|Type/<br>Value|Description|
|---|---|---|---|---|
|view|Type|REQ|<enum><br>Results,<br>Status|Type<br>If**Type** is set to Results or Status, the<br>**view** action must be sent together<br>with**SearchToken**.|
||SearchToken|REQ|<string>|Search token|
||ShowAIStats|REQ|<bool><br>True,False|Whether to show AI Stats|
||ResultInterval|RES|<enum><br>Hourly,<br>Daily,<br>Weekly,<br>Monthly|Search result interval|



SUNAPI 63


|Action|Parameters|Request/<br>Response|Type/<br>Value|Description|
|---|---|---|---|---|
||Camera.#.Line.#.Directio<br>n.#.Result|RES|<csv>|Vehicle Count Search Results.<br>If**ResultInterval** is Hourly, search<br>results are in terms of hours and the<br>number of results is fixed, i.e. 24.<br>Here, the first result in the array<br>represents the 0<br>th hour of the day, and<br>the last result in the array represents<br>the 23<br>rd hour of the day.<br>If**ResultInterval** is Daily, search<br>results are in terms of days and the<br>first result in the array represents the<br>first day of the month while the last<br>result in the array represents the last<br>day of the month.<br>If**ResultInterval** is Weekly, search<br>results are in terms of weeks.<br>If**ResultInterval** is Monthly, search<br>results are in terms of months and the<br>first result in the array represents the<br>first month of the year, while the last<br>result in the array represents the last<br>month of the year.|
||Camera.#.Line.#.Directio<br>n.#.Car|RES|<csv>|Car Count Search Results.<br>This parameter is shown when<br>**ShowAIStats** is True|
||Camera.#.Line.#.Directio<br>n.#.Bus|RES|<csv>|Bus Count Search Results.<br>This parameter is shown when<br>**ShowAIStats** is True|
||Camera.#.Line.#.Directio<br>n.#.Truck|RES|<csv>|Truck Count Search Results.<br>This parameter is shown when<br>**ShowAIStats** is True|
||Camera.#.Line.#.Directio<br>n.#.Motorcycle|RES|<csv>|Motorcycle Count Search Results.<br>This parameter is shown when<br>**ShowAIStats** is True|



64 Recording


|Action|Parameters|Request/<br>Response|Type/<br>Value|Description|
|---|---|---|---|---|
||Camera.#.Line.#.Directio<br>n.#.Bicycle|RES|<csv>|Bicycle Count Search Results.<br>This parameter is shown when<br>**ShowAIStats** is True<br>**Note**<br>**ResultInterval** is fixed by the<br>camera based on**FromDate** and<br>**ToDate** of the search|
||Status|RES|<enum><br>Completed,<br>NotComple<br>ted|Search status<br>**Status** is valid only when**Type** is set<br>to Status.|
|control|Mode|REQ|<enum><br>Start,<br>Cancel|Mode|
||Channel|REQ|<int>|Channel ID|
||FromDate|REQ|<string><br><format=YY<br>YY-MM-<br>DDTHH:MM<br>:SSZ>|The start date and time for search|
||ToDate|REQ|<string><br><format=YY<br>YY-MM-<br>DDTHH:MM<br>:SSZ>|The end date and time for search|
||SearchToken|REQ, RES|<string>|Search token<br>**SearchToken** is a request-only<br>parameter when**Mode** is set to<br>Cancel, but it will return data when<br>**Mode** is set to Start.|
||Camera.#.Line.#.Directio<br>n|REQ|<csv><br>In,Out|Vehicle Count Line Direction to search|

### **12.4. Examples**







SUNAPI 65


#### **12.4.1. Vehicle Count Search**

REQUEST

```
 http://<Device IP>/stw cgi/recording.cgi?msubmenu=vehiclecountsearch&action=control&Channel=0&Mode=
 Start&FromDate=2016-09-24T00:00:00Z&ToDate=2016-09 24T23:59:59Z&Camera.VehicleCount Master.Line.Gate1.Direction=In,Out&Camera.VehicleCount Master.Line.Gate2.Direction=In,Out

```

TEXT RESPONSE

```
 HTTP/1.0 200 OK
 Content-type: text/plain
 <Body>

 SearchToken=VehicleCount-2016-09-24T02:32:51-614

```

JSON RESPONSE

```
 HTTP/1.0 200 OK
 Content-type: application/json
 <Body>

 {
 "SearchToken": " VehicleCount-2016-09-24T02:32:51-614"
 }

#### **12.4.2. Getting the status of searching**
```

**Type** must be set to Status, and **SearchToken** must be sent with **view** action.


REQUEST

```
 http://<Device IP>/stw-cgi/recording.cgi?msubmenu=vehiclecountsearch
 &action=view&Type=Status&SearchToken=VehicleCount-2016-09-24T02:32:51-614

```

TEXT RESPONSE

```
 HTTP/1.0 200 OK
 Content-type: text/plain

```

66 Recording


```
 <Body>

 Status=Completed

```

JSON RESPONSE

```
 HTTP/1.0 200 OK
 Content-type: application/json
 <Body>

 {
 "Status": "Completed"
 }

#### **12.4.3. Getting the result**
```

**Type** must be set to Results, and **SearchToken** must be sent with **view** action.


REQUEST

```
 http://<Device IP>/stw-cgi/recording.cgi?msubmenu=vehiclecountsearch
 &action=view&Type=Results&SearchToken=VehicleCount-2016-09-24T02:32:51-614

```

TEXT RESPONSE

```
 HTTP/1.0 200 OK
 Content-type: text/plain
 <Body>

 ResultInterval = Hourly
 Camera.VehicleCount-Master.Line.Gate1.Direction.In.Result =
 0,0,0,0,0,0,2,0,0,0,0,0,0,0,6,0,0,0,0,0,3,0,2,2
 Camera.VehicleCount-Master.Line.Gate1.Direction.Out.Result =
 0,0,0,0,0,0,1,0,0,0,0,0,0,0,2,0,0,0,0,0,2,0,5,3
 Camera.VehicleCount-Master.Line.Gate1.Direction.In.Result =
 0,0,0,0,0,0,0,0,0,0,0,0,0,1,1,0,0,0,0,0,11,0,0,0
 Camera.VehicleCount-Master.Line.Gate2.Direction.Out.Result =
 0,0,0,0,0,0,2,0,0,1,1,0,0,1,6,0,0,0,0,0,11,0,3,2

```

SUNAPI 67


JSON RESPONSE

```
 HTTP/1.0 200 OK
 Content-type: application/json
 <Body>

 {
 "ResultInterval": "Hourly",
 "VehicleCountSearchResults": [
 {
 "Camera": "VehicleCount-Master",
 "LineResults": [
 {
 "Line": "Gate1",
 "DirectionResults": [
 {
 "Direction": "In",
 "Result":
 "0,0,0,0,0,0,2,0,0,0,0,0,0,0,6,0,0,0,0,0,3,0,2,2"
 },
 {
 "Direction": "Out",
 "Result":
 "0,0,0,0,0,0,1,0,0,0,0,0,0,0,2,0,0,0,0,0,2,0,5,3"
 }
 ]
 },
 {
 "Line": "Gate2",
 "DirectionResults": [
 {
 "Direction": "In",
 "Result":
 "0,0,0,0,0,0,0,0,0,0,0,0,0,1,1,0,0,0,0,0,11,0,0,0"
 },
 {
 "Direction": "Out",
 "Result":
 "0,0,0,0,0,0,2,0,0,1,1,0,0,1,6,0,0,0,0,0,11,0,3,2"
 }
 ]

```

68 Recording


```
 }
 ]
 }
 ]
 }

#### **12.4.4. Cancelling the search**
```

REQUEST

```
 http://<Device IP>/stw cgi/recording.cgi?msubmenu=vehiclecountsearch&action=control&Mode=Cancel&Sea
 rchToken=VehicleCount-2016-09-24T02:32:51-614

```

SUNAPI 69


## **Chapter 13. POS Configuration**
### **13.1. Description**

The **posconf** submenu is used for configuring a POS device.


This chapter applies to NVR only.
**NOTE**

Attribute to check for Feature Support: "attributes/System/Limit/MaxPOS"


**Access level**

|Action|NVR|
|---|---|
|view|User|
|set|User|


### **13.2. Syntax**

```
 http://<Device IP>/stw-cgi/recording.cgi?msubmenu=
 posconf &action=<value>[&<parameter>=<value>]

### **13.3. Parameters**

```














|Action|Parameters|Request/<br>Response|Type/<br>Value|Description|
|---|---|---|---|---|
|view|DeviceIDList|REQ|<csv>|Optional request parameter for<br>sending a specific device ID.<br>**Note**<br>DeviceID starts from 0.|
|set|DeviceID|REQ, RES|<int><br>Start,<br>Cancel|Mode|
||DeviceName|REQ, RES|<string>|Name of the device|
||Port|REQ, RES|<int>|Port number to which POS is<br>configured|
||ChannelIDList|REQ, RES|<csv>|Channels to which POs is mapped|


70 Recording


|Action|Parameters|Request/<br>Response|Type/<br>Value|Description|
|---|---|---|---|---|
||EncodingType|REQ, RES|<enum><br>US-ASCII,<br>UTF-8, UTF-<br>16, EUC-KR,<br>ISO-2022-<br>KR, EUC-JP,<br>SHIFT-JIS,<br>ISO-2022-<br>JP, EUC-CN,<br>ISO-2022-<br>CN, BIG5,<br>GB2312,<br>ISO-8859-1,<br>ISO-8859-2,<br>ISO-8859-3,<br>WINDOWS-<br>1250,<br>WINDOWS-<br>1251,<br>WINDOWS-<br>1252,<br>WINDOWS-<br>1253,<br>WINDOWS-<br>1254,<br>CP850,<br>CP866,<br>CP932,<br>CP949,<br>CP950,<br>CP1250,<br>CP1251,<br>CP1252,<br>CP1253,<br>CP1254,<br>CP1257|POS encoding type setting|
||ReceiptStart|REQ, RES|<string>|Receipt start identifier|
||ReceiptStartType|REQ, RES|<enum><br>Text,HexCo<br>de,RegExpr<br>ession|Receipt start identifier type|
||ReceiptEnd|REQ, RES|<string>|Receipt end identifier|


SUNAPI 71


|Action|Parameters|Request/<br>Response|Type/<br>Value|Description|
|---|---|---|---|---|
||ReceiptEndType|REQ, RES|<enum><br>Text,HexCo<br>de,RegExpr<br>ession|Receipt end identifier type|
||EventPlaybackStartTime|REQ, RES|<int>|Playback start time|
||EventPlaybackStartTime<br>Units|REQ, RES|<enum><br>Seconds|Time units|
||Enable|REQ, RES|<bool><br>True, False|Enabling and Disabling a device|
||DeviceType|REQ, RES|<enum><br>User<br>Defined,<br>EPSON,WIN<br>COR,AXIHO<br>N,RADIANT<br>SYSTEM,IB<br>M,ANPR|Pos Device Types|

### **13.4. Examples**

REQUEST

```
 http://<Device IP>/stw
```



```
 cgi/recording.cgi?msubmenu=posconf&action=view&DeviceIDList=0,1

```

TEXT RESPONSE

```
 HTTP/1.0 200 OK
 Content-type: text/plain
 <Body>

 DeviceID.0.DeviceName=TEXT 01
 DeviceID.0.Enable=True
 DeviceID.0.Port=7001
 DeviceID.0.EventPlaybackStartTime=0
 DeviceID.0.EventPlaybackStartTimeUnits=Seconds
 DeviceID.0.ReceiptStart=(1)
 DeviceID.0.ReceiptEnd=(2)
 DeviceID.0.EncodingType=US-ASCII

```

72 Recording


```
 DeviceID.0.ChannelIDList=0,1,2,3,4,5,6,7,16,17,18,19,20,21,22,23,32,33,34,35
,36,37,38,39,48,49,50,51,52,53,54,55
 DeviceID.1.DeviceName=TEXT 02
 DeviceID.1.Enable=True
 DeviceID.1.Port=7002
 DeviceID.1.EventPlaybackStartTime=0
 DeviceID.1.EventPlaybackStartTimeUnits=Seconds
 DeviceID.1.ReceiptStart=(1)
 DeviceID.1.ReceiptEnd=(2)
 DeviceID.1.EncodingType=US-ASCII
 DeviceID.1.ChannelIDList=8,9,10,11,12,13,14,15,24,25,26,27,28,29,30,31,40,41
,42,43,44,45,46,47,56,57,58,59,60,61,62,63

```

JSON RESPONSE

```
 HTTP/1.0 200 OK
 Content-type: application/json
 <Body>

 {
 "POSDevices": [
 {
 "DeviceID": 0,
 "DeviceName": "TEXT 01",
 "Enable": true,
 "Port": 7001,
 "EventPlaybackStartTime": 0,
 "EventPlaybackStartTimeUnits": "Seconds",
 "ReceiptStart": "(1)",
 "ReceiptEnd": "(2)",
 "EncodingType": "US-ASCII",
 "ChannelIDList": [
 "0",
 "1",
 "2",
 "3",
 "4",
 "5",
 "6",
 "7",
 "16",

```

SUNAPI 73


```
 "17",
 "18",
 "19",
 "20",
 "21",
 "22",
 "23",
 "32",
 "33",
 "34",
 "35",
 "36",
 "37",
 "38",
 "39",
 "48",
 "49",
 "50",
 "51",
 "52",
 "53",
 "54",
 "55"
 ]
 },
 {
 "DeviceID": 1,
 "DeviceName": "TEXT 02",
 "Enable": true,
 "Port": 7002,
 "EventPlaybackStartTime": 0,
 "EventPlaybackStartTimeUnits": "Seconds",
 "ReceiptStart": "(1)",
 "ReceiptEnd": "(2)",
 "EncodingType": "US-ASCII",
 "ChannelIDList": [
 "8",
 "9",
 "10",
 "11",
 "12",

```

74 Recording


```
 "13",
 "14",
 "15",
 "24",
 "25",
 "26",
 "27",
 "28",
 "29",
 "30",
 "31",
 "40",
 "41",
 "42",
 "43",
 "44",
 "45",
 "46",
 "47",
 "56",
 "57",
 "58",
 "59",
 "60",
 "61",
 "62",
 "63"
 ]
 }
 ]
 }

```

SUNAPI 75


## **Chapter 14. POS Event Configuration**
### **14.1. Description**

The **poseventconf** submenu is used to configure a POS event in the device.


This chapter applies to NVR only.
**NOTE**

Attribute to check for Feature Support: "attributes/System/Limit/MaxPOS"


**Access level**

|Action|NVR|
|---|---|
|view|User|
|set|User|
|add/update|User|
|remove|User|


### **14.2. Syntax**

```
 http://<Device IP>/stw-cgi/recording.cgi?msubmenu=
 poseventconf &action=<value>[&<parameter>=<value>...]

### **14.3. Parameters**

```










|Action|Parameters|Request/<br>Response|Type/<br>Value|Description|
|---|---|---|---|---|
|view|||||
|set|AmountEventEnable|REQ, RES|<bool><br>True, False|Enables or disables the event based<br>on the amount|
||TotalType|REQ, RES|<enum><br>Equal,<br>Above,<br>Below|Total amount condition|
||TotalAmount|REQ, RES|<float>|Total amount|
|add/update|KeywordIndex|REQ, RES|<int>|Index of keyword to be<br>added/updated|
||KeywordCondition|REQ, RES|<string>|Keyword string|
|remove|KeywordIndex|REQ|<int>|Valid keyword index that needs to be<br>removed.|


76 Recording


### **14.4. Examples**

REQUEST

```
 http://<Device IP>/stw-cgi/recording.cgi?msubmenu=poseventconf&action=view

```

TEXT RESPONSE

```
 HTTP/1.0 200 OK
 Content-type: text/plain
 <Body>

 AmountEventEnable=True
 TotalAmount=100.000000
 TotalType=Above
 KeywordIndex.1.KeywordCondition=Apple
 KeywordIndex.2.KeywordCondition=banana

```

JSON RESPONSE

```
 HTTP/1.0 200 OK
 Content-type: application/json
 <Body>

 {
 "AmountEventEnable": true,
 "TotalAmount": 100,
 "TotalType": "Above",
 "Keywords": [
 {
 "KeywordIndex": 1,
 "KeywordCondition": "Apple"
 },
 {
 "KeywordIndex": 2,
 "KeywordCondition": "banana"
 }
 ]
 }

```

SUNAPI 77


## **Chapter 15. POS Data**
### **15.1. Description**

The **posdata** submenu is used to receive the live POS data from the device.


This chapter applies to NVR only.
**NOTE**

Attribute to check for Feature Support: "attributes/System/Limit/MaxPOS"


**Access level**

|Action|NVR|
|---|---|
|monitordiff|User|


### **15.2. Syntax**

```
 http://<Device IP>/stw-cgi/recording.cgi?msubmenu=
 posdata &action=<value>[&<parameter>=<value>...]

### **15.3. Parameters**

```








|Action|Parameter|Request/<br>Response|Type/<br>Value|Description|
|---|---|---|---|---|
|monitordiff|DeviceIDList|REQ, RES|<csv>|Device ID list for which POS data<br>needs to be monitored|
||ReceivedDate|RES|<string>|Date and time|
||DeviceID|RES|<int>|Device ID<br>**Note**<br>DeviceID starts from 0.|
||Receipt|RES|<string>|Receipt information|

### **15.4. Examples**

REQUEST

```
 http://<Device IP>/stw-cgi/recording.cgi?msubmenu=posdata&action=monitordiff

```

TEXT RESPONSE

```
 HTTP/1.0 200 OK
 Content-type: text/plain

```

78 Recording


```
 <Body>

 --SamsungTechwin
 Content-type:text/plain

 ReceivedDate=2016-07-28T05:06:55Z
 DeviceID=1
 Receipt=
 03-06-16 2:43P
 <keyword>APPLE</keyword> 9.00
 BERRY 3.50
 MELON 10.50
 PLUM 3.00

 SUBTOTAL 26.00
 TAX 03.00
 TOTAL 29.00
 CASH 30.00
 CHANGE 01.00

 --SamsungTechwin
 Content-type:text/plain

 ReceivedDate=2016-07-28T05:06:55Z
 DeviceID=0
 Receipt=
 02-06-16 2:43P
 OKRA 5.00
 OIL 9.50
 LEMON 2.50
 GREEN BANANNAS 3.00
 YELLOW BANANNAS 3.00

```

JSON RESPONSE

```
 HTTP/1.0 200 OK
 Content-type: application/json
 <Body>

```

SUNAPI 79


```
 --SamsungTechwin
 Content-type:application/json

 {
 "ReceivedDate": "2016-07-28T05:06:55Z",
 "DeviceID": 1,
 "Receipt": "\r\n03-06-16 2:43P\r\n<keyword>APPLE</keyword>
 \t\t9.00\r\nBERRY\t \t3.50\r\nMELON \t\t10.50\r\nPLUM\t
 \t3.00\r\n\r\nSUBTOTAL \t26.00\r\nTAX \t\t03.00\r\nTOTAL \t\t29.00\r\nCASH
 \t\t30.00\r\nCHANGE \t\t01.00\r\n"
 }

 --SamsungTechwin
 Content-type:application/json

 {
 "ReceivedDate": "2016-07-28T05:06:55Z",
 "DeviceID": 0,
 "Receipt": "\r\n02-06-16 2:43P\r\nOKRA \t\t5.00\r\nOIL\t \t9.50\r\nLEMON
 \t\t2.50\r\nGREEN BANANNAS\t3.00\r\nYELLOW
 BANANNAS\t3.00\r\n\r\n\r\nSUBTOTAL \t23.00\r\nTAX \t\t02.70\r\nTOTAL
 \t\t25.70\r\nCASH \t\t30.00\r\nCHANGE \t\t04.30\r\n"
 }

```

80 Recording


## **Chapter 16. POS Calendar**
### **16.1. Description**

The **poscalendar** submenu is used to get the availability of POS data in a month.


This chapter applies to NVR only.
**NOTE**

Attribute to check for Feature Support: "attributes/System/Limit/MaxPOS"


**Access level**

|Action|NVR|
|---|---|
|view|User|


### **16.2. Syntax**

```
 http://<Device IP>/stw-cgi/recording.cgi?msubmenu=
 poscalendar &action=<value>[&<parameter>=<value>...]

### **16.3. Parameters**

```








|Action|Parameter|Request/<br>Response|Type/<br>Value|Description|
|---|---|---|---|---|
|view|Month|REQ|<string>|Target month for searching<br>Month must be specified in <YYYY-<br>MM> format.|
||Calendar|RES|<string>|String of 31 characters consisting of 0s<br>and 1s to represent each day of the<br>month; if data is available it is set to 1<br>and set to 0 otherwise|

### **16.4. Examples**

REQUEST

```
 http://<Device IP>/stw cgi/recording.cgi?msubmenu=poscalendar&action=view&Month=2016-09

```

TEXT RESPONSE

```
 HTTP/1.0 200 OK
 Content-type: text/plain

```

SUNAPI 81


```
 <Body>

 Calendar=0000011110000000001100101010101

```

JSON RESPONSE

```
 HTTP/1.0 200 OK
 Content-type: application/json
 <Body>

 {
 "Calendar": "0000011110000000001100101010101"
 }

```

82 Recording


## **Chapter 17. Meta Data Search**
### **17.1. Description**

The **metadata** submenu searches POS, GPS, video, audio, and image information for a given search

criteria.


This chapter applies to NVR only.

Attribute to check for Feature Support in NVR: "attributes/Recording/Support/

SearchMetadata"



**NOTE**


**Access level**



Attribute to check for MaxResults supported in NVR: "attributes/Recording/

metadata/view/MaxResults"

Attribute to check for Maximum Allowed time gap between search from date and search

to date: "attributes/Recording/Limit/MaxMetadataSearchDays"



|Action|NVR|
|---|---|
|view|User|
|control|User|

### **17.2. Syntax**

```
 http://<Device IP>/stw-cgi/recording.cgi?msubmenu=
 metadata &action=<value>[&<parameter>=<value>]

### **17.3. Parameters**

```










|Action|Parameters|Request/<br>Response|Type/<br>Value|Description|
|---|---|---|---|---|
|view|Type|REQ|<enum><br>Results,<br>Status|Search Type|
||SearchToken|REQ|<sring>|Search Session token|
||ResultFromIndex|REQ|<int>|Index from which search results to be<br>fetched|
||ResultFromTime|REQ|<string>|Time from which search results are<br>fetched.<br>Time in UTC format.<br>YYYY-MM-DDTHH:MM::SSZ|


SUNAPI 83


|Action|Parameters|Request/<br>Response|Type/<br>Value|Description|
|---|---|---|---|---|
||ResultToTime|REQ|<string>|Time to which search results are<br>fetched.<br>Time in UTC format.<br>YYYY-MM-DDTHH:MM::SSZ|
||MaxResults|REQ|<int>|Maximum number of search results to<br>return|
||Status|RES|<enum><br>Results,<br>Status|Search status|
||TotalResultsFound|RES|<int>|Total results|
||TotalCount|RES|<int>|Total result count|
||TimedOut|RES|<bool><br>True, False||
|SearchToke<br>nExpiryTim<br>e|RES|<string><br>UTCFormat<br>=YYYY-MM-<br>DDTHH:MM<br>:SSZ|Time at<br>which<br>search<br>token<br>expires||
|Result.#.Da<br>te|RES|<string><br>UTCFormat<br>=YYYY-MM-<br>DDTHH:MM<br>:SSZ|Result date||
|Result.#.Pla<br>yTime|RES|<string><br>UTCFormat<br>=YYYY-MM-<br>DDTHH:MM<br>:SSZ|Result play<br>time||
|Result.#.De<br>viceID|RES|<int>|POS ID||
|Result.#.Te<br>xtData|RES|<string>|POS receipt||
|Result.#.Ke<br>ywordsMat<br>ched|RES|<csv>|Keywords<br>found in<br>POS receipt||



84 Recording


|Action|Parameters|Request/<br>Response|Type/<br>Value|Description|
|---|---|---|---|---|
|Result.#.Ch<br>annelIDList|RES|<csv>|Result<br>channel ID<br>List||
|Result.#.BkI<br>D|RES|<string>|Bookmark<br>ID|control|
|Mode|REQ|<enum><br>Start,<br>Cancel,<br>Renew,<br>Stop|Search<br>Mode||
|MetadataTy<br>pe|REQ|<enum><br>POS|Type of<br>metadata<br>to be<br>searched||
|DeviceIDLis<br>t|REQ|<csv>|POS ID list||
|Overlapped<br>ID|REQ|<int>|Overlapped<br>number||
|Keyword|REQ|<string>|Search<br>keyword||
|IsWholeWo<br>rd|REQ|<bool><br>True, False|To match<br>whole word<br>or not for<br>search||
|IsCaseSensi<br>tive|REQ|<bool><br>True, False|Whether<br>search is<br>case-<br>sensitive or<br>not||
|FromDate|REQ|<string><br>UTCFormat<br>=YYYY-MM-<br>DDTHH:MM<br>:SSZ|From date<br>of the<br>search||



SUNAPI 85


|Action|Parameters|Request/<br>Response|Type/<br>Value|Description|
|---|---|---|---|---|
|ToDate|REQ|<string><br>UTCFormat<br>=YYYY-MM-<br>DDTHH:MM<br>:SSZ|To date of<br>search||

### **17.4. Examples**

#### **17.4.1. Start search for POS data**

**Request without any filters**


REQUEST

```
 http://<Device IP>/stw
```





```
 cgi/recording.cgi?msubmenu=metadata&action=control&Mode=Start&MetadataType=P
 OS&FromDate=2016-07-13T00:00:00Z&ToDate=2016-07-16T23:59:59Z

```

**Request with Overlapped ID**


REQUEST

```
 http://<Device IP>/stw cgi/recording.cgi?msubmenu=metadata&action=control&Mode=Start&MetadataType=P
 OS&FromDate=2016-07-15T00:00:00Z&ToDate=2016-07-16T23:59:59Z&OverlappedID=11

```

**Request with Overlapped ID and Single Keyword**


REQUEST

```
 http://<Device IP>/stw cgi/recording.cgi?msubmenu=metadata&action=control&Mode=Start&MetadataType=P
 OS&FromDate=2016-07-15T00:00:00Z&ToDate=2016-07 16T23:59:59Z&OverlappedID=11&Keyword=Apple

```

**Request with Overlapped ID and Keyword Green or Apple**


REQUEST

```
 http://<Device IP>/stw cgi/recording.cgi?msubmenu=metadata&action=control&Mode=Start&MetadataType=P
 OS&FromDate=2016-07-15T00:00:00Z&ToDate=2016-07
```

86 Recording


```
 16T23:59:59Z&OverlappedID=11&IsWholeWord=false&Keyword=Green%20Apple

```

**Request with Overlapped ID and Keyword "Green,Apple"sss**


REQUEST

```
 http://<Device IP>/stw cgi/recording.cgi?msubmenu=metadata&action=control&Mode=Start&MetadataType=P
 OS&FromDate=2016-07-15T00:00:00Z&ToDate=2016-07 16T23:59:59Z&OverlappedID=11&Keyword=Green,Apple

```

**Request with Overlapped ID, Keyword and IsCaseSensitive**


REQUEST

```
 http://<Device IP>/stw cgi/recording.cgi?msubmenu=metadata&action=control&Mode=Start&MetadataType=P
 OS&FromDate=2016-07-15T00:00:00Z&ToDate=2016-07 16T23:59:59Z&OverlappedID=11&Keyword=APPLE&IsCaseSensitive=true

```

**Request with Overlapped ID, Keyword, IsCaseSensitive and Single DeviceID**


REQUEST

```
 http://<Device IP>/stw cgi/recording.cgi?msubmenu=metadata&action=control&Mode=Start&MetadataType=P
 OS&FromDate=2016-07-15T00:00:00Z&ToDate=2016-07 16T23:59:59Z&OverlappedID=11&Keyword=OKRA&IsCaseSensitive=true&DeviceIDList=
 0

```

**Request with Overlapped ID, Keyword, IsCaseSensitive and Multiple DeviceIDs**


REQUEST

```
 http://<Device IP>/stw cgi/recording.cgi?msubmenu=metadata&action=control&Mode=Start&MetadataType=P
 OS&FromDate=2016-07-15T00:00:00Z&ToDate=2016-07 16T23:59:59Z&OverlappedID=11&Keyword=OKRA&IsCaseSensitive=true&DeviceIDList=
 1,2

```

TEXT RESPONSE

```
 HTTP/1.0 200 OK

```

SUNAPI 87


```
 Content-type: text/plain
 <Body>

 SearchToken=7475

```

JSON RESPONSE

```
 HTTP/1.0 200 OK
 Content-type: application/json
 <Body>

 {
 "SearchToken": "7475"
 }

#### **17.4.2. Cancel Search**
```

REQUEST

```
 http://<Device IP>/stw cgi/recording.cgi?msubmenu=metadata&action=control&Mode=Cancel&SearchToken=7
 475

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

```

88 Recording


```
 "Response": "Success"
 }

#### **17.4.3. To get search status**
```

REQUEST

```
 http://<Device-IP>/stw cgi/recording.cgi?msubmenu=metadata&action=view&Type=Status&SearchToken=7475

```

TEXT RESPONSE

```
 HTTP/1.0 200 OK
 Content-type: text/plain
 <Body>

 Status=Completed

```

JSON RESPONSE

```
 HTTP/1.0 200 OK
 Content-type: application/json
 <Body>

 {
 "Status": "Completed"
 }

#### **17.4.4. To renew search token (For 1 minute)**
```

REQUEST

```
 http://<Device-IP>/stw cgi/recording.cgi?msubmenu=metadata&action=control&Mode=Renew&SearchToken=74
 75

```

TEXT RESPONSE

```
 HTTP/1.0 200 OK
 Content-type: text/plain

```

SUNAPI 89


```
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

#### **17.4.5. To get the results of search (First 100 results)**
```

REQUEST

```
 http://<Device-IP>/stw cgi/recording.cgi?msubmenu=metadata&action=view&Type=Results&ResultFromIndex
 =1&MaxResults=100&SearchToken=6619

```

TEXT RESPONSE

```
 HTTP/1.0 200 OK
 Content-type: text/plain
 <Body>

 SearchTokenExpiryTime=2016-07-19T07:22:47Z
 TotalResultsFound=399
 TotalCount=100

 Result.1.DeviceID=1
 Result.1.Date=2016-07-18T07:28:01Z
 Result.1.ChannelIDList=0,1,2,3,4,5,6,7
 Result.1.KeywordsMatched=
 Result.1.TextData=
 02-06-16 2:43P
 OKRA 5.00

```

90 Recording


```
 OIL 9.50
 LEMON 2.50
 GREEN BANANNAS 3.00
 YELLOW BANANNAS 3.00

 SUBTOTAL 23.00
 TAX 02.70
 TOTAL 25.70
 CASH 30.00
 CHANGE 04.30

 Result.2.DeviceID=2
 Result.2.Date=2016-07-18T07:28:00Z
 Result.2.ChannelIDList=8,9,10,11,12,13,14,15
 Result.2.KeywordsMatched=
 Result.2.TextData=
 03-06-16 2:43P
 APPLE 9.00
 BERRY 3.50
 MELON 10.50
 PLUM 3.00

 SUBTOTAL 26.00
 TAX 03.00
 TOTAL 29.00
 CASH 30.00
 CHANGE 01.00

 Result.3.DeviceID=1
 Result.3.Date=2016-07-18T07:27:56Z
 Result.3.ChannelIDList=0,1,2,3,4,5,6,7
 Result.3.KeywordsMatched=
 Result.3.TextData=
 02-06-16 2:43P
 OKRA 5.00
 OIL 9.50
 LEMON 2.50
 GREEN BANANNAS 3.00
 YELLOW BANANNAS 3.00

```

SUNAPI 91


JSON RESPONSE

```
 HTTP/1.0 200 OK
 Content-type: application/json
 <Body>

 {
 "SearchTokenExpiryTime": "2016-07-19T07:22:47Z",
 "ToralResultsFound": 399,
 "TotalCount": 100,
 "MetaDataSearchResults": [
 {
 "Result": 1,
 "DeviceID": 2,
 "Date": "2016-07-18T07:22:47Z",
 "ChannelIDList": [
 8,
 9,
 10,
 11,
 12,
 13,
 14,
 15
 ],
 "KeywordsMatched": [],
 "TextData": "\r\n03-06-16 2:43P\r\nAPPLE \t\t9.00\r\nBERRY\t
 \t3.50\r\nMELON \t\t10.50\r\nPLUM\t \t3.00\r\n\r\nSUBTOTAL \t26.00\r\nTAX
 \t\t03.00\r\nTOTAL \t\t29.00\r\nCASH \t\t30.00\r\nCHANGE \t\t01.00\r\n"
 },
 {
 "Result": 2,
 "DeviceID": 1,
 "Date": "2016-07-18T07:22:47Z",
 "ChannelIDList": [
 0,
 1,
 2,
 3,
 4,
 5,

```

92 Recording


```
 6,
 7
 ],
 "KeywordsMatched": [],
 "TextData": "\r\n02-06-16 2:43P\r\nOKRA \t\t5.00\r\nOIL\t
 \t9.50\r\nLEMON \t\t2.50\r\nGREEN BANANNAS\t3.00\r\nYELLOW
 BANANNAS\t3.00\r\n\r\n\r\nSUBTOTAL \t23.00\r\nTAX \t\t02.70\r\nTOTAL
 \t\t25.70\r\nCASH \t\t30.00\r\nCHANGE \t\t04.30\r\n"
 },
 {
 "Result": 3,
 "DeviceID": 2,
 "Date": "2016-07-18T07:22:43Z",
 "ChannelIDList": [
 8,
 9,
 10,
 11,
 12,
 13,
 14,
 15
 ],
 "KeywordsMatched": [],
 "TextData": "\r\n03-06-16 2:43P\r\nAPPLE \t\t9.00\r\nBERRY\t
 \t3.50\r\nMELON \t\t10.50\r\nPLUM\t \t3.00\r\n\r\nSUBTOTAL \t26.00\r\nTAX
 \t\t03.00\r\nTOTAL \t\t29.00\r\nCASH \t\t30.00\r\nCHANGE \t\t01.00\r\n"
 }
 ]
 }

#### **17.4.6. To get the results of search (Next 100 results)**
```

REQUEST

```
 http://<Device-IP>/stw cgi/recording.cgi?msubmenu=metadata&action=view&Type=Results&ResultFromIndex
 =101&MaxResults=100&SearchToken=6619

```

SUNAPI 93


## **Chapter 18. Smart Search**
### **18.1. Description**

The **smartsearch** submenu is used to search video analytics information for a given search criteria.


This chapter applies to NVR only.

Attribute to check for Feature Support in NVR for each channel:

"attributes.cgi/attributes/recording/Support/1/SmartSearch"

Attribute to check for maximum number of include areas supported in NVR:



**NOTE**


**Access level**



"attributes/recording/Limit/MaxSmartSearchIncludeAreas"

Attribute to check for maximum number of exclude areas supported in NVR:

"attributes/recording/Limit/MaxSmartSearchExcludeAreas"

Attribute to check for maximum number of lines supported in NVR:

"attributes/recording/Limit/MaxSmartSearchlines"



|Action|NVR|
|---|---|
|view|User|
|control|User|

### **18.2. Syntax**

```
 http://<Device IP>/stw-cgi/recording.cgi?msubmenu=
 smartsearch &action=<value>[&<parameter>=<value>]

### **18.3. Parameters**

```



















|Action|Parameters|Request/<br>Response|Type/<br>Value|Description|
|---|---|---|---|---|
|view|Type|REQ|<enum><br>Results,<br>Status|Search Type|
||SearchToken|REQ|<sring>|Search session token|
||TotalCount|RES|<int>|Result count|
||TimedOut|RES|<bool><br>True, False|Asynchronous search timeout.|
||Channel.#.Result.#.Event<br>Time|RES|<string>|Time at which event happened|



94 Recording


|Action|Parameters|Request/<br>Response|Type/<br>Value|Description|
|---|---|---|---|---|
||Channel.#.Result.#.Event<br>Type|RES|<enum><br>Motion,<br>Enter, Exit,<br>Pass|Type of event|
||Status|RES|<enum><br>Completed,<br>NotComple<br>ted|Search status<br>This parameter is returned only when<br>Type is set to Status in the request.|
|control|Mode|REQ|<enum><br>Start,<br>Cancel,<br>Renew,<br>Stop|Search mode|
||OverlappedID|REQ|<int>|Overlapped ID number|
||Channel|REQ|<int>|Channel ID|
||FromDate|REQ|<string>|From date of the search|
||ToDate|REQ|<string>|To date of search|
||Area.#.EventType|REQ|<csv><br>Motion,<br>Enter, Exit|Type of area event|
||Line.#.EventType|REQ|<enum><br>BothDirecti<br>ons, Right,<br>Left|Type of line event|
||Area.#.Type|REQ|<enum><br>Inside,<br>Outside|Area type|
||Area.#.Coordinates|REQ|<string><br>Format=x1,<br>y1,x2,y2||
|Area.#.Filte<br>r|REQ|<enum>+<br>Person,<br>Vehicle,<br>Unknown<br>Object filter|Coordinate<br>s of the<br>area||



SUNAPI 95


|Action|Parameters|Request/<br>Response|Type/<br>Value|Description|
|---|---|---|---|---|
|Line.#.Coor<br>dinates|REQ|<string><br>Format=x1,<br>y1,x2,y2|Coordinate<br>s of the line||


### **18.4. Examples**

#### **18.4.1. Start smart search for selected area**

Request without any filters


REQUEST

```
 http://<Device IP>/stw cgi/recording.cgi?msubmenu=smartsearch&action=control&Mode=Start&channel=5&F
 romDate=2016-06-15T00:00:00Z&ToDate=2016-06 15T23:59:59Z&Area.1.EventType=Motion,Enter,Exit&Area.1.Type=Inside&Area.1.Co
 ordinates=-0.903226,0.870504,-0.903226,-0.877698,0.903226, 0.877698,0.903226,0.870504

```

TEXT RESPONSE

```
 HTTP/1.0 200 OK
 Content-type: text/plain
 <Body>

 SearchToken=4174

```

JSON RESPONSE

```
 HTTP/1.0 200 OK
 Content-type: application/json
 <Body>

 {
 "SearchToken": "4174"
 }

```

96 Recording


#### **18.4.2. Check the status of smart search**

REQUEST

```
 http://<Device IP>/stw cgi/recording.cgi?msubmenu=smartsearch&action=view&Type=Status&SearchToken=4
 174

```

TEXT RESPONSE

```
 HTTP/1.0 200 OK
 Content-type: text/plain
 <Body>

 Status=Completed

```

JSON RESPONSE

```
 HTTP/1.0 200 OK
 Content-type: application/json
 <Body>

 {
 "Status": "Completed"
 }

#### **18.4.3. To get results of smart search**
```

REQUEST

```
 http://<Device IP>/stw cgi/recording.cgi?msubmenu=smartsearch&action=view&Type=Results&SearchToken=
 4174

```

TEXT RESPONSE

```
 HTTP/1.0 200 OK
 Content-type: text/plain
 <Body>

```

SUNAPI 97


```
 TotalCount=5
 Channel.5.Result.1.EventTime=2016-06-15T00:08:35Z
 Channel.5.Result.1.EventType=Motion
 Channel.5.Result.2.EventTime=2016-06-15T00:32:34Z
 Channel.5.Result.2.EventType=Motion
 Channel.5.Result.3.EventTime=2016-06-15T00:32:35Z
 Channel.5.Result.3.EventType=Motion
 Channel.5.Result.4.EventTime=2016-06-15T01:32:02Z
 Channel.5.Result.4.EventType=Motion
 Channel.5.Result.5.EventTime=2016-06-15T01:32:03Z
 Channel.5.Result.5.EventType=Motion

```

JSON RESPONSE

```
 HTTP/1.0 200 OK
 Content-type: application/json
 <Body>

 {
 "TotalCount": 5,
 "SmartSearchResults": [
 {
 "Channel": 5,
 "Results": [
 {
 "Result": 1,
 "EventTime": "2016-06-15T00:08:35Z",
 "EventType": "Motion"
 },
 {
 "Result": 2,
 "EventTime": "2016-06-15T00:32:34Z",
 "EventType": "Motion"
 },
 {
 "Result": 3,
 "EventTime": "2016-06-15T00:32:35Z",
 "EventType": "Motion"
 },
 {

```

98 Recording


```
 "Result": 4,
 "EventTime": "2016-06-15T01:32:02Z",
 "EventType": "Motion"
 },
 {
 "Result": 5,
 "EventTime": "2016-06-15T01:32:03Z",
 "EventType": "Motion"
 }
 ]
 }
 ]
 }

#### **18.4.4. Start Smart search for the lines**
```

REQUEST

```
 http://<Device IP>/stw cgi/recording.cgi?msubmenu=smartsearch&action=control&Mode=Start&channel=5&F
 romDate=2016-06-15T00:00:00Z&ToDate=2016-06 15T23:59:59Z&Line.1.EventType=Right&Line.1.Coordinates= 0.903226,0.870504,0.903226,0.870504

```

SUNAPI 99


## **Chapter 19. Queue Search**
### **19.1. Description**

The **queuesearch** submenu provides statistical analysis and measurement of average dwell time and

number of people in queues based on a given search criteria.


This chapter applies to camera only.



**NOTE**


**Access level**



Attribute to check for Feature Support: "Recording/Support/QueueManagement"

Attribute to check for Max Queues Supported: "Eventsource/Limit/MaxQueues"



|Action|Camera|
|---|---|
|view|Admin|
|control|Admin|

### **19.2. Syntax**

```
 http://<Device IP>/stw-cgi/recording.cgi?msubmenu=
 queuesearch &action=<value>[&<parameter>=<value>]

### **19.3. Parameters**

```















|Action|Parameters|Request/<br>Response|Type/<br>Value|Description|
|---|---|---|---|---|
|view|Type|REQ|<enum><br>Results,<br>Status|Type<br>If**Type** is set to Results or Status, the<br>**view** action must be sent together<br>with**SearchToken**.|
||SearchToken|REQ|<string>|Search token|
||ResultInterval|RES|<enum><br>Hourly,<br>Daily,<br>Weekly,<br>Monthly|Search result interval|



100 Recording


|Action|Parameters|Request/<br>Response|Type/<br>Value|Description|
|---|---|---|---|---|
||Queue.#.AveragePeople<br>Result|RES|<csv>|Queue Search Average People Results.<br>If**ResultInterval** is Hourly, search<br>results are returned in terms of hours<br>and the number of results is fixed, i.e.<br>24. Here, the first result in the array<br>represents the 0<br>th hour of the day, and<br>the last result in the array represents<br>the 23<br>rd hour of the day.<br>If**ResultInterval** is Daily, search<br>results are returned in terms of days<br>and the first result in the array<br>represents the first day of the month<br>while the last result in the array<br>represents the last day of the month.<br>If**ResultInterval** is Weekly, search<br>results are returned in terms of<br>weeks.<br>If**ResultInterval** is Monthly, search<br>results are returned in terms of<br>months and the first result in the<br>array represents the first month of the<br>year, while the last result in the array<br>represents the last month of the year.<br>**Note**<br>**ResultInterval** is fixed by the<br>camera based on**FromDate** and<br>**ToDate** of the search|


SUNAPI 101


|Action|Parameters|Request/<br>Response|Type/<br>Value|Description|
|---|---|---|---|---|
||Queue.#.Level.#.Cumulat<br>iveTimeResult|RES|<csv>|Queue Search Cumulative Time Result<br>If**ResultInterval** is Hourly, search<br>results are returned in terms of hours<br>and the number of results is fixed, i.e.<br>24. Here, the first result in the array<br>represents the 0<br>th hour of the day, and<br>the last result in the array represents<br>the 23<br>rd hour of the day.<br>If**ResultInterval** is Daily, search<br>results are returned in terms of days<br>and the first result in the array<br>represents the first day of the month<br>while the last result in the array<br>represents the last day of the month.<br>If**ResultInterval** is Weekly, search<br>results are returned in terms of<br>weeks.<br>If**ResultInterval** is Monthly, search<br>results are returned in terms of<br>months and the first result in the<br>array represents the first month of the<br>year, while the last result in the array<br>represents the last month of the year.<br>**Note**<br>**ResultInterval** is fixed by the<br>camera based on**FromDate** and<br>**ToDate** of the search|
||Status|RES|<enum><br>Completed,<br>NotComple<br>ted|Search status<br>**Status** is valid only when**Type** is set<br>to Status.|
|control|Mode|REQ|<enum><br>Start,<br>Cancel|Mode|
||Channel|REQ|<int>|Channel ID|


102 Recording


|Action|Parameters|Request/<br>Response|Type/<br>Value|Description|
|---|---|---|---|---|
||FromDate|REQ|<string><br><format=YY<br>YY-MM-<br>DDTHH:MM<br>:SSZ>|The start date and time for search|
||ToDate|REQ|<string><br><format=YY<br>YY-MM-<br>DDTHH:MM<br>:SSZ>|The end date and time for search|
||SearchToken|REQ, RES|<string>|Search token<br>**SearchToken** is a request-only<br>parameter when**Mode** is set to<br>Cancel, but it will return data when<br>**Mode** is set to Start.|
||Queue.#.AveragePeople|REQ|<bool><br>True, False|Enables or disables Queue Average<br>People search|
||Queue.#.Level.#.Cumulat<br>iveTime|REQ|<bool><br>True, False|Enables or disables Queue Cumulative<br>Time search|

### **19.4. Examples**

#### **19.4.1. Queue Search**







**Queue search for average people result**


REQUEST

```
 http://<Device IP>/stw cgi/recording.cgi?msubmenu=queuesearch&action=control&Channel=0&Mode=Start&F
 romDate=2017-01-17T00:00:00Z&ToDate=2017-01 17T23:59:59Z&Queue.1.AveragePeople=True&Queue.2.AveragePeople=True&Queue.3.A
 veragePeople=True

```

JSON RESPONSE

```
 HTTP/1.0 200 OK
 Content-type: application/json
 <Body>

```

SUNAPI 103


```
 {
 "SearchToken": "QueueManagement-2017-09-15T04:3"
 }

```

**Queue search for cumulative time result**


REQUEST

```
 http://<Device IP>/stw cgi/recording.cgi?msubmenu=queuesearch&action=control&Channel=0&Mode=Start&F
 romDate=2017-01-17T00:00:00Z&ToDate=2017-01 17T23:59:59Z&Queue.1.Level.High.CumulativeTime=True&Queue.1.Level.Medium.Cum
 ulativeTime=True&Queue.2.Level.High.CumulativeTime=True&Queue.2.Level.Medium
 .CumulativeTime=True&Queue.3.Level.High.CumulativeTime=True&Queue.3.Level.Me
 dium.CumulativeTime=True

```

JSON RESPONSE

```
 HTTP/1.0 200 OK
 Content-type: application/json
 <Body>

 {
 "SearchToken": "QueueManagement-2017-09-15T04:4"
 }

```

**Queue search for average people and cumulative time result**


REQUEST

```
 http://<Device IP>/stw cgi/recording.cgi?msubmenu=queuesearch&action=control&Channel=0&Mode=Start&F
 romDate=2017-01-17T00:00:00Z&ToDate=2017-01 17T23:59:59Z&Queue.1.AveragePeople=True&Queue.2.AveragePeople=True&Queue.3.A
 veragePeople=True&Queue.1.Level.High.CumulativeTime=True&Queue.1.Level.Mediu
 m.CumulativeTime=True&Queue.2.Level.High.CumulativeTime=True&Queue.2.Level.M
 edium.CumulativeTime=True&Queue.3.Level.High.CumulativeTime=True&Queue.3.Lev
 el.Medium.CumulativeTime=True

```

104 Recording


JSON RESPONSE

```
 HTTP/1.0 200 OK
 Content-type: application/json
 <Body>

 {
 "SearchToken": "QueueManagement-2017-09-15T04:5"
 }

#### **19.4.2. Getting the status of Queue search**
```

**Type** must be set to Status, and **SearchToken** must be sent with **view** action.


REQUEST

```
 http://<Device IP>/stw cgi/recording.cgi?msubmenu=queuesearch&action=view&Type=Status&SearchToken=Q
 ueueManagement-2017-09-15T04:4

```

JSON RESPONSE

```
 HTTP/1.0 200 OK
 Content-type: application/json
 <Body>

 {
 "Status": "Completed"
 }

#### **19.4.3. Getting Queue search result**
```

**Type** must be set to Results, and **SearchToken** must be sent with **view** action.


**Getting Average People search result**


REQUEST

```
 http://<Device IP>/ stw cgi/recording.cgi?msubmenu=queuesearch&action=view&Type=Results&SearchToken=
 QueueManagement-2017-09-15T04:3

```

SUNAPI 105


JSON RESPONSE

```
 HTTP/1.0 200 OK
 Content-type: application/json
 <Body>

 {
 "ResultInterval": "Hourly",
 "QueueResults": [
 {
 "Queue": 1,
 "AveragePeopleResult": [
 "0",
 "1",
 "2",
 "3",
 "4",
 "5",
 "6",
 "7",
 "8",
 "9",
 "10",
 "11",
 "12",
 "13",
 "14",
 "15",
 "16",
 "17",
 "18",
 "19",
 "20",
 "21",
 "22",
 "23"
 ]
 },
 {
 "Queue": 2,
 "AveragePeopleResult": [

```

106 Recording


```
 "0",
 "1",
 "2",
 "3",
 "4",
 "5",
 "6",
 "7",
 "8",
 "9",
 "10",
 "11",
 "12",
 "13",
 "14",
 "15",
 "16",
 "17",
 "18",
 "19",
 "20",
 "21",
 "22",
 "23"
 ]
 },
 {
 "Queue": 3,
 "AveragePeopleResult": [
 "0",
 "1",
 "2",
 "3",
 "4",
 "5",
 "6",
 "7",
 "8",
 "9",
 "10",
 "11",

```

SUNAPI 107


```
 "12",
 "13",
 "14",
 "15",
 "16",
 "17",
 "18",
 "19",
 "20",
 "21",
 "22",
 "23"
 ]
 }
 ]
 }

```

**Getting Cumulative Time search result**


REQUEST

```
 http://<Device IP>/ stw cgi/recording.cgi?msubmenu=queuesearch&action=view&Type=Results&SearchToken=
 QueueManagement-2017-09-15T04:4

```

JSON RESPONSE

```
 HTTP/1.0 200 OK
 Content-type: application/json
 <Body>

 {
 "ResultInterval": "Hourly",
 "QueueResults": [
 {
 "Queue": 1,
 "QueueLevels": [
 {
 "Level": "High",
 "CumulativeTimeResult": [
 "0", "1", "2", "3", "4", "5", "6", "7", "8", "9",

```

108 Recording


```
 "10", "11", "12",
 "13", "14", "15", "16", "17", "18", "19", "20",
 "21", "22", "23"
 ]
 },
 {
 "Level": "Medium",
 "CumulativeTimeResult": [
 "0", "1", "2", "3", "4", "5", "6", "7", "8", "9",
 "10", "11", "12",
 "13", "14", "15", "16", "17", "18", "19", "20",
 "21", "22", "23"
 ]
 }
 ]
 },
 {
 "Queue": 2,
 "QueueLevels": [
 {
 "Level": "High",
 "CumulativeTimeResult": [
 "0", "1", "2", "3", "4", "5", "6", "7", "8", "9",
 "10", "11", "12",
 "13", "14", "15", "16", "17", "18", "19", "20",
 "21", "22", "23"
 ]
 },
 {
 "Level": "Medium",
 "CumulativeTimeResult": [
 "0", "1", "2", "3", "4", "5", "6", "7", "8", "9",
 "10", "11", "12",
 "13", "14", "15", "16", "17", "18", "19", "20",
 "21", "22", "23"
 ]
 }
 ]
 },
 {
 "Queue": 3,

```

SUNAPI 109


```
 "QueueLevels": [
 {
 "Level": "High",
 "CumulativeTimeResult": [
 "0", "1", "2", "3", "4", "5", "6", "7", "8", "9",
 "10", "11", "12",
 "13", "14", "15", "16", "17", "18", "19", "20",
 "21", "22", "23"
 ]
 },
 {
 "Level": "Medium",
 "CumulativeTimeResult": [
 "0", "1", "2", "3", "4", "5", "6", "7", "8", "9",
 "10", "11", "12",
 "13", "14", "15", "16", "17", "18", "19", "20",
 "21", "22", "23"
 ]
 }
 ]
 }
 ]
 }

```

**Getting Average People and Cumulative Time search result**


REQUEST

```
 http://<Device IP>/ stw cgi/recording.cgi?msubmenu=queuesearch&action=view&Type=Results&SearchToken=
 QueueManagement-2017-09-15T04:5

```

JSON RESPONSE

```
 HTTP/1.0 200 OK
 Content-type: application/json
 <Body>

 {
 "ResultInterval": "Hourly",
 "QueueResults": [

```

110 Recording


```
 {
 "Queue": 1,
 "AveragePeopleResult": [
 "0", "1", "2", "3", "4", "5", "6", "7", "8", "9", "10",
 "11", "12",
 "13", "14", "15", "16", "17", "18", "19", "20", "21", "22",
 "23"
 ],
 "QueueLevels": [
 {
 "Level": "High",
 "CumulativeTimeResult": [
 "0", "1", "2", "3", "4", "5", "6", "7", "8", "9",
 "10", "11", "12",
 "13", "14", "15", "16", "17", "18", "19", "20",
 "21", "22", "23"
 ]
 },
 {
 "Level": "Medium",
 "CumulativeTimeResult": [
 "0", "1", "2", "3", "4", "5", "6", "7", "8", "9",
 "10", "11", "12",
 "13", "14", "15", "16", "17", "18", "19", "20",
 "21", "22", "23"
 ]
 }
 ]
 },
 {
 "Queue": 2,
 "AveragePeopleResult": [
 "0", "1", "2", "3", "4", "5", "6", "7", "8", "9", "10",
 "11", "12",
 "13", "14", "15", "16", "17", "18", "19", "20", "21", "22",
 "23"
 ],
 "QueueLevels": [
 {
 "Level": "High",
 "CumulativeTimeResult": [

```

SUNAPI 111


```
 "0", "1", "2", "3", "4", "5", "6", "7", "8", "9",
 "10", "11", "12",
 "13", "14", "15", "16", "17", "18", "19", "20",
 "21", "22", "23"
 ]
 },
 {
 "Level": "Medium",
 "CumulativeTimeResult": [
 "0", "1", "2", "3", "4", "5", "6", "7", "8", "9",
 "10", "11", "12",
 "13", "14", "15", "16", "17", "18", "19", "20",
 "21", "22", "23"
 ]
 }
 ]
 },
 {
 "Queue": 3,
 "AveragePeopleResult": [
 "0", "1", "2", "3", "4", "5", "6", "7", "8", "9", "10",
 "11", "12",
 "13", "14", "15", "16", "17", "18", "19", "20", "21", "22",
 "23"
 ],
 "QueueLevels": [
 {
 "Level": "High",
 "CumulativeTimeResult": [
 "0", "1", "2", "3", "4", "5", "6", "7", "8", "9",
 "10", "11", "12",
 "13", "14", "15", "16", "17", "18", "19", "20",
 "21", "22", "23"
 ]
 },
 {
 "Level": "Medium",
 "CumulativeTimeResult": [
 "0", "1", "2", "3", "4", "5", "6", "7", "8", "9",
 "10", "11", "12",
 "13", "14", "15", "16", "17", "18", "19", "20",

```

112 Recording


```
 "21", "22", "23"
 ]
 }
 ]
 }
 ]
 }

#### **19.4.4. Cancelling Queue search**
```

REQUEST

```
 http://<Device IP>/stw-cgi/recording.cgi?msubmenu=queuesearch
 &action=control&Mode=Cancel&SearchToken=QueueManagement-2017-09-15T04:3

```

SUNAPI 113


## **Chapter 20. Disk Utility**
### **20.1. Description**

The **diskutility** submenu gets the details of HDD array from NVR


**NOTE** This submenu is only available for NVR


**Access level**

|Action|NVR|
|---|---|
|view|User|


### **20.2. Syntax**

```
 http://<Device IP>/stw-cgi/recording.cgi?msubmenu=
 diskutility &action=<value>[&<parameter>=<value>]

### **20.3. Parameters**

```








|Action|Parameters|Request/<br>Response|Type/<br>Value|Description|
|---|---|---|---|---|
|view|Index|REQ|<int>|Disk index|
||Disk.#.Index|RES|<int>|Disk index|
||Disk.#.Name|RES|<string>|Disk model name|
||Disk.#.SMART|RES|<string>|Smart HDD details|

### **20.4. Examples**

#### **20.4.1. Getting the disk information**

REQUEST

```
 http://<Device IP>/stw-cgi/recording.cgi?msubmenu=diskutility&action=view

```

TEXT RESPONSE

```
 HTTP/1.0 200 OK
 Content-type: text/plain
 <Body>

```

114 Recording


```
 Disk.0.Index=14
 Disk.0.Name=ST1000VM002-1CT162
 Disk.1.Index=15
 Disk.1.Name=WDC WD60PURX-64T0ZY1
 Disk.2.Index=16
 Disk.2.Name=WDC WD40PURX-64N96Y0

```

JSON RESPONSE

```
 HTTP/1.0 200 OK
 Content-type: application/json
 <Body>

 {
 "Disks": [
 {
 "Index": 14,
 "Name": "ST1000VM002-1CT162 "
 },
 {
 "Index": 15,
 "Name": "WDC WD60PURX-64T0ZY1 "
 },
 {
 "Index": 16,
 "Name": "WDC WD40PURX-64N96Y0 "
 }
 ]
 }

```

REQUEST

```
 http://<Device IP>/stw cgi/recording.cgi?msubmenu=diskutility&action=view&Index=14

```

TEXT RESPONSE

```
 HTTP/1.0 200 OK
 Content-type: text/plain

```

SUNAPI 115


```
 <Body>

 Enable=True
 Disk.0.Index=14
 Disk.0.Name=ST1000VM002-1CT162
 Disk.0.SMART=<html><body><h3 style="color:rgb(60,179,133);"> Status :
 GOOD</h3>
 <pre>Model Name : ST1000VM002-1CT162
 Serial : W1G0AJYW
 Firmware Version : SC23
 Capacity : 1 TB
 Temperature : 35&#8451; / 95&#8457;

 </pre><pre>ID Attribute Name Current Worst Threshhold RawValue Status
 001 Read Error Rate 117 099 006 000000057888 GOOD
 003 Spin-Up Time 098 097 000 000000000000 GOOD
 004 Start/Stop Count 096 096 020 000000004413 GOOD
 005 Reallocated Sectors 100 100 036 000000000000 GOOD
 007 Seek Error Rate 080 060 030 000000024466 GOOD
 009 Power-On Hours Count 076 076 000 000000021334 GOOD
 010 Spin Retry Count 100 100 097 000000000000 GOOD
 012 Power Cycle Count 099 099 020 000000001131 GOOD
 184 End-to-End error 100 100 099 000000000000 GOOD
 187 Reported Uncorrectable 088 088 000 000000000012 GOOD
 188 Command Timeout 100 099 000 000000000002 GOOD
 189 High Fly Writes 001 001 000 000000000363 GOOD
 190 Temperature Diff 065 051 045 000000000035 GOOD
 191 G-sense error rate 100 100 000 000000000000 GOOD
 192 Power-off retract 100 100 000 000000001125 GOOD
 193 Load/Unload cycle 098 098 000 000000004413 GOOD
 194 HDA temperature 035 049 000 000000000035 GOOD
 197 Current pending 100 100 000 000000000000 GOOD
 198 Offline scan wrong 100 100 000 000000000000 GOOD
 199 UDMA CRC error rate 200 200 000 000000000000 GOOD
 </pre></body></html>

```

JSON RESPONSE

```
 HTTP/1.0 200 OK
 Content-type: application/json

```

116 Recording


```
 <Body>

 {
 "Disks": [
 {
 "Index": 14,
 "Name": "ST1000VM002-1CT162 ",
 "SMART": "<html><body><h3 style=\"color:rgb(60,179,133);\">
 Status : GOOD</h3>\n<pre>Model Name : ST1000VM002-1CT162\nSerial :
 W1G0AJYW\nFirmware Version : SC23\nCapacity : 1 TB\nTemperature : 35&#8451;
 / 95&#8457; \n\n</pre><pre>ID Attribute Name Current Worst Threshhold
 RawValue Status\n001 Read Error Rate 117 099 006 000000057888 GOOD \n003
 Spin-Up Time 098 097 000 000000000000 GOOD \n004 Start/Stop Count 096 096
 020 000000004413 GOOD \n005 Reallocated Sectors 100 100 036 000000000000
 GOOD \n007 Seek Error Rate 080 060 030 000000024466 GOOD \n009 Power-On
 Hours Count 076 076 000 000000021334 GOOD \n010 Spin Retry Count 100 100 097
 000000000000 GOOD \n012 Power Cycle Count 099 099 020 000000001131 GOOD
 \n184 End-to-End error 100 100 099 000000000000 GOOD \n187 Reported
 Uncorrectable 088 088 000 000000000012 GOOD \n188 Command Timeout 100 099
 000 000000000002 GOOD \n189 High Fly Writes 001 001 000 000000000363 GOOD
 \n190 Temperature Diff 065 051 045 000000000035 GOOD \n191 G-sense error
 rate 100 100 000 000000000000 GOOD \n192 Power-off retract 100 100 000
 000000001125 GOOD \n193 Load/Unload cycle 098 098 000 000000004413 GOOD
 \n194 HDA temperature 035 049 000 000000000035 GOOD \n197 Current pending
 100 100 000 000000000000 GOOD \n198 Offline scan wrong 100 100 000
 000000000000 GOOD \n199 UDMA CRC error rate 200 200 000 000000000000 GOOD
 \n</pre></body></html>"
 }
 ]
 }

```

SUNAPI 117


## **Chapter 21. Bookmark**
### **21.1. Description**

The **bookmark** submenu can be used to bookmark a video clip in NVR.


**NOTE** This submenu is available only for NVR that supports System/Support/AIFeatures


**Access level**

|Action|NVR|
|---|---|
|view|User|
|add|User|
|update|User|
|remove|User|


### **21.2. Syntax**

```
 http://<Device IP>/stw-cgi/recording.cgi?msubmenu=
 bookmark &action=<value>[&<parameter>=<value>]

### **21.3. Parameters**

```








|Action|Parameters|Request/<br>Response|Type/<br>Value|Description|
|---|---|---|---|---|
|view|ChannelIDList|REQ|<csv>|Channel id list|
||FromDate|REQ|<string>|Time in UTC format<br>YYYY-MM-DDTHH:MM:SSZ|
||ToDate|REQ|<string>|Time in UTC format<br>YYYY-MM-DDTHH:MM:SSZ|
||OverlappedID|REQ|<int>|Overlapped id|
||TotalCount|RES|<int>|Total result count|
||Result.#.FromDate|RES|<string>|Time in UTC format<br>YYYY-MM-DDTHH:MM:SSZ|
||Result.#.ToDate|RES|<string>|Time in UTC format<br>YYYY-MM-DDTHH:MM:SSZ|


118 Recording


|Action|Parameters|Request/<br>Response|Type/<br>Value|Description|
|---|---|---|---|---|
||Result.#.ChannelIDLis<br>t|RES|<csv>|Channel id list|
||Result.#.Name|RES|<string>|Name of bookmark|
||Result.#.Category|RES|<enum><br>TIME, EVENT, SMART,<br>TEXT, AI_PERSON,<br>AI_FACE,<br>AI_FACE_RECOGNITIO<br>N, AI_VEHICLE|Bookmark category|
||Result.#.SubCategory|RES|<enum><br>AlarmInput,<br>MotionDetection,Vide<br>oloss, Passing,<br>Entering, Exiting,<br>Appearing,<br>Disappering,<br>Tampering,<br>FaceDetection,<br>Loitering, Tracking,<br>DefocusDetection,<br>FogDetection,<br>AudioDetection,<br>Scream, Gunshot,<br>Explosion, GlassBreak,<br>GSensorEvent,<br>EmergencyTrigger,<br>Intrusion|Subcategory of bookmark|
||Result.#.OverlappedI<br>D|RES|<int>|Recording overlapped id|
||Result.#.ObjectID|RES|<int>|Object ID|
||Result.#.BkID|RES|<string>|Unique bookmark ID (UUID)|
|add|FromDate|REQ|<sting>|Time in UTC format<br>YYYY-MM-DDTHH:MM:SSZ|
||ToDate|REQ|<string>|Time in UTC format<br>YYYY-MM-DDTHH:MM:SSZ|
||ChannelIDList|REQ|<csv>|Channel id list|
||ObjectID|REQ|<int>|Object ID|
||Name|REQ|<string>|Bookmark Name|


SUNAPI 119


|Action|Parameters|Request/<br>Response|Type/<br>Value|Description|
|---|---|---|---|---|
||Category|REQ|<enum><br>TIME, EVENT, SMART,<br>TEXT, AI_PERSON,<br>AI_FACE,<br>AI_FACE_RECOGNITIO<br>N, AI_VEHICLE|Bookmark category|
||OverlappedID|REQ|<int>|Recording overlapped id|
|update|BkID|REQ|<string>|Bookmark unique id (UUID)|
||Name|REQ|<string>|Bookmark name|
|remove|BkID|REQ|<string>|Unique bookmark id to be<br>removed|

### **21.4. Examples**

#### **21.4.1. Adding a bookmark**

REQUEST

```
 http://<Device IP>/stw cgi/recording.cgi?msubmenu=bookmark&action=add&FromDate=2020-04 12T09:00:00Z&ToDate=2020-04 13T09:03:00Z&ChannelIDList=0&Category=TIME&Name=TestBookMark&OverlappedID= 1&ObjectID=214

```

TEXT RESPONSE

```
 HTTP/1.0 200 OK
 Content-type: text/plain
 <Body>

 BkID=3757c60d27b8484cab29468d0c800a23

```

JSON RESPONSE

```
 HTTP/1.0 200 OK
 Content-type: application/json
 <Body>

```

120 Recording


```
 {
 "BkID": "3757c60d27b8484cab29468d0c800a23"
 }

#### **21.4.2. Removing a bookmark**
```

REQUEST

```
 http://<Device IP>/stw cgi/recording.cgi?msubmenu=bookmark&action=remove&BkID=3757c60d27b8484cab294
 68d0c800a23

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

#### **21.4.3. Updating a bookmark**
```

REQUEST

```
 http://<Device
 IP>/stwcgi/recording.cgi?msubmenu=bookmark&action=update&BkID=3757c60d27b848
 4cab29468d0c800a23&Name=TestBookMark2

```

SUNAPI 121


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

#### **21.4.4. Viewing a bookmark**
```

REQUEST

```
 http://<Device IP>/stw cgi/recording.cgi?msubmenu=bookmark&action=view&Category=TEXT

```

TEXT RESPONSE

```
 HTTP/1.0 200 OK
 Content-type: text/plain
 <Body>

 TotalResultsFound=1
 TotalCount=1

 Result.0.FromDate=2020-03-31T09:00:00Z
 Result.0.ToDate=2020-03-31T09:03:00Z
 Result.0.ChannelIDList=0
 Result.0.Name=TestBookMark
 Result.0.Category=TIME

```

122 Recording


```
 Result.0.SubCategory=
 Result.0.OverlappedID=100
 Result.0.ObjectID=0
 Result.0.BkID=3757c60d27b8484cab29468d0c800a23

```

JSON RESPONSE

```
 HTTP/1.0 200 OK
 Content-type: application/json
 <Body>

 {
 "TotalResultsFound": 1,
 "TotalCount": 1,
 "BookmarkResults": [
 {
 "Result": 0,
 "FromDate": "2020-03-31T09:00:00Z",
 "ToDate": "2020-03-31T09:03:00Z",
 "ChannelIDList": [
 "0"
 ],
 "Name": "TestBookMark",
 "Category": "TIME",
 "SubCategory": "",
 "OverlappedID": 100,
 "ObjectID": 0,
 "BkID": "3757c60d27b8484cab29468d0c800a23"
 }
 ]
 }

```

SUNAPI 123


## **Chapter 22. Event Search**
### **22.1. Description**

The **eventsearch** submenu used to search event information for a given time period.


This submenu is supported only in NVR.
**NOTE**

Attribute to check for Feature Support: "attributes/Recording/Support/SearchEvent"


**Access level**

|Action|NVR|
|---|---|
|view|User|
|control|User|


### **22.2. Syntax**

```
 http://<Device IP>/stw-cgi/recording.cgi?msubmenu=
 eventsearch &action=<value>[&<parameter>=<value>]

### **22.3. Parameters**

```










|Action|Parameters|Request/<br>Response|Type/<br>Value|Description|
|---|---|---|---|---|
|view|Type|REQ|<enum><br>Results,<br>Status|If Type is passed as**Status**, search<br>status is informed.<br>If Type is passed as**Result**, search<br>result is provided.|
||SearchToken|REQ|<string>|Search session token|
||ResultFromIndex|REQ|<int>|Index from which search results are<br>fetched|
||ResultFromTime|REQ|<string>|Time from which search results are<br>fetched.<br>Time in UTC format.<br>YYYY-MM-DDTHH:MM::SSZ|


124 Recording


|Action|Parameters|Request/<br>Response|Type/<br>Value|Description|
|---|---|---|---|---|
||ResultToTime|REQ|<string>|Time to which search results are<br>fetched.<br>Time in UTC format.<br>YYYY-MM-DDTHH:MM::SSZ|
||MaxResults|REQ|<int>|Maximum number of search results to<br>return|
||Status|RES|<enum><br>Completed,<br>NotComple<br>ted|Search status|
||TotalResultsFound|RES|<int>|Total results|
||TotalCount|RES|<int>|Total count of result|
||TimedOut|RES|<bool><br>True, False|Search timeout.|
||IntervalFrom|RES|<string>|Start time of search result.<br>Time in UTC format.<br>YYYY-MM-DDTHH:MM::SSZ|
||IntervalTo|RES|<string>|End time of search result.<br>Time in UTC format.<br>YYYY-MM-DDTHH:MM::SSZ|
||SearchTokenExpiryTime|RES|<string>|Time when the search token expires<br>Time in UTC format<br>YYYY-MM-DDTHH:MM:SSZ|
||Result.#.StartDateTime|RES|<string>|Time in UTC format<br>YYYY-MM-DDTHH:MM:SSZ|
||Result.#.EndDateTime|RES|<string>|Time in UTC format<br>YYYY-MM-DDTHH:MM:SSZ|
||Result.#.Channel|RES|<int>|Result channel ID|
||Result.#.OverlapId|RES|<int>|Recording overlapped id|


SUNAPI 125


|Action|Parameters|Request/<br>Response|Type/<br>Value|Description|
|---|---|---|---|---|
||Result.#.EventType|RES|<enum><br>Refer to<br>**Recording**<br>**Types** for<br>supported<br>values|EventType|
||Result.#.BkID|RES|<string>|Bookmark ID|
|control|Mode|REQ|<enum><br>Start,<br>Cancel,<br>Renew,<br>Stop|Used to start, cancel, renew or stop<br>search|
||FromDate|REQ|<string>|Time in UTC format<br>YYYY-MM-DDTHH:MM:SSZ|
||ToDate|REQ|<string>|Time in UTC format<br>YYYY-MM-DDTHH:MM:SSZ|
||ChannelIDList|REQ|<csv>|On which channel search has to be<br>performed|
||OverlappedID|REQ|<int>|Recording overlapped id|
||Type|REQ|<enum><br>Refer to<br>**Recording**<br>**Types** for<br>supported<br>values|Recording type to search<br>Common Types<br>• All: All video recordings including<br>normal and event recordings.<br>• Normal: Continuous video<br>recordings.<br>• Event: Video recording for all<br>events.|
||WaitTime|REQ|<int>|Timeout second.(Default:60 sec.)|


**Recording Types**


Type All, Normal, Event, AlarmInput, VideoAnalysis, MotionDetection,

NetworkDisconnect, FaceDetection, TamperingDetection, AudioDetection, Tracking,

Manual, UserInput, DefocusDetection, FogDetection, AudioAnalysis, QueueEvent,

videoloss, EmergencyTrigger, InternalHDDWarmup, GSensorEvent, ShockDetection,

TemperatureChangeDetection, BoxTemperatureDetection,

BodyTemperatureDetection, MaskDetection, CallRequest, TamperingSwitch,

DTMFReceived, ProximitySensor


126 Recording


Channel.#.Result.#.

Type



Normal, AlarmInput, VideoAnalysis, MotionDetection, NetworkDisconnect,

FaceDetection, TamperingDetection, AudioDetection, Tracking, ManualRecording,

UserInput, DefocusDetection, FogDetection, AudioAnalysis, ShockDetection,

TemperatureChangeDetection, BoxTemperatureDetection,

BodyTemperatureDetection, MaskDetection, CallRequest, TamperingSwitch,

DTMFReceived, ProximitySensor


### **22.4. Examples**

#### **22.4.1. Event search**

REQUEST

```
 http://<Device IP>/stw cgi/recording.cgi?msubmenu=eventSearch&action=control&Mode=Start&OverlappedI
 D=100&FromDate=2023-04-04T00:00:00Z&ToDate=2023-04 04T01:00:00Z&ChannelIDList=0

```

TEXT RESPONSE

```
 HTTP/1.0 200 OK
 Content-type: text/plain
 <Body>

 SearchToken=22775

```

JSON RESPONSE

```
 HTTP/1.0 200 OK
 Content-type: application/json
 <Body>

 {
 "SearchToken": "22775"
 }

#### **22.4.2. Viewing search result status**
```

REQUEST

```
 http://<Device IP>/stw cgi/recording.cgi?msubmenu=eventsearch&action=view&Type=Status&SearchToken=2

```

SUNAPI 127


```
 2775

```

TEXT RESPONSE

```
 HTTP/1.0 200 OK
 Content-type: text/plain
 <Body>

 SearchTokenExpiryTime=2023-04-04T01:36:35Z
 Status=Completed
 TotalResultsFound=0
 TotalCount=4
 TimedOut=False
 IntervalFrom=2023-04-04T00:01:54Z
 IntervalTo=2023-04-04T00:25:15Z

```

JSON RESPONSE

```
 HTTP/1.0 200 OK
 Content-type: application/json
 <Body>

 {
 "SearchTokenExpiryTime":  "2023-04-04T01:36:35Z",
 "Status":  "Completed",
 "TotalResultsFound":  0,
 "TotalCount":  4,
 "TimedOut": "False",
 "IntervalFrom": "2023-04-04T00:01:54Z",
 "IntervalTo":  "2023-04-04T00:25:15Z",
 "Results": []
 }

#### **22.4.3. Viewing search result**
```

REQUEST

```
 http://<Device IP>/stw cgi/recording.cgi?msubmenu=eventsearch&action=view&Type=Results&SearchToken=

```

128 Recording


```
 22775&ResultFromIndex=1&MaxResults=100

```

TEXT RESPONSE

```
 HTTP/1.0 200 OK
 Content-type: text/plain
 <Body>

 SearchTokenExpiryTime=2023-04-04T01:38:05Z
 Status=Completed
 TotalResultsFound=4
 TotalCount=4
 TimedOut=False
 Result.0.StartDateTime=2023-04-04T00:24:50Z
 Result.0.EndDateTime=2023-04-04T00:25:15Z
 Result.0.Channel=0
 Result.0.OverlapId=100
 Result.0.EventType=Normal
 Result.0.BkID=00000000000000000000000000000000
 ...
 Result.3.StartDateTime=2023-04-04T00:01:54Z
 Result.3.EndDateTime=2023-04-04T00:23:38Z
 Result.3.Channel=0
 Result.3.OverlapId=100
 Result.3.EventType=Normal
 Result.3.BkID=00000000000000000000000000000000

```

JSON RESPONSE

```
 HTTP/1.0 200 OK
 Content-type: application/json
 <Body>

 {
 "SearchTokenExpiryTime":  "2023-04-04T01:38:05Z",
 "Status":  "Completed",
 "TotalResultsFound":  4,
 "TotalCount":  4,
 "TimedOut": "False",
 "Results": [{

```

SUNAPI 129


```
 "Result":  0,
 "StartDateTime":  "2023-04-04T00:24:50Z",
 "EndDateTime": "2023-04-04T00:25:15Z",
 "Channel": 0,
 "OverlapId":  100,
 "EventType":  "Normal",
 "BkID": "00000000000000000000000000000000"
 },
 ...
 {
 "Result":  3,
 "StartDateTime":  "2023-04-04T00:01:54Z",
 "EndDateTime": "2023-04-04T00:23:38Z",
 "Channel": 0,
 "OverlapId":  100,
 "EventType":  "Normal",
 "BkID": "00000000000000000000000000000000"
 }]
 }

```

130 Recording


