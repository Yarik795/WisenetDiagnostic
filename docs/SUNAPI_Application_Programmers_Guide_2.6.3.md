# Application Programmer’s Guide


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

1. Introduction . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . 7

2. Discovery . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . 8

3. Password Encryption . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . 10

4. Setting the password in factory default state. . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . 12

4.1. To check if the camera password is initialized or not initialized . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . 12

4.2. Checking the Install Wizard state in NVR . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . 14

4.3. To set the initial password . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . 14

5. Basic Setup . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . 16

5.1. Attributes . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . 16

5.2. Device Information . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . 17

5.3. Date Information . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . 19

5.4. Event Session . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . 20

6. Live Stream Setup . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . 23

6.1. Get Video Sources . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . 23

6.2. Get Video Profiles . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . 24

6.3. Get Audio Inputs . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . 29

6.4. Get Audio Outputs . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . 29

6.5. Get Video Profile Policy . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . 30

6.6. Get Session Key . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . 31

6.7. Get Stream URI For Live . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . 32

7. Playback Setup. . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . 34

7.1. Get Storage Information . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . 34

7.2. Get Recording Setup . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . 35

7.3. Search Recording Period . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . 36

7.4. Calendar Search . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . 36

7.5. Get Overlapped IDs . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . 37

7.5.1. OverlapID - Behaviour of Camera . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . 37

7.5.2. OverlapID - Behaviour of NVR . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . 38

7.6. Timeline Search . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . 38

7.7. Get Stream URI for Playback . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . 39

8. PTZ Operation . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . 41

8.1. Continuous Move. . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . 41

8.2. Stop . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . 41

8.3. Preset. . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . 41

8.4. Identifying Capability . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . 42

8.4.1. Real PTZ . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . 42


2 Application Programmer’s Guide


8.4.2. Zoom Only . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . 42

8.4.3. PTRZ . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . 42

8.4.4. DPTZ . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . 43

8.4.5. External PTZ . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . 43

8.4.6. From SUNAPI 2.5.4 . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . 43

9. GPS Information . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . 44

10. RTSP. . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . 45

10.1. RTSP Live Session. . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . 45

10.2. RTSP Playback Session . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . 48

10.2.1. Rewind/Fast-Forward . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . 51

10.2.2. Slow Play . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . 52

10.3. Backup Session . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . 52

11. POS . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . 53

11.1. Capabilities . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . 53

11.2. Configuration Setup . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . 54

11.3. Event Setup. . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . 55

11.4. Live POS Data . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . 56

12. Metadata Search . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . 58

12.1. Capabilities . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . 58

12.2. Start Search . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . 59

12.3. Cancel Search . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . 61

12.4. Get Search Status. . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . 61

12.5. Renew Search Token . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . 61

12.6. Get Search Results. . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . 61

13. Bypass . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . 64

14. Queue management . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . 67

15. People Count . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . 92

16. Thermal Camera Integration. . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . 99

16.1. Attributes . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . 99

16.2. Color Palette Selection & Temperature Unit Selection . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . 99

16.2.1. View . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . 99

16.2.2. Set Operation . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . 100

16.3. Temperature Change Detection . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . 100

16.3.1. Attributes. . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . 100

16.4. Configuring Temperature Change Detection . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . 100

16.4.1. Options Command. . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . 100

16.4.2. Enable . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . 101

16.4.3. Set. . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . 101

16.4.4. View . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . 101

16.5. TemperatureChange Detection Event Format . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . 102


SUNAPI 3


16.6. Spot Temperature Reading . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . 103

16.7. BoxTemperatureDetection. . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . 103

16.7.1. Changing Box Temperature Detection Settings . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . 105

16.7.2. Removing Box Temperature Detection ROI Region 1 . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . 105

16.7.3. BoxTemperatureDetectionOptions . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . 106

16.7.4. Box Temperature Metadata Reading (Available only as Metadata). . . . . . . . . . . . . . . . . . . . . . . 107

16.7.5. Box temperature Event . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . 108

16.7.6. SUNAPI Event Status . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . 109

17. Dual Channel Thermal Camera Integration . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . 110

17.1. Overview . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . 110

17.1.1. Dual Channel. . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . 110

17.1.2. Thermal Image Position Calibration . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . 110

17.1.3. Thermal Detection Mode . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . 110

17.2. Estimated Body Temperature Detection . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . 110

17.2.1. Body Temperature Detection. . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . 110

17.2.2. Temperature Measurement Region Setting . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . 110

17.2.3. Improve Temperature Measurement Accuracy using blackbody device . . . . . . . . . . . . . . . . . . 110

17.2.4. Supported Events difference-based thermal detection mode . . . . . . . . . . . . . . . . . . . . . . . . . . . 111

17.3. Sample ONVIF Event for Body temperature detection . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . 111

17.4. BodyTemperatureDetection SUNAPI event status example. . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . 112

17.5. BodyTemperatureDetection SUNAPI schema-based event status example . . . . . . . . . . . . . . . . . . . 114

17.5.1. Getting event status schema of body temperature detection . . . . . . . . . . . . . . . . . . . . . . . . . . . 114

17.5.2. Getting scheme-based event status . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . 115

17.6. Metadata format for body temperature detection . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . 118

18. AI Camera Integration . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . 119

18.1. IVA Object Type Filter . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . 119

18.2. Line Rule . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . 119

18.2.1. Set operation . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . 119

18.2.2. View . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . 119

18.3. Area Rule. . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . 122

18.3.1. Set operation . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . 122

18.3.2. View . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . 122

18.4. Object Detection Submenu . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . 125

18.4.1. Set operation . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . 125

18.4.2. View operation . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . 125

18.5. Metaimagetransfer Submenu (BestShot Feature) . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . 126

18.5.1. View the current settings . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . 126

18.5.2. Set operation . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . 127

18.6. Digital Auto Tracking. . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . 127

18.6.1. View . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . 127


4 Application Programmer’s Guide


18.6.2. Set. . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . 128

18.7. EventStatus Check . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . 128

18.7.1. Object detection events . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . 128

18.8. SchemaBased Dynamic Event format . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . 129

18.8.1. Check . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . 129

18.8.2. Monitor . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . 129

18.8.3. Monitor diff . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . 130

18.9. ONVIF/MetaEvent Notification (Based on ONVIF Draft) . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . 130

18.10. BestShot RTP Stream . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . 131

18.11. Metadata Format . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . 131

18.11.1. Sample Meta Frame with all fields (Only for reference) . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . 132

19. Self-signed Certificate Creation and Use. . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . 136

19.1. Attributes . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . 136

19.2. Getting the List of Certificates . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . 136

19.3. Creating a Self-signed Certificate . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . 138

19.4. Selecting a Certificate . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . 139

19.5. Removing a Certificate . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . 139

20. Intercom Camera Integration . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . 140

20.1. Overview . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . 140

20.1.1. Supports the SIP (Session Initation Protocol) . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . 140

20.1.2. NAT Traversal . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . 140

20.2. Difference of other cameras . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . 140

20.2.1. Profile for VoIP . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . 140

20.2.2. Power relay output . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . 140

20.3. Events . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . 140

20.3.1. Call Request . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . 140

20.3.2. DTMF Received . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . 141

20.3.3. Tampering Switch . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . 141

20.4. Video codec information for VoIP-only profile . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . 141

20.4.1. Getting all resolution information based on Encoding Type . . . . . . . . . . . . . . . . . . . . . . . . . . . . 141

20.5. Usage Scenarios. . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . 161

20.5.1. VMS Usage (When SIP not supported) . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . 161

20.5.2. SIP Call Usage . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . 161

20.6. SUNAPI event status example . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . 161

20.6.1. Getting event status . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . 161

20.6.2. Getting scheme-based event status . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . 164

20.7. Metadata format . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . 174

20.7.1. CallRequest event. . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . 174

20.7.2. TamperingSwitch event . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . 175

20.7.3. DTMF event . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . 175


SUNAPI 5


21. Sample Application to get Device Information. . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . 177

22. References . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . 181


6 Application Programmer’s Guide


## **Chapter 1. Introduction**

SUNAPI (Smart Unified API) is a common protocol used by CMS, VMS and mobile clients to communicate

with Hanwha security devices, such as network cameras, DVRs and NVRs.


SUNAPI allows you to access product features simply by entering standard HTTP URLs. The URLs pass

variables to SUNAPI’s CGI, which interfaces with the specific product. This simplified interface system

makes it possible for central monitoring software to access the features of a diverse set of products in a

standardized way. This makes SUNAPI a valuable tool for developers of central monitoring software and

other network video applications.


This document describes how the SUNAPI protocol can be used from a programmer’s perspective. It is

intended as a complementary document to the SUNAPI specification document; as such, this document

does not cover all of the features described in the specification.


SUNAPI 7


## **Chapter 2. Discovery**

The Discovery protocol used by SUNAPI is a binary protocol, in which the client sends a broadcast

message to a particular port and waits for a response message on a specific port number.


DISCOVERY REQUEST

```
 SunapiDiscoveryRequest()
 {
 IPScanRequest.nMode = DEF_REQ_SCAN;
 IPScanRequest.chPacketID = getUniqueID();// An unique 18 byte value
 derived from MAC.
 Res = Send_BroadcastMessage(IPScanRequest, 255.255.255.255,7701);
 }

```

DISCOVERY RESPONSE

```
 SunapiDiscoveryResponse()
 {
 Response = ReadBroadcastResponse(7711);
 If(Response.chPacketID != getUniqueID())
 {
 return -1;
 }

 Result.MacAddress = Response.chMac;
 Result.IPAddress = Response.IpAddress;
 Result.HttpPort = Response.nPort;

```

8 Application Programmer’s Guide


```
 Result.DeviceName = Response.chDeviceName;
 Result.HTTPSMode = Response.nHttpMode;
 If(Result.HTTPSMode)
 Result.HTTPsPort = Response.HttpsPort;
 Result.SunapiVersion = Response.nsupportedProtocol; //1-SVNP,2-sunapi
 1.0, 4 –sunapi 2.0
 return Result;
 }

```

SUNAPI 9


## **Chapter 3. Password Encryption**

This feature was added to protect passwords sent in a URL as plain text. The client can use the following

procedure to send an encrypted password to the device.


**NOTE** This is applicable for all submenus where password is a parameter.


**Step1**


Download the public key from the submenu below: .REQUEST

```
 http://<ip>/stw-cgi/security.cgi?msubmenu=rsa&action=view

```

TEXT RESPONSE

```
 PublicKey=-----BEGIN RSA PUBLIC KEY---- MIIBCgKCAQEA6UfAclvda/DANJqOoWN3u292M+xLpVWgCNUEhhXeuPdgOIlYIWTh
 cABwVhimgngXbn1isEwuIKZ5Q4g366/JgpSkRRCwdXZ4Xz6jObr544Dp9nCKU/UJ
 3D3bQ9FJbAkBcFN7UCe6UISCcfUMrmn4PFOPSupqiCjDJ/oZgENIG8Ugtt392/QT
 KX9l108IDHSj+ziL2FlJ3VW8xX7KNismZg5h8xPnwb90qQJawxyW7p5Z+ngOnJ0X
 pA6X35Z0qOBsEw0L3x6QDrvKcGXA1pR6odfQlExj2uNT+Xg8NNeGiCGvFwBHooqh
 yMDY1EATgAtROSeTjgnO4aCz3uB2GjAw/QIDAQAB
 -----END RSA PUBLIC KEY----
```

JSON RESPONSE

```
 {
 "PublicKey": "-----BEGIN RSA PUBLIC KEY---- \nMIIBCgKCAQEA6UfAclvda/DANJqOoWN3u292M+xLpVWgCNUEhhXeuPdgOIlYIWTh\ncABwVhim
 gngXbn1isEwuIKZ5Q4g366/JgpSkRRCwdXZ4Xz6jObr544Dp9nCKU/UJ\n3D3bQ9FJbAkBcFN7UC
 e6UISCcfUMrmn4PFOPSupqiCjDJ/oZgENIG8Ugtt392/QT\nKX9l108IDHSj+ziL2FlJ3VW8xX7K
 NismZg5h8xPnwb90qQJawxyW7p5Z+ngOnJ0X\npA6X35Z0qOBsEw0L3x6QDrvKcGXA1pR6odfQlE
 xj2uNT+Xg8NNeGiCGvFwBHooqh\nyMDY1EATgAtROSeTjgnO4aCz3uB2GjAw/QIDAQAB\n---- END RSA PUBLIC KEY-----\n"
 }

```

**Step 2**


Client encrypts the password using the RSA Public Key and RSA_PKCS1_PADDING padding scheme.


**Step 3**


Base64 encodes the binary data and sends the password in the post message. The **IsPasswordEncrypted**


10 Application Programmer’s Guide


parameter should be set to true in the request.


Example:

```
 http://<DeviceIp>/stw cgi/security.cgi?msubmenu=users&action=update&Index=1&UserID=user1&Enable=Tr
 ue&IsPasswordEncrypted=True

```

Body

```
 Vvg2Ku93HlReI+3RseQgfYQoxUFkh9P2L5RvjZ+bLovLTGMQ23OFT+BDaIwMcgvszTwCugk0TuKH
 ENsczardZMQLSosu8RBcqKUMqDq2M1x8fO6Y4S0qlklAtaKl3d9vG0fBdV7BXRqgvK6VIGEc/6Gd
 Pyp4wzY31dalmfwObsdtN//eOU/cVP8MQSCiPod0b5fIWWwekHfDMbQhW2J8eY1KIeOo2O9+vo0g
 ql5vBLFEeFvASZI8UEguxAbOJk4F7iaSr8IFmQhNBXsVYevcAuMgAPvGk3LbXv1DlJrUqUhj9U2r
 2peMGAGl4vaLPt3M2V9UUKlEn7JR/CUI8Pk1Qg==

```

SUNAPI 11


## **Chapter 4. Setting the password in factory** **default state**

Starting from Sunapi version 2.5.5, the device supports the initial password setting using pw_init.cgi.

Password init cgi is a hidden CGI and it requires no authentication to be used only in the factory default

state.


The initial password can also be configured using the IP Installer Protocol [Refer:
**NOTE**

Ipinstaller protocol document].

### **4.1. To check if the camera password is initialized or not** **initialized**

REQUEST

```
 http://<ip>/init-cgi/pw_init.cgi?msubmenu=statuscheck&action=view

```

If the camera is already initialized, the response would be:


RESPONSE

```
 {
 "Initialized": true,
 "Language": "English",
 "MaxChannel": 1,
 "SpecialType": "none",
 "NewPasswordPolicy": true,
 "MaxPasswordLength": 64,
 "Manufacturer": "Hanwha Vision"
 }

```

If the camera is not initialized, the response would be (The RSA public below can be used to encrypt the

password as explained in chapter 12.):


RESPONSE

```
 {
 "Initialized": false,
 "Language": "English",
 "MaxChannel": 2,
 "SpecialType": "none",
 "NewPasswordPolicy": true,
 "MaxPasswordLength" : 64,

```

12 Application Programmer’s Guide


```
 "SupportedPublicKeyFormats": [
 "PKCS1",
 "X509"
 ],
 "PublicKey": "-----BEGIN RSA PUBLIC KEY---- \nMIIBCgKCAQEAxQMliqqm+N+smTfckt4t9Ab8/PaRLTWa1OfgtnYaimcNtP9O5xJx\nS7rRu1Md
 MSTbXf6MSRNUjUJYK57HpGOIUlc8jPeqo7bEO27nhRYu/zWOsgkT4VS5\nALDLh85U87Z7OsTTpn
 UhjBzGJltOTDToA4T51hd0BNbFNQWWIia2dHukxzdiTiGo\n8gPkEEare7HVHBqdA6ET58jkk7dM
 UbmgARpOvFjm1sgYQRdRRa0JvfZz0A6hEQA0\nqG18pqTAahyQ19k4N2AHROV7UcsblmIotJ+Lql
 WhSJzcy5BWSy8bm6s4r5zJoDL1\ncyYUuvvaswaMobVTk5afysS7rRu2UW/9LwIDAQAB\n---- END RSA PUBLIC KEY-----\n",
 "Manufacturer": "Hanwha Vision"
 }

```

When **SupportedPublicKeyFormats** are specified in response, it’s possible to get the rsa public key in

different formats, default key format is PKCS1.


If in response **MaxPasswordLength** is not present, the maximum password length
**NOTE**

supported is 15. If present, it defines the maximum allowed password length.


Example request to get the certificate in X509 format.


REQUEST

```
 http://<DeviceIP>/init cgi/pw_init.cgi?msubmenu=statuscheck&action=view&PublicKeyFormat=X509

```

RESPONSE

```
 {
 "Initialized": false,
 "Language": "English",
 "MaxChannel": 2,
 "SpecialType": "none",
 "NewPasswordPolicy": true,
 "MaxPasswordLength" : 64,
 "SupportedPublicKeyFormats": [
 "PKCS1",
 "X509"
 ],
 "PublicKey": "-----BEGIN PUBLIC KEY---- \nMIIBIjANBgkqhkiG9w0BAQEFAAOCAQ8AMIIBCgKCAQEAxQMliqqm+N+smTfckt4t\n9Ab8/PaR
 LTWa1OfgtnYaimcNtP9O5xJxS7rRu1MdMSTbXf6MSRNUjUJYK57HpGOI\nUlc8jPeqo7bEO27nhR

```

SUNAPI 13


```
 Yu/zWOsgkT4VS5ALDLh85U87Z7OsTTpnUhjBzGJltOTDTo\nA4T51hd0BNbFNQWWIia2dHukxzdi
 TiGo8gPkEEare7HVHBqdA6ET58jkk7dMUbmg\nARpOvFjm1sgYQRdRRa0JvfZz0A6hEQA0qG18pq
 TAahyQ19k4N2AHROV7UcsblmIo\ntJ+LqlWhSJzcy5BWSy8bm6s4r5zJoDL1cyYUuvvaswaMobVT
 k5afysS7rRu2UW/9\nLwIDAQAB\n-----END PUBLIC KEY-----\n",
 "Manufacturer": "Hanwha Vision"
 }

### **4.2. Checking the Install Wizard state in NVR**
```

REQUEST

```
 http://<ip>/init cgi/pw_init.cgi?msubmenu=statuscheck&action=view&ShowStage=True

```

If the NVR is already initialized, the response would be:


Stage field can take any of the following values "factoryreset, "installwizard", "installwizard_done


RESPONSE

```
 {
 "Initialized": true,
 "Stage": "installwizard_done",
 "Language": "English",
 "MaxChannel": 1,
 "SpecialType": "none",
 "Manufacturer": "Hanwha Vision"
 }

### **4.3. To set the initial password**
```

Setting the initial password will work only once. If the password is already set, it will fail.


To set the password without password encryption:


REQUEST

```
 http://<DeviceIP>/init cgi/pw_init.cgi?msubmenu=setinitpassword&action=set&Password=5tkatjd!

```

**NOTE** The plain text initial password setting will soon be deprecated.


To set the password with password encryption, use the RSA key and follow the instructions in Chapter


14 Application Programmer’s Guide


Password Encryption


REQUEST (POST)

```
 http://<DeviceIP>/init cgi/pw_init.cgi?msubmenu=setinitpassword&action=set&IsPasswordEncrypted=True

```

POST Payload

```
 <base64 encoded encypted password as post content>

```

Until initial password is set, all the cgis will be disabled. They will be enabled immediately
**NOTE**

after setting the initial password.


SUNAPI 15


## **Chapter 5. Basic Setup**

### **5.1. Attributes**

Attributes XML contains two sections.


 - **attributes** : Gives Information about the capabilities of the device.

Ex: Max Channels, Max Alarm Inputs, Max Alarm Outputs etc.


 - **cgis** : Gives Information about each submenu, action and parameters in SUNAPI commands.


16 Application Programmer’s Guide


Attributes will be changed dynamically based on the camera connection.


For more information on the attributes, please refer to [8] SUNAPI_attributes_2.6.3 in the References

section.

### **5.2. Device Information**

This command will return information about the device, such as model name, firmware version, language

etc.


REQUEST

```
 http://<Device IP>/stw-cgi/system.cgi?msubmenu=deviceinfo&action=view

```

NVR RESPONSE

```
 HTTP/1.0 200 OK
 Content-type: application/json
 <Body>

```

SUNAPI 17


```
 {
 Model=PRN-4011
 FirmwareVersion=v2.10_180329015157
 BuildDate=2018.03.29
 WebURL=http://www.hanwhasecurity.com
 DeviceType=NVR
 ConnectedMACAddress=00:09:18:30:97:01
 RequestedClientIPAddress=192.168.71.43
 CGIVersion=2.5.6
 MicomVersion=36
 DeviceName=PRN-4011
 Language=English
 }

```

CAMERA RESPONSE

```
 HTTP/1.0 200 OK
 Content-type: application/json
 <Body>

 {
 "Model": "PNM-C7083RVD",
 "SerialNumber": "SEP70GRC0000SY",
 "FirmwareVersion": "2.21.01_20220517_R276",
 "BuildDate": "2022.05.17",
 "WebURL": "http://www.hanwhavision.com/",
 "DeviceType": "NWC",
 "ConnectedMACAddress": "00:09:18:6E:12:B0",
 "ISPVersion": "1.00_220504",
 "BootloaderVersion": "    ",
 "CGIVersion": "2.6.1",
 "ONVIFVersion": "20.12",
 "DeviceName": "Camera",
 "DeviceLocation": "Location",
 "DeviceDescription": "Description",
 "Memo": "Memo",
 "Language": "English",
 "PasswordStrength": "Strong",
 "OpenSDKVersion": "4.02_220405",
 "FirmwareGroup": "PNM-C7083RVD"

```

18 Application Programmer’s Guide


```
 }

### **5.3. Date Information**
```

This command will return information about the device’s Date settings, such as the Time zone, DST

settings, etc. Please refer to [3] SUNAPI_system_2.6.3 in the References section.


**NOTE** VMS Application has to sync the date and time with the Device.


REQUEST

```
 http://<Device IP>/stw-cgi/system.cgi?msubmenu=date&action=view

```

NVR RESPONSE

```
 HTTP/1.0 200 OK
 Content-type: application/json
 <Body>

 {
 "NTPLastUpdatedTime":  "2022-02-13 02:10:43",
 "LocalTime":  "2022-02-13 02:10:43",
 "UTCTime": "2022-02-13 02:10:43",
 "SyncType": "Manual",
 "NTPURLList":  "203.248.240.140",
 "NTPStatus":  "Fail",
 "DSTEnable":  true,
 "POSIXTimeZone":  "STWT0STWST,M3.5.0/1:00:00,M10.5.0/1:00:00",
 "DateFormat":  "YYYY-MM-DD",
 "TimeFormat":  "HMS24"
 }

```

CAMERA RESPONSE

```
 HTTP/1.0 200 OK
 Content-type: application/json
 <Body>

 {
 "NTPURLList": [

```

SUNAPI 19


```
 "pool.ntp.org",
 "asia.pool.ntp.org",
 "europe.pool.ntp.org",
 "north-america.pool.ntp.org",
 "time.nist.gov"
 ],
 "LocalTime": "2022-05-25 03:32:52",
 "UTCTime": "2022-05-25 03:32:52",
 "SyncType": "Manual",
 "DSTEnable": false,
 "TimeZoneIndex": 33,
 "POSIXTimeZone": "STWT0STWST,M3.5.0/1,M10.5.0"
 }

### **5.4. Event Session**
```

VMS application has to open an event session to receive the events from the Device.


NVR will send all events by channels, system events, alarm events, configuration change events, etc., to all

connected VMS applications. Please refer to [7] SUNAPI_event_2.6.3 in the References section.


If the event is "ChangedConfigURI", VMS application has to update the corresponding
**NOTE**

configuration.


Ex: SNMP Configuration change

```
 Timestamp=2015-05-08T02:18:59Z
 SystemEvent.ConfigChange=True
 ChangedConfigURI=network.cgi?msubmenu=snmp

```

**Event Status** has three actions –


 - Check : Gets the current status of all events


 - MonitorDiff : Gets the event status whenever the state of the event changes


20 Application Programmer’s Guide


 - Monitor: Gets the event status of all events periodically and when the state of the event changes


In Monitor and MonitorDiff modes, the connection is maintained, and there is a
**NOTE**

notification whenever an event occurs.


REQUEST

```
 http://<DeviceIP>/stw-cgi/eventstatus.cgi?msubmenu=eventstatus&action=check

```

SUNAPI 21


RESPONSE

```
 HTTP/1.0 200 OK
 Content-type: text/plain
 <Body>

 Channel.0.NetworkCameraConnect=True
 Channel.0.AMDStart=False
 Channel.0.LowFps=False
 Channel.0.Tampering=False
 Channel.0.Videoloss=False
 Channel.0.AudioDetection=False
 Channel.0.NetworkAlarmInput=False
 Channel.0.MotionDetection=False
 Channel.0.FaceDetection=False
 Channel.0.VideoAnalytics.Passing=False
 Channel.0.VideoAnalytics.Entering=False
 Channel.0.VideoAnalytics.Exiting=False
 Channel.0.VideoAnalytics.Appearing=False
 Channel.0.VideoAnalytics.Disappearing=False
 Channel.0.AudioAnalytics.Scream=False
 Channel.0.AudioAnalytics.Gunshot=False
 Channel.0.AudioAnalytics.Explosion=False
 Channel.0.AudioAnalytics.GlassBreak=False
 Channel.0.DefocusDetection=False
 Channel.0.FogDetection=False
 Channel.0.SDFail=False
 Channel.0.SDFull=False
 Channel.0.Tracking=False

```

22 Application Programmer’s Guide


## **Chapter 6. Live Stream Setup**

### **6.1. Get Video Sources**

This command will return information about all video sources.


For an NVR, it will also provide information on whether the camera is registered or not, whether video is

enabled or not, etc. Refer to [4] in the References section for more information.


REQUEST

```
 http://<Device IP>/stw-cgi/media.cgi?msubmenu=videosource&action=view

```

SUNAPI 23


RESPONSE

```
 HTTP/1.0 200 OK
 Content-type: text/plain
 <Body>

 Channel.0.Type=NTSC
 Channel.0.SensorCaptureSize=Unknown
 Channel.0.Name=CAM 01
 Channel.0.State=On
 Channel.1.Type=NTSC
 Channel.1.SensorCaptureSize=Unknown
 Channel.1.Name=CAM 02
 Channel.1.State=On
 Channel.2.Type=NTSC
 Channel.2.SensorCaptureSize=Unknown
 Channel.2.Name=CAM 03
 Channel.2.State=On

### **6.2. Get Video Profiles**
```

This command will return information about all the video profiles.


For an NVR, we can get the video profile information of all registered cameras. Please refer to [4]

SUNAPI_video.audio_2.6.3 in the References section for more information.


REQUEST

```
 http://<Device IP>/stw-cgi/media.cgi?msubmenu=videoprofile&action=view

```

CAMERA RESPONSE

```
 HTTP/1.0 200 OK
 Content-type: text/plain
 <Body>

 Channel.0.Profile.1.Name=MJPEG
 Channel.0.Profile.1.EncodingType=MJPEG
 Channel.0.Profile.1.RTPMulticastEnable=False
 Channel.0.Profile.1.RTPMulticastType=IPV4
 Channel.0.Profile.1.RTPMulticastAddress=

```

24 Application Programmer’s Guide


```
 Channel.0.Profile.1.RTPMulticastAddressIPv6=
 Channel.0.Profile.1.RTPMulticastPort=0
 Channel.0.Profile.1.RTPMulticastTTL=5
 Channel.0.Profile.1.CropEncodingEnable=False
 Channel.0.Profile.1.CropAreaCoordinate=480,360,2080,1560
 Channel.0.Profile.1.CropRatio=Manual
 Channel.0.Profile.1.Resolution=2560x1920
 Channel.0.Profile.1.FrameRate=1
 Channel.0.Profile.1.CompressionLevel=10
 Channel.0.Profile.1.Bitrate=6144
 Channel.0.Profile.1.MJPEG.PriorityType=Bitrate
 Channel.0.Profile.1.AudioInputEnable=False
 Channel.0.Profile.1.ViewModeType=Overview
 Channel.0.Profile.1.IsFixedProfile=True
 Channel.0.Profile.1.ProfileToken=DefaultProfile-01-0

 Channel.0.Profile.2.Name=H.264
 Channel.0.Profile.2.EncodingType=H264
 Channel.0.Profile.2.RTPMulticastEnable=False
 Channel.0.Profile.2.RTPMulticastType=IPV4
 Channel.0.Profile.2.RTPMulticastAddress=
 Channel.0.Profile.2.RTPMulticastAddressIPv6=
 Channel.0.Profile.2.RTPMulticastPort=0
 Channel.0.Profile.2.RTPMulticastTTL=5
 Channel.0.Profile.2.CropEncodingEnable=False
 Channel.0.Profile.2.CropAreaCoordinate=480,360,2080,1560
 Channel.0.Profile.2.CropRatio=Manual
 Channel.0.Profile.2.Resolution=2560x1920
 Channel.0.Profile.2.FrameRate=30
 Channel.0.Profile.2.CompressionLevel=10
 Channel.0.Profile.2.Bitrate=7168
 Channel.0.Profile.2.H264.BitrateControlType=VBR
 Channel.0.Profile.2.H264.PriorityType=FrameRate
 Channel.0.Profile.2.H264.GOVLength=60
 Channel.0.Profile.2.H264.Profile=High
 Channel.0.Profile.2.H264.EntropyCoding=CABAC
 Channel.0.Profile.2.H264.SmartCodecEnable=False
 Channel.0.Profile.2.H264.MaxGOVLength=240
 Channel.0.Profile.2.H264.MinGOVLength=1
 Channel.0.Profile.2.H264.DynamicFPSEnable=False
 Channel.0.Profile.2.H264.MinDynamicFPS=1

```

SUNAPI 25


```
 Channel.0.Profile.2.H264.DynamicGOVEnable=False
 Channel.0.Profile.2.H264.DynamicGOVLength=240
 Channel.0.Profile.2.H264.MaxDynamicGOVLength=480
 Channel.0.Profile.2.AudioInputEnable=False
 Channel.0.Profile.2.ViewModeType=Overview
 Channel.0.Profile.2.IsFixedProfile=True
 Channel.0.Profile.2.IsDigitalPTZProfile=False
 Channel.0.Profile.2.ProfileToken=DefaultProfile-02-0
 Channel.0.Profile.2.IsFixedFrameRateProfile=False

 Channel.0.Profile.3.Name=H.265
 Channel.0.Profile.3.EncodingType=H265
 Channel.0.Profile.3.RTPMulticastEnable=False
 Channel.0.Profile.3.RTPMulticastType=IPV4
 Channel.0.Profile.3.RTPMulticastAddress=
 Channel.0.Profile.3.RTPMulticastAddressIPv6=
 Channel.0.Profile.3.RTPMulticastPort=0
 Channel.0.Profile.3.RTPMulticastTTL=5
 Channel.0.Profile.3.CropEncodingEnable=False
 Channel.0.Profile.3.CropAreaCoordinate=480,360,2080,1560
 Channel.0.Profile.3.CropRatio=Manual
 Channel.0.Profile.3.Resolution=2560x1920
 Channel.0.Profile.3.FrameRate=30
 Channel.0.Profile.3.CompressionLevel=10
 Channel.0.Profile.3.Bitrate=4608
 Channel.0.Profile.3.H265.BitrateControlType=VBR
 Channel.0.Profile.3.H265.PriorityType=FrameRate
 Channel.0.Profile.3.H265.GOVLength=60
 Channel.0.Profile.3.H265.Profile=Main
 Channel.0.Profile.3.H265.EntropyCoding=CABAC
 Channel.0.Profile.3.H265.SmartCodecEnable=False
 Channel.0.Profile.3.H265.MaxGOVLength=240
 Channel.0.Profile.3.H265.MinGOVLength=1
 Channel.0.Profile.3.H265.DynamicFPSEnable=False
 Channel.0.Profile.3.H265.MinDynamicFPS=1
 Channel.0.Profile.3.H265.DynamicGOVEnable=False
 Channel.0.Profile.3.H265.DynamicGOVLength=240
 Channel.0.Profile.3.H265.MaxDynamicGOVLength=480
 Channel.0.Profile.3.AudioInputEnable=False
 Channel.0.Profile.3.ViewModeType=Overview
 Channel.0.Profile.3.IsFixedProfile=True

```

26 Application Programmer’s Guide


```
 Channel.0.Profile.3.IsDigitalPTZProfile=False
 Channel.0.Profile.3.ProfileToken=DefaultProfile-03-0
 Channel.0.Profile.3.IsFixedFrameRateProfile=False

 Channel.0.Profile.10.Name=MOBILE
 Channel.0.Profile.10.EncodingType=H264
 Channel.0.Profile.10.RTPMulticastEnable=False
 Channel.0.Profile.10.RTPMulticastType=IPV4
 Channel.0.Profile.10.RTPMulticastAddress=
 Channel.0.Profile.10.RTPMulticastAddressIPv6=
 Channel.0.Profile.10.RTPMulticastPort=0
 Channel.0.Profile.10.RTPMulticastTTL=5
 Channel.0.Profile.10.CropEncodingEnable=False
 Channel.0.Profile.10.CropAreaCoordinate=480,360,2080,1560
 Channel.0.Profile.10.CropRatio=Manual
 Channel.0.Profile.10.Resolution=320x240
 Channel.0.Profile.10.FrameRate=10
 Channel.0.Profile.10.CompressionLevel=10
 Channel.0.Profile.10.Bitrate=2048
 Channel.0.Profile.10.H264.BitrateControlType=VBR
 Channel.0.Profile.10.H264.PriorityType=FrameRate
 Channel.0.Profile.10.H264.GOVLength=20
 Channel.0.Profile.10.H264.Profile=High
 Channel.0.Profile.10.H264.EntropyCoding=CABAC
 Channel.0.Profile.10.H264.SmartCodecEnable=False
 Channel.0.Profile.10.H264.MaxGOVLength=80
 Channel.0.Profile.10.H264.MinGOVLength=1
 Channel.0.Profile.10.H264.DynamicFPSEnable=False
 Channel.0.Profile.10.H264.MinDynamicFPS=1
 Channel.0.Profile.10.H264.DynamicGOVEnable=False
 Channel.0.Profile.10.H264.DynamicGOVLength=80
 Channel.0.Profile.10.H264.MaxDynamicGOVLength=160
 Channel.0.Profile.10.AudioInputEnable=False
 Channel.0.Profile.10.ViewModeType=Overview
 Channel.0.Profile.10.IsFixedProfile=False
 Channel.0.Profile.10.IsDigitalPTZProfile=False
 Channel.0.Profile.10.ProfileToken=DefaultProfile-04-0
 Channel.0.Profile.10.IsFixedFrameRateProfile=False

```

SUNAPI 27


NVR RESPONSE

```
 HTTP/1.0 200 OK
 Content-type: text/plain
 <Body>

 Channel.0.Profile.1.IsFixedProfile=True
 Channel.0.Profile.1.IsDigitalPTZProfile=False
 Channel.0.Profile.1.Name=MJPEG
 Channel.0.Profile.1.ProfileToken=Profile1
 Channel.0.Profile.1.ViewModeIndex=0
 Channel.0.Profile.1.ViewModeType=Overview
 Channel.0.Profile.1.EncodingType=MJPEG
 Channel.0.Profile.1.Bitrate=6144
 Channel.0.Profile.1.Resolution=640x480
 Channel.0.Profile.1.FrameRate=1
 Channel.0.Profile.1.CompressionLevel=10
 Channel.0.Profile.1.AudioInputEnable=True
 Channel.0.Profile.2.IsFixedProfile=True
 Channel.0.Profile.2.IsDigitalPTZProfile=False
 Channel.0.Profile.2.Name=FisheyeView
 Channel.0.Profile.2.ProfileToken=Profile2
 Channel.0.Profile.2.ViewModeIndex=0
 Channel.0.Profile.2.ViewModeType=Overview
 Channel.0.Profile.2.EncodingType=H264
 Channel.0.Profile.2.Bitrate=7280
 Channel.0.Profile.2.H264.Profile=High
 Channel.0.Profile.2.H264.BitrateControlType=VBR
 Channel.0.Profile.2.Resolution=4000x3000
 Channel.0.Profile.2.FrameRate=20
 Channel.0.Profile.2.CompressionLevel=10
 Channel.0.Profile.2.AudioInputEnable=True
 Channel.0.Profile.3.IsFixedProfile=False
 Channel.0.Profile.3.IsDigitalPTZProfile=True
 Channel.0.Profile.3.Name=Dewarp1
 Channel.0.Profile.3.ProfileToken=Profile3
 Channel.0.Profile.3.ViewModeIndex=1
 Channel.0.Profile.3.ViewModeType=QuadView
 Channel.0.Profile.3.EncodingType=H264
 Channel.0.Profile.3.Bitrate=5120
 Channel.0.Profile.3.H264.Profile=High

```

28 Application Programmer’s Guide


```
 Channel.0.Profile.3.H264.BitrateControlType=VBR
 Channel.0.Profile.3.Resolution=2944x2208
 Channel.0.Profile.3.FrameRate=20
 Channel.0.Profile.3.CompressionLevel=10
 Channel.0.Profile.3.AudioInputEnable=True

### **6.3. Get Audio Inputs**
```

This command will return information about audio the input configuration, such as enabled statuses,

encoding types, etc., for all the channels. Please refer to [4] SUNAPI_video.audio_2.6.3 in the References

section for more information.


REQUEST

```
 http://<Device IP>/stw-cgi/media.cgi?msubmenu=audioinput&action=view

```

RESPONSE

```
 HTTP/1.0 200 OK
 Content-type: text/plain
 <Body>

 Channel.0.Enable=True
 Channel.0.SampleRate=8000
 Channel.0.Mode=Mono
 Channel.0.EncodingType=G711
 Channel.0.Bitrate=0
 Channel.0.Gain=1
 Channel.1.Enable=True
 Channel.1.SampleRate=8000
 Channel.1.Mode=Mono
 Channel.1.EncodingType=G711
 Channel.1.Bitrate=0
 Channel.1.Gain=1

### **6.4. Get Audio Outputs**
```

This command will return information about the audio talk configuration, such as the enabled/disabled

statuses, decoding types, etc., for all the channels. Please refer to [4] SUNAPI_video.audio_2.6.3 in the

References section for more information.


SUNAPI 29


REQUEST

```
 http://<Device IP>/stw-cgi/media.cgi?msubmenu=audiooutput&action=view

```

RESPONSE

```
 HTTP/1.0 200 OK
 Content-type: text/plain
 <Body>

 Channel.0.Enable=False
 Channel.1.Enable=False
 Channel.2.Enable=True
 Channel.2.UnitSize=8000
 Channel.2.SampleRate=8000
 Channel.2.Mode=Mono
 Channel.2.DecodingType=G711
 Channel.2.Bitrate=0
 Channel.2.Gain=1
 Channel.3.Enable=True
 Channel.3.UnitSize=8000
 Channel.3.SampleRate=8000
 Channel.3.Mode=Mono
 Channel.3.DecodingType=G711
 Channel.3.Bitrate=0
 Channel.3.Gain=1

### **6.5. Get Video Profile Policy**
```

This command will return information about which profile is configured for what purpose. For a camera,

we can check which profile is used as Default, Event Profile and Recording Profile. For an NVR, we can

check which profile is used for Live, Recording and Network.


Please refer to [4] SUNAPI_video.audio_2.6.3 in the References section for more information.


REQUEST

```
 http://<Device IP>/stw-cgi/media.cgi?msubmenu=videoprofilepolicy&action=view

```

NVR RESPONSE

```
 HTTP/1.0 200 OK

```

30 Application Programmer’s Guide


```
 Content-type: text/plain
 <Body>

 Channel.0.NetworkProfile=1
 Channel.0.LiveProfile=5
 Channel.0.RecordProfile=2
 Channel.0.LiveMode=Auto
 Channel.1.NetworkProfile=0
 Channel.1.LiveProfile=8
 Channel.1.RecordProfile=2
 Channel.1.LiveMode=Auto
 Channel.2.NetworkProfile=4
 Channel.2.LiveProfile=3
 Channel.2.RecordProfile=2
 Channel.2.LiveMode=Auto
 Channel.3.NetworkProfile=3
 Channel.3.LiveProfile=4
 Channel.3.RecordProfile=2
 Channel.3.LiveMode=Auto

```

CAMERA RESPONSE

```
 HTTP/1.0 200 OK
 Content-type: text/plain
 <Body>

 Channel.0.DefaultProfile=2
 Channel.0.EventProfile=1
 Channel.0.RecordProfile=1

### **6.6. Get Session Key**
```

This command will return the unique session key for Live, Playback, and Backup from NVR.


Please refer to [4] SUNAPI_video.audio_2.6.3 in the References section for more information.


**NOTE** This functionality is NVR specific


SUNAPI 31


REQUEST

```
 http://<Device IP>/stw-cgi/media.cgi?msubmenu=sessionkey&action=view

```

RESPONSE

```
 HTTP/1.0 200 OK
 Content-type: text/plain
 <Body>

 SessionKey=1519123

### **6.7. Get Stream URI For Live**
```

This command will return the URL for getting live streams from the device.


Please refer to [4] SUNAPI_video.audio_2.6.3 in the References section for more information.


NVR REQUEST

```
 http://<Device IP>/stw cgi/media.cgi?msubmenu=streamuri&action=view&Channel=0&MediaType=Live&Mode=F
 ull&ClientType=PC

```

NVR RESPONSE

```
 HTTP/1.0 200 OK
 Content-type: text/plain
 <Body>

 URI=rtsp://<Device IP>:<RTSP Port>/LiveChannel/0/media.smp

```

CAMERA REQUEST

```
 http://192.168.75.194/stw cgi/media.cgi?msubmenu=streamuri&action=view&Channel=0&Profile=1&MediaType=L
 ive&Mode=Full&StreamType=RTPUnicast&TransportProtocol=TCP&RTSPOverHTTP=False

```

CAMERA RESPONSE

```
 HTTP/1.0 200 OK

```

32 Application Programmer’s Guide


```
 Content-type: text/plain
 <Body>

 URI=rtsp://192.168.75.194:554/0/profile1/media.smp

```

SUNAPI 33


## **Chapter 7. Playback Setup**

### **7.1. Get Storage Information**

This command is used to get the current storage settings of the device.


Please refer to [6] SUNAPI_recording_2.6.3 in the References section for more information.


34 Application Programmer’s Guide


REQUEST

```
 http://<Device IP>/stw-cgi/recording.cgi?msubmenu=storage&action=view

```

RESPONSE

```
 HTTP/1.0 200 OK
 Content-type: text/plain
 <Body>

 Enable=True
 OverWrite=True
 DiskEndBeep=False
 AutoDeleteEnable=False
 AutoDeleteDays=400

### **7.2. Get Recording Setup**
```

This method will return the device’s current recording configuration for all the channels. Please refer to

[6] SUNAPI_recording_2.6.3 in the References section for more information.


Ex: current recording frame rate and recording bandwidth and codec information


REQUEST

```
 http://<Device IP>/stw-cgi/recording.cgi?msubmenu=general&action=view

```

RESPONSE

```
 HTTP/1.0 200 OK
 Content-type: text/plain
 <Body>

 Channel.0.FullFrameBandWidth=1.217640
 Channel.0.FullFrameRate=19.980000
 Channel.0.KeyFrameBandWidth=0.406219
 Channel.0.KeyFrameRate=1.000000
 Channel.0.Codec=H264
 Channel.0.RecordOverlap=Normal,AlarmInput
 Channel.0.SourceProfile=FisheyeView
 Channel.0.NormalMode=Full

```

SUNAPI 35


```
 Channel.0.EventMode=I-Frame
 Channel.0.PreEventDuration=Off
 Channel.0.PostEventDuration=1m
 Channel.0.Resolution=4000x3000
 Channel.0.FrameRate=20
 Channel.0.CompressionLevel=10
 Channel.0.AudioEnable=False
 Channel.0.BitrateLimit=148.000000

### **7.3. Search Recording Period**
```

This command will return the overall recording duration in NVR. It retrieves the recording start and end

time that are available from the storage.


**NOTE** This only applies to NVR


Please refer to [6] SUNAPI_recording_2.6.3 in the References section for more information.


REQUEST

```
 http://<Device IP>/stw cgi/recording.cgi?msubmenu=searchrecordingperiod&action=view

```

RESPONSE

```
 HTTP/1.0 200 OK
 Content-type: text/plain
 <Body>

 StartTime=2018-03-19 11:32:13
 EndTime=2018-04-19 13:03:45 DST

### **7.4. Calendar Search**
```

This command is used to retrieve information on the availability of recordings for the selected month and

channels. Please refer to [6] SUNAPI_recording_2.6.3 in the References section for more information.


The response is a 31-digit string, with a digit to represent each day of the month; if the digit is 0 then there

is no recording for that channel on that day, and if it is 1 then recording is available for that day.


REQUEST

```
 http://<Device IP>/stw
```

36 Application Programmer’s Guide


```
 cgi/recording.cgi?msubmenu=calendarsearch&action=view&Month=2015-05 01T00:00:00Z&ChannelIdList=0,5

```

RESPONSE

```
 HTTP/1.0 200 OK
 Content-type: text/plain
 <Body>

 Channel.0.Result=0001111000000000000000000000000
 Channel.5.Result=0000011100000000000000000000000

### **7.5. Get Overlapped IDs**
```

This command is used to get the recordings of overlapped information for the given time range.


If the system time settings changes or DST is applied while recording the video, recordings will be

overlapped for certain period of time.


Eg: When the current recording time is 14:00:00 and the time in the set was changed to 10:00:00, the

recording will have a 4-hour duration and two media tracks. To access these media individually we would

need the overlapped ID information. This will be passed along with the playback RTSP URL and timeline

search. Please refer to [6] SUNAPI_recording_2.6.3 in the References section for more information.


REQUEST

```
 http://<Device IP>/stw cgi/recording.cgi?msubmenu=overlapped&action=view&FromDate=2018-03 01T00:00:00Z&ToDate=2018-03-31T23:59:59Z

```

RESPONSE

```
 HTTP/1.0 200 OK
 Content-type: text/plain
 <Body>

 OverlappedIDList=36, 37

#### **7.5.1. OverlapID - Behaviour of Camera**
```

During the camera’s local recording, the local time is taken as a reference. A new Overlap ID is created

when the time zone changes. Even when the time has changed multiple times, only one Overlap ID will be


SUNAPI 37


created. An Overlap ID is only created on a daily basis and will not be created after the current day. The

latest Overlap ID is determined by the highest value.

#### **7.5.2. OverlapID - Behaviour of NVR**

In NVR UTC, time is taken as a reference for recording, therefore no overlap ID will be created when the

time zone changes or DST is applied. NVR can create an overlap ID when time is changed backwards,

either manually or through NTP sync. If a time shift backwards is over 5 secs, NVR creates a new overlap

ID. Overlap ID is incremented each time a new overlap recording is created, and is maintained throughout

the recording period and not on a daily basis.

### **7.6. Timeline Search**

This command is used to get the recording timeline information for the specific period of time and for the

specific channel. Please refer to [6] SUNAPI_recording_2.6.3 in the References section for more

imformation.


If "SearchByUTCTime" **is set as true** in the attributes response, **then UTC time can be used for timeline**

**search.**


**If the request is sent with time in YYYY-MM-DDTHH:MM:SSZ format, then UTC time is used for**

**search; if the time is in YYYY-MM-DDTHH:MM:SS format then local time is used.**


REQUEST

```
 http://<Device IP>/stw cgi/recording.cgi?msubmenu=timeline&action=view&ChannelIDList=0&FromDate=201
 8-03-07T00:00:01Z&ToDate=2018-03-08T23:59:59Z

```

RESPONSE

```
 HTTP/1.0 200 OK
 Content-type: text/plain
 <Body>

 Channel.0.Result.1.StartTime=2018-03-07T00:00:01Z
 Channel.0.Result.1.EndTime=2018-03-07T01:56:03Z
 Channel.0.Result.1.Type=Manual
 Channel.0.Result.2.StartTime=2018-03-07T00:00:01Z
 Channel.0.Result.2.EndTime=2018-03-07T01:56:03Z
 Channel.0.Result.2.Type=Normal
 Channel.0.Result.3.StartTime=2018-03-07T01:59:01Z
 Channel.0.Result.3.EndTime=2018-03-07T02:07:30Z
 Channel.0.Result.3.Type=Manual

```

38 Application Programmer’s Guide


```
 Channel.0.Result.4.StartTime=2018-03-07T01:59:01Z
 Channel.0.Result.4.EndTime=2018-03-07T02:07:30Z
 Channel.0.Result.4.Type=Normal
 Channel.0.Result.5.StartTime=2018-03-07T02:13:59Z
 Channel.0.Result.5.EndTime=2018-03-07T02:15:13Z
 Channel.0.Result.5.Type=Manual
 Channel.0.Result.6.StartTime=2018-03-07T02:13:59Z
 Channel.0.Result.6.EndTime=2018-03-07T02:15:13Z
 Channel.0.Result.6.Type=Normal
 Channel.0.Result.7.StartTime=2018-03-07T02:15:17Z
 Channel.0.Result.7.EndTime=2018-03-07T04:52:53Z
 Channel.0.Result.7.Type=Manual
 Channel.0.Result.8.StartTime=2018-03-07T02:15:17Z
 Channel.0.Result.8.EndTime=2018-03-07T04:52:53Z
 Channel.0.Result.8.Type=Normal
 TotalCount=8

### **7.7. Get Stream URI for Playback**
```

This command will give the RTSP streaming URL in playback mode.


**NOTE** For a camera, the Playback and Backup URL are the same.


Please refer to [4] SUNAPI_video.audio_2.6.3 in the References section for more information.


NVR REQUEST

```
 http://<Device IP>/stw cgi/media.cgi?msubmenu=streamuri&action=view&Channel=0&MediaType=Search&Mode
 =Full&ClientType=PC

```

NVR RESPONSE

```
 HTTP/1.0 200 OK
 Content-type: text/plain
 <Body>

 URI=rtsp://<Device IP>:<RTSP Port>/PlaybackChannel/0/media.smp

```

SUNAPI 39


CAMERA REQUEST

```
 http://192.168.75.194/stw cgi/media.cgi?msubmenu=streamuri&action=view&Channel=0&MediaType=Backup&Mode
 =Full&StreamType=RTPUnicast&TransportProtocol=TCP&RTSPOverHTTP=False&Overlap
 pedID=0&Profile=1

```

CAMERA RESPONSE

```
 HTTP/1.0 200 OK
 Content-type: text/plain
 <Body>

 URI=rtsp://192.168.75.194:554/0/recording/backup.smp

```

40 Application Programmer’s Guide


## **Chapter 8. PTZ Operation**

PTZ operation can be performed using the PTZ CGI service. In this document we will discuss only basic PTZ

functionality. Please refer to [5] SUNAPI_ptz_2.6.3 in the References section for more information.

### **8.1. Continuous Move**

Pan operation can be performed as follows; in continuous move, the particular operation will continue

until the stop command is sent.


REQUEST

```
 http://<Device IP>/stw cgi/ptzcontrol.cgi?msubmenu=continuous&action=control&Pan=5&Channel=5

```

Tilt Operation


REQUEST

```
 http://<DeviceIP>/stw cgi/ptzcontrol.cgi?msubmenu=continuous&action=control&Tilt=5&Channel=1

```

Zoom operation


REQUEST

```
 http://<DeviceIP>/stw cgi/ptzcontrol.cgi?msubmenu=continuous&action=control&Zoom=3&Channel=1

### **8.2. Stop**
```

To stop all PTZ operation


REQUEST

```
 http://<DeviceIP>/stw cgi/ptzcontrol.cgi?msubmenu=stop&action=control&OperationType=All&Channel=0

### **8.3. Preset**
```

To get preset information


REQUEST

```
 http://<DeviceIP>/stw
```

SUNAPI 41


```
 cgi/ptzcontrol.cgi?msubmenu=preset&action=view&Channel=0

```

RESPONSE

```
 HTTP/1.0 200 OK
 Content-type: text/plain
 <Body>

 Channel.0.Preset.1.Name=Preset1
 Channel.0.Preset.2.Name=Preset2

```

To go to a particular preset


REQUEST

```
 http://<DeviceIP>/stw cgi/ptzcontrol.cgi?msubmenu=preset&action=control&Channel=0&Preset=1

### **8.4. Identifying Capability**
```

PTZ capability of a device can be identified using the attributes cgi.

#### **8.4.1. Real PTZ**

```
 PTZSupport/Support/Absolute.Pan = true
 PTZSupport/Support/Absolute.Tilt = true
 PTZSupport/Support/Absolute.Zoom = true
 PTZSupport/Support/DigitalPTZ = false

#### **8.4.2. Zoom Only**

 PTZSupport/Support/Absolute.Pan = false
 PTZSupport/Support/Absolute.Tilt = false
 PTZSupport/Support/Absolute.Zoom = true

#### **8.4.3. PTRZ**
```

CGI section:

```
 image/ptr/Pan/int = true

```

42 Application Programmer’s Guide


```
 image/ptr/Tilt/int = true
 image/ptr/Rotate/int = true

#### **8.4.4. DPTZ**

 PTZSupport/Support/DigitalPTZ = true
 PTZSupport/Limit/MaxGroupCount > 0

```

Profile-based DPTZ support:


If any of the below parameters is listed, DPTZ is only based on the selected profile. Otherwise, DPTZ is

global and applicable to all profiles in the channel.


CGI section,

```
 media/videoprofile/IsDigitalPTZProfile

#### **8.4.5. External PTZ**

 PTZSupport/Support/Absolute.Pan = false
 PTZSupport/Support/Absolute.Tilt = false
 PTZSupport/Support/Absolute.Zoom = false
 IO/Support/RS485 = true
 PTZSupport/Limit/MaxGroupCount = 0

#### **8.4.6. From SUNAPI 2.5.4**
```

Explicit capability added to attribute section

```
 PTZSupport/Support/ExternalPTZ=True
 PTZSupport/Support/RealPTZ=True
 PTZSupport/Support/ZoomOnly=True
 Image/Support/PTRZ=true

```

SUNAPI 43


## **Chapter 9. GPS Information**

Mobile NVR supports getting the current GPS location using SUNAPI.


REQUEST

```
 http://<DeviceIP>/stw-cgi/system.cgi?msubmenu=gps&action=view

```

RESPONSE

```
 HTTP/1.0 200 OK
 Content-type: text/plain
 <Body>

 Check=Periodically
 Periodicity=1
 GPSData=$GPRMC,hhmmss.ss,A,llll.ll,a,yyyyy.yy,a,x.x,x.x,ddmmyy,x.x,a*hh

```

44 Application Programmer’s Guide


## **Chapter 10. RTSP**
### **10.1. RTSP Live Session**

In the RTSP URL, channel information and session ID are important for NVR, while for camera channel

information, the profile name or profile number is important.


Generally for NVR, after creating a session ID for live and getting the stream URI, we can establish a LIVE

RTSP session.


Camera URL Format

[Type1]

```
 rtsp://<Device IP>/<encoding>/media.smp

```

[Type2]

```
 rtsp://<Device IP>/profile<no>/media.smp

```

[Type3]

```
 rtsp://<Device IP>/multicast/<encoding>/media.smp

```

[Type4]

```
 rtsp://<Device IP>/multicast/profile<no>/media.smp

```

[Type5]

```
 rtsp://<Device IP>/<profile name>/media.smp

```

[Type6]

```
 rtsp://<Device IP>/multicast/<profile name>/media.smp

```

Camera URL Format (multi source device)

[Type1]

```
 rtsp://<Device IP>/<chid>/<encoding>/media.smp

```

SUNAPI 45


[Type2]

```
 rtsp://<Device IP>/<chid>/profile<no>/media.smp

```

[Type3]

```
 rtsp://<Device IP>/<chid>/multicast/<encoding>/media.smp

```

[Type4]

```
 rtsp://<Device IP>/<chid>/multicast/profile<no>/media.smp

```

[Type5]

```
 rtsp://<Device IP>/<chid>/<profile name>/media.smp

```

[Type6]

```
 rtsp://<Device IP>/<chid>/multicast/<profile name>/media.smp

```

NVR URL Format

[Type1]

```
 rtsp://<Device IP>:558/LiveChannel/<chid>/media.smp

```

[Type2]

```
 rtsp://<DeviceIP>:558/LiveChannel/<chid>/media.smp/session=<sid>

```

[Type3]

```
 rtsp://<Device IP>:558/LiveChannel/<chid>/media.smp/multicast&session=<sid>

```

[Type4]

```
 rtsp://<DeviceIP>:558/LiveChannel/<chid>/media.smp/iframe&multicast&session=
 <sid>

```

46 Application Programmer’s Guide


[Type5]

```
 rtsp://<Device
 IP>:558/LiveChannel/<chid>/media.smp/profile=<profileNo>&session=<sid>

```

[Type6]

```
 rtsp://<Device
 IP>:558/LiveChannel/<chid>/media.smp/ProfileUsage=<profileType>&session=<sid
 >

```

**NOTE** For NVR the default RTSP Port is 558.


In general, the following types of sessions are supported:


 - Audio


 - Video


 - Metadata


 - BackChannel


In an NVR, all RTSP connections with the same session ID are considered to be a single



**NOTE**



session. (Eg: In 16-view mode, all of the 16 RTSP connections will have the same session

ID).

SessionId should be different for Live, Playback and Backup Sessions.



If the Audio talk feature is supported by a channel, client can open a new RTSP connection only with

backchannel RTP session and send the audio data. This can be done dynamically, only when audio talk is

required, because at one point of time only one client can access Audio talk for a channel.


Backchannel audio RTP session will be mentioned in the SDP only when the DESCRIBE request has


[Require: www.onvif.org/ver20/backchannel as defined in the ONVIF streaming specifications. Please refer](http://www.onvif.org/ver20/backchannel)

to [12] ONVIF Streaming Spec in the References section.


When Audio or Video configuration such as codec/resolution changes, the RTSP connection will be

disconnected from the NVR and an event will be sent to the client regarding configuration change. At this

point, it is the client’s responsibility to reconnect the RTSP session.


The device supports media transport through the following protocols


 - TCP


 - UDP


 - HTTP


SUNAPI 47


 - HTTPS (When SSL is enabled in NVR)


 - Multicast


For RTSP over HTTP and RTSP over HTTPS, port 80 and port 443 are used by default.


MJPEG Streaming Over 3 MP:


Since RFC 2435 does not support resolutions over 2040, we use a combination of the RTP extension and

RFC 2435 for streaming MJPEG videos as described in the ONVIF streaming spec. Please refer to [12]

ONVIF Streaming Spec in the References section.


<RTP HEADER> with extension flag set


<RTP Extension> → FFD8 start code, FFCO (SOF will have the height and width info)


<RFC 2435>

### **10.2. RTSP Playback Session**

To initiate playback streaming and playback RTSP, the URL is required.


For NVR, session is also required. For NVR, when performing multichannel playback, the same session id

can be used. Separate RTSP sessions are used to connect to each channel, and after sending the first play

command, one RTSP session can be used to send commands like, PAUSE, PLAY etc.


Even though playback streaming can work with VLC player, we do not recommend using
**NOTE**

VLC player for testing playback streaming.


Camera URL format:

[Type1]


48 Application Programmer’s Guide


```
 rtsp://<Device IP>/recording/<Start Time>/play.smp

```

[Type2]

```
 rtsp://<Device IP>/recording/<Start Time>-<End Time>/play.smp

```

[Type3]

```
 rtsp://<Device IP>/recording/play.smp

```

Camera URL format (multi source device)

[Type1]

```
 rtsp://<Device IP>/<chid>/recording/<Start Time>/play.smp

```

[Type2]

```
 rtsp://<Device IP>/<chid>/recording/<Start Time>-<End Time>/play.smp

```

[Type3]

```
 rtsp://<Device IP>/<chid>/recording/<Start Time>-<End
 Time>/OverlappedID=<overlapid>/play.smp

```

[Type4]

```
 rtsp://<Device IP>/<chid>/recording/play.smp

```

NVR URL format

[Type1]

```
 rtsp://<Device IP>:558/PlaybackChannel/<chid>/media.smp

```

[Type2]

```
 rtsp://<Device IP>:558/PlaybackChannel/<chid>/media.smp/session=<sid>

```

SUNAPI 49


[Type3]

```
 rtsp://<DeviceIP>:558/PlaybackChannel/<chid>/media.smp/overlap=<id>&session=
 <sid>

```

[Type4]

```
 rtsp://<DeviceIP>:558/PlaybackChannel/<chid>/media.smp/overlap=<id>&session=
 <sid>&iframe

```

[Type5]

```
 rtsp://<DeviceIP>:558/PlaybackChannel/<chid>/media.smp/start=<starttime>&end
 =<endtime>&overlap=<overlapid>&session=<sid>

```

In general all of the supported video formats (h264, MJPEG, MPEG4) and up to 5 audio formats are

supplied in the RTSP DESCRIBE response as RTP sessions. Therefore, when the video/audio format

changes in between recording, the playback session can still continue.


Ex: If the recording has h264 and mjpeg, initially h264 video will be sent over h264 rtp session; when the

format changes to mjpeg, mjpeg rtp session will be used to send the media.


The date and time to play can be sent in two ways. It can be sent in the URL, or in the PLAY command with

Range: clock field as defined in the ONVIF streaming specifications. Please refer to [12] ONVIF Streaming

Spec in the References section.


The time should be specified in the following format:


 - <YYYYMMDDTHHMMSS> (e.g., 20141206T111500) for local time and <YYYYMMDDTHHMMSSZ> (e.g.,

20141206T110000Z) for UTC time on the NVR.


 - <YYYYMMDDHHMMSS> (e.g., 20141206111500) for local time on the camera.


In playback mode, actual playback time of video can be received in two ways: one is through the RTCP,

and another is using RTP Playback Extension header defined in ONVIF specifications. RTP Playback

extension header will be sent only when client sends "Require: ONVIF-replay" in the setup and play

commands.


Rate control can be sent in the play command, to notify whether video should be time-controlled on the

NVR. If it is set to no as below, then receiver/client should control the timing.


The RTP Extension header in playback will follow the ONVIF streaming spec format. Please refer to [12]

ONVIF Streaming Spec in the References section.


50 Application Programmer’s Guide


When MJPEG over 3MP needs to be streamed, we can use the following format:


JPEG extension will have the same SOF information as described in the live case. We can use this SOF

information in the final image we construct.


**Rate-Control:**


By default, rate-control is set to yes in playback mode. It is also defined in the ONVIF streaming spec.


**Immediate:**


Immediate field can be sent, along with play command as defined in the ONVIF streaming spec, to go to a

particular time instantaneously.

#### **10.2.1. Rewind/Fast-Forward**

Rewind and Fast forward operation can be performed using the scale header defined in the RTSP

specification.

```
 PLAY rtsp://<Device IP>/PlaybackChannel/0/media.smp RTSP/1.0
 Scale: 8

```

In the above example, the video will play at 8x speed in forward direction.


**NOTE** NVR supports -64x to 64x. Camera supports -8x to 8x.


SUNAPI 51


When negative scale value is supplied, the video will play in reverse direction.

#### **10.2.2. Slow Play**

Slow play can be performed by specifying a scale header value between 0.1 and 0.9.


For example, if we specify the scale value as 0.5, then the video will be played at half the normal playback

speed.

### **10.3. Backup Session**

In SUNAPI, video backup is achieved using a backup RTSP session and is as follows:


**NOTE** Backup URL is only applicable to NVR


[Type1]

```
 rtsp://<Device IP>:558/BackupChannel/<chid>/media.smp

```

[Type2]

```
 rtsp://<Device IP>:558/BackupChannel/<chid>/media.smp/session=<sid>

```

[Type3]

```
 rtsp://<DeviceIP>:558/BackupChannel/<chid>/media.smp/overlap=<id>&session=<s
 id>

```

[Type4]

```
 rtsp://<DeviceIP>:558/BackupChannel/<chid>/media.smp/overlap=<id>&session=<s
 id>&iframe

```

[Type5]

```
 rtsp://<DeviceIP>:558/BackupChannel/<chid>/media.smp/start=<starttime>&end=<
 endtime>&overlap=<overlapid>&session=<sid>

```

A backup RTSP session is very similar to a playback session, but in backup mode the rate control is

disabled by default, and therefore the media is sent rapidly.


52 Application Programmer’s Guide


## **Chapter 11. POS**

This section explains how to achieve POS (Point of Sale) integration.


**NOTE** This section is applicable only to NVR

### **11.1. Capabilities**

Get Max POS devices supported


REQUEST

```
 http://<DeviceIP>/stw-cgi/attributes.cgi/attributes/System/Limit/MaxPOS

```

RESPONSE

```
 <attribute accesslevel="*user*" value="*64*" type="*int*" name="*MaxPOS*"/>

```

Check whether device supports POS streaming or not


REQUEST

```
 http://<DeviceIP>/stw cgi/attributes.cgi/attributes/Media/Limit/StreamingMetadata

```

RESPONSE

```
 <attribute name="*StreamingMetadata*" accesslevel="*user*" value="*POS*"
 type="*csv*"/>

```

Check whether channel supports Metadata streaming or not


REQUEST

```
 http://<DeviceIP>/stw cgi/attributes.cgi/attributes/Media/Support/0/Stream.Metadata

```

RESPONSE

```
 <attribute name="*Stream.Metadata*" accesslevel="*user*" value="*True*"
 type="*bool*"/>

```

SUNAPI 53


### **11.2. Configuration Setup**

To get the POS configuration


REQUEST

```
 http://<DeviceIP>/stw-cgi/recording.cgi?msubmenu=posconf&action=view

```

REQUEST

```
 http://<DeviceIP/stw cgi/recording.cgi?msubmenu=posconf&action=view&DeviceIDList=1,2

```

RESPONSE

```
 DeviceID.1.DeviceName=TEXT 01
 DeviceID.1.Enable=True
 DeviceID.1.Port=7001
 DeviceID.1.EventPlaybackStartTime=0
 DeviceID.1.EventPlaybackStartTimeUnits=Seconds
 DeviceID.1.ReceiptStart=(1)
 DeviceID.1.ReceiptEnd=(2)
 DeviceID.1.EncodingType=US-ASCII
 DeviceID.1.ChannelIDList=0,1,2,3,4,5,6,7,16,17,18,19,20,21,22,23,32,33,34,35
,36,37,38,39,48,49,50,51,52,53,54,55
 DeviceID.2.DeviceName=TEXT 02
 DeviceID.2.Enable=True
 DeviceID.2.Port=7002
 DeviceID.2.EventPlaybackStartTime=0
 DeviceID.2.EventPlaybackStartTimeUnits=Seconds
 DeviceID.2.ReceiptStart=(1)
 DeviceID.2.ReceiptEnd=(2)
 DeviceID.2.EncodingType=US-ASCII
 DeviceID.2.ChannelIDList=8,9,10,11,12,13,14,15,24,25,26,27,28,29,30,31,40,41
,42,43,44,45,46,47,56,57,58,59,60,61,62,63

```

To set the POS configuration


REQUEST

```
 http://<DeviceIP>/stw cgi/recording.cgi?msubmenu=posconf&action=set&DeviceID=1&DeviceName=POS1&Ena
 ble=True&Port=8001&EventPlaybackStartTime=10&ReceiptStart=Start&ReceiptEnd=E

```

54 Application Programmer’s Guide


```
 nd&EncodingType=UTF-8&ChannelIDList=7,8,9,10

```

REQUEST

```
 http://<DeviceIP>/stw cgi/recording.cgi?msubmenu=posconf&action=set&DeviceID=1&ChannelIDList=None

### **11.3. Event Setup**
```

To get the POS events configuration


REQUEST

```
 http://<DeviceIP>/stw-cgi/recording.cgi?msubmenu=poseventconf&action=view

```

RESPONSE

```
 AmountEventEnable=True
 TotalAmount=100.000000
 TotalType=Above
 KeywordIndex.1.KeywordCondition=Apple
 KeywordIndex.2.KeywordCondition=banana

```

To set POS event configuration


REQUEST

```
 http://<DeviceIP>/stw cgi/recording.cgi?msubmenu=poseventconf&action=set&AmountEventEnable=False&T
 otalAmount=9999999999.9988&TotalType=Below

```

To add event keywords


REQUEST

```
 http://<DeviceIP>/stw cgi/recording.cgi?msubmenu=poseventconf&action=add&KeywordCondition=melon

```

To update the event keyword


REQUEST

```
 http://<DeviceIP>/stw
```

SUNAPI 55


```
 cgi/recording.cgi?msubmenu=poseventconf&action=update&KeywordIndex=2&Keyword
 Condition=apple

```

To remove all event keywords


REQUEST

```
 http://<DeviceIP>/stw-cgi/recording.cgi?msubmenu=poseventconf&action=remove

```

To remove all particular event keywords


REQUEST

```
 http://<DeviceIP>/stw cgi/recording.cgi?msubmenu=poseventconf&action=remove&KeywordIndex=2

### **11.4. Live POS Data**
```

Similar to events, live POS data will be sent in a multi-part session. Client has to open a keep live session to

receive the POS receipts. If any of the configured keywords are found in the receipt, it will be highlighted

in the following format:


Ex: <keyword>APPLE</keyword>


REQUEST

```
 http://<DeviceIP>/stw-cgi/recording.cgi?msubmenu=posdata&action=monitordiff

```

RESPONSE

```
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

```

56 Application Programmer’s Guide


```
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

SUNAPI 57


## **Chapter 12. Metadata Search**

**NOTE** NVR Only

### **12.1. Capabilities**

Check whether the Metadata Search feature is supported or not


REQUEST

```
 http://<DeviceIP>/stw cgi/attributes.cgi/attributes/Recording/Support/SearchMetadata

```

RESPONSE

```
 <attribute name="SearchMetadata" accesslevel="admin" value="True"
 type="bool"/>

```

Get the maximum allowed time gap between from date and to date


REQUEST

```
 http://<DeviceIP>/stw-cgi/
 attributes.cgi/attributes/Recording/Limit/MaxMetadataSearchDays

```

RESPONSE

```
 <attribute accesslevel="admin" value="7" type="int"
 name="MaxMetadataSearchDays"/>

```

Get the maximum supported value for MaxResults


REQUEST

```
 http://<DeviceIP>/stw-cgi/attributes.cgi/recording/metadata/view/MaxResults

```

RESPONSE

```
 http://55.101.54.147/stw cgi/attributes.cgi/recording/storage/set/Channel[<parameter
 name="MaxResults" response="true" request="true"><dataType>]<int max="1000"
 min="1"/></dataType></parameter>

```

58 Application Programmer’s Guide


### **12.2. Start Search**

Request without any filters


REQUEST

```
 http://<DeviceIP>/stw cgi/recording.cgi?msubmenu=metadata&action=control&Mode=Start&MetadataType=P
 OS&FromDate=2016-07-13T00:00:00Z&ToDate=2016-07-16T23:59:59Z

```

Request with Overlapped ID


REQUEST

```
 http://<DeviceIP>/stw cgi/recording.cgi?msubmenu=metadata&action=control&Mode=Start&MetadataType=P
 OS&FromDate=2016-07-15T00:00:00Z&ToDate=2016-07-16T23:59:59Z&OverlappedID=11

```

Request with Overlapped ID and Single Keyword


REQUEST

```
 http://<DeviceIP>/stw cgi/recording.cgi?msubmenu=metadata&action=control&Mode=Start&MetadataType=P
 OS&FromDate=2016-07-15T00:00:00Z&ToDate=2016-07 16T23:59:59Z&OverlappedID=11&Keyword=Apple

```

Request with Overlapped ID and Keyword Green or Apple


REQUEST

```
 http://<DeviceIP>/stw cgi/recording.cgi?msubmenu=metadata&action=control&Mode=Start&MetadataType=P
 OS&FromDate=2016-07-15T00:00:00Z&ToDate=2016-07 16T23:59:59Z&OverlappedID=11&IsWholeWord=false&Keyword=Green%20Apple

```

Request with Overlapped ID and Keyword "Green Apple"


REQUEST

```
 http://<DeviceIP>/stw cgi/recording.cgi?msubmenu=metadata&action=control&Mode=Start&MetadataType=P
 OS&FromDate=2016-07-15T00:00:00Z&ToDate=2016-07 16T23:59:59Z&OverlappedID=11&IsWholeWord=true&Keyword=Green%20Apple

```

SUNAPI 59


Request with Overlapped ID and Keyword Green,Apple


REQUEST

```
 http://<DeviceIP>/stw cgi/recording.cgi?msubmenu=metadata&action=control&Mode=Start&MetadataType=P
 OS&FromDate=2016-07-15T00:00:00Z&ToDate=2016-07 16T23:59:59Z&OverlappedID=11&Keyword=Green,Apple

```

Request with Overlapped ID, Keyword and IsCaseSensitive


REQUEST

```
 http://<DeviceIP>/stw cgi/recording.cgi?msubmenu=metadata&action=control&Mode=Start&MetadataType=P
 OS&FromDate=2016-07-15T00:00:00Z&ToDate=2016-07 16T23:59:59Z&OverlappedID=11&Keyword=APPLE&IsCaseSensitive=true

```

Request with Overlapped ID, Keyword, IsCaseSensitive and Single DeviceID


REQUEST

```
 http://<DeviceIP>/stw cgi/recording.cgi?msubmenu=metadata&action=control&Mode=Start&MetadataType=P
 OS&FromDate=2016-07-15T00:00:00Z&ToDate=2016-07 16T23:59:59Z&OverlappedID=11&Keyword=OKRA&IsCaseSensitive=true&DeviceIDList=
 0

```

Request with Overlapped ID, Keyword, IsCaseSensitive and Multiple DeviceIDs


REQUEST

```
 http://<DeviceIP>/stw cgi/recording.cgi?msubmenu=metadata&action=control&Mode=Start&MetadataType=P
 OS&FromDate=2016-07-15T00:00:00Z&ToDate=2016-07 16T23:59:59Z&OverlappedID=11&Keyword=OKRA&IsCaseSensitive=true&DeviceIDList=
 1,2

```

If search request is successful, Device will return a search token.


RESPONSE

```
 SearchToken=7475

```

60 Application Programmer’s Guide


**NOTE**



It is not possible to search for multiple keywords.

Ex: Search for Keyword1 and Keyword2 is not supported

Ex: Search for Keyword1 or Keyword2 is supported (By using space as delimiter)


### **12.3. Cancel Search**

```
 http://<DeviceIP>/stw cgi/recording.cgi?msubmenu=metadata&action=control&Mode=Cancel&SearchToken=7
 475

### **12.4. Get Search Status**
```

To get search status:

```
 http://<DeviceIP>/stw cgi/recording.cgi?msubmenu=metadata&action=view&Type=Status&SearchToken=7475

### **12.5. Renew Search Token**

 http://<DeviceIP>/stw cgi/recording.cgi?msubmenu=metadata&action=control&Mode=Renew&SearchToken=74
 75

```

TEXT RESPONSE

```
 OK

### **12.6. Get Search Results**
```

To get the results of a search (Max 1000 results by default):

```
 http://<DeviceIP>/stw cgi/recording.cgi?msubmenu=metadata&action=view&Type=Results&SearchToken=747
 5

```

To get the results of a search (First 100 results):

```
 http://<DeviceIP>/stw cgi/recording.cgi?msubmenu=metadata&action=view&Type=Results&ResultFromIndex

```

SUNAPI 61


```
 =1&MaxResults=100&SearchToken=6619

```

TEXT RESPONSE

```
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

```

62 Application Programmer’s Guide


```
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

To get the results of a search (Next 100 results):

```
 http://<DeviceIP>/stw cgi/recording.cgi?msubmenu=metadata&action=view&Type=Results&ResultFromIndex
 =101&MaxResults=100&SearchToken=6619

```

Search Token will expire in 60 seconds.



**NOTE**



Client has to send Renew command periodically to increase the expiry time to 60 seconds

more.



SUNAPI 63


## **Chapter 13. Bypass**

This section explains how the bypass feature can be used in NVR to send commands directly to a camera

registered in an NVR.


**NOTE** NVR Only


**Check whether channel is registered with SUNAPI**

```
 http://<NVR-IP>/stw cgi/attributes.cgi/attributes/Media/Support/0/Protocol.SUNAPI

 <attribute accesslevel="user" value="True" type="bool"
 name="Protocol.SUNAPI"/>

```

**Normal get-set commands**


REQUEST

```
 http://<NVR-IP>/stw cgi/bypass.cgi?msubmenu=bypass&action=control&Channel=<ID>&BypassURI=<URI>

```

**Configuration backup**


REQUEST

```
 curl --digest -u admin:7i8o9p0[ "http://<NVR-IP>/stw cgi/bypass.cgi?msubmenu=bypass&action=control&Channel=2&BypassURI=/stw cgi/system.cgi?msubmenu=configbackup&action=control" > config.bin

```

RESPONSE

```
 Downloaded File from Camera

```

**Snapshot**

```
 http://<NVR-IP>/stw cgi/bypass.cgi?msubmenu=bypass&action=control&Channel=2&BypassURI=/stw cgi/video.cgi?msubmenu=snapshot&action=view&Channel=0

```

**POST**


64 Application Programmer’s Guide


**Configuration restore**


openssl base64 -in config.bin -out encoded.bin


REQUEST

```
 curl --digest -u admin:7i8o9p0[ "http://<NVR-IP>/stw cgi/bypass.cgi?msubmenu=bypass&action=control&Channel=2&BypassURI=/stw cgi/system.cgi?msubmenu=configrestore&action=control&ExcludeSettings=Network
,Camera" -H "Expect:" --data-urlencode @encoded.bin

```

**Firmware update**


REQUEST

```
 curl --digest -u admin:7i8o9p0[ "http://<NVR-IP>/stw cgi/bypass.cgi?msubmenu=bypass&action=control&Channel=2&BypassURI=/stw cgi/system.cgi?msubmenu=firmwareupdate&action=control&Type=Normal" -H
 "Expect:" -F uploadFile=@pkg_v2.00_150114103354.img

```

**Sample requests and responses**


REQUEST

```
 http://<NVR-IP>/stw cgi/bypass.cgi?msubmenu=bypass&action=control&Channel=2&BypassURI=/stw cgi/eventstatus.cgi?msubmenu=eventstatus&action=check

```

RESPONSE

```
 Channel.0.Videoloss=False
 Channel.0.AudioDetection=False
 Channel.0.NetworkCameraConnect=True
 Channel.0.NetworkAlarmInput=False
 Channel.0.MotionDetection=False
 Channel.0.FaceDetection=False
 Channel.0.VideoAnalytics.Passing=False
 Channel.0.VideoAnalytics.Entering=False
 Channel.0.VideoAnalytics.Exiting=False
 Channel.0.VideoAnalytics.Appearing=False
 Channel.0.VideoAnalytics.Disappearing=False
 Channel.0.AMDStart=False
 Channel.0.LowFps=False

```

SUNAPI 65


```
 Channel.0.Tampering=False

```

REQUEST

```
 http://<NVR-IP>/stw cgi/bypass.cgi?msubmenu=bypass&action=control&Channel=2&BypassURI=/stw cgi/system.cgi?msubmenu=deviceinfo&action=view

```

RESPONSE

```
 Model=XXXXXXXX
 FirmwareVersion=XXXXXXXXXXX
 BuildDate=XXXXXXXXXX
 WebURL=XXXXXXXXXXX
 DeviceType=XXXXXXXX
 ConnectedMACAddress=XXXXXXXX
 CGIVersion=XXXXX
 MicomVersion=XXXXXXXXX
 DeviceName=XXXXXXXXXXX
 Language=XXXXXXXX

```

66 Application Programmer’s Guide


## **Chapter 14. Queue management**

**Check whether or not Queue Management feature is supported by device**


REQUEST

```
 http://<DeviceIP>/stw cgi/attributes.cgi/attributes/Recording/Support/QueueManagement

```

RESPONSE

```
 <attribute accesslevel="admin" value="True" type="bool" name="QueueManagemen
 t"/>

```

**Get maximum Queues supported by device**


REQUEST

```
 http://<DeviceIP>/stw cgi/attributes.cgi/attributes/Eventsource/Limit/MaxQueues

```

RESPONSE

```
 <attribute accesslevel="guest" value="3" type="int" name="MaxQueues"/>

```

**Get Queue Management setup**


REQUEST

```
 http://<DeviceIP>/stw cgi/eventsources.cgi?msubmenu=queuemanagementsetup&action=view

```

JSON RESPONSE

```
 {
 "QueueManagementSetup": [
 {
 "Channel": 0,
 "Enable": true,
 "ReportEnable": false,
 "ReportFilename": "",
 "ReportFileType": "XLS",
 "CalibrationMode": "CameraHeight",

```

SUNAPI 67


```
 "CameraHeight": 300,
 "ObjectSizeCoordinates": [
 {
 "x": 1316,
 "y": 1316
 },
 {
 "x": 1675,
 "y": 1675
 }
 ],
 "Queues": [
 {
 "Queue": 1,
 "MaxPeople": 8,
 "Name": "Queue1",
 "Enable": true,
 "Coordinates": [
 {
 "x": 1316,
 "y": 1596
 },
 {
 "x": 2991,
 "y": 1596
 }
 ],
 "QueueLevels": [
 {
 "Level": "High",
 "Count": 6,
 "AlarmEnable": true,
 "Threshold": 180
 },
 {
 "Level": "Medium",
 "Count": 3,
 "AlarmEnable": true,
 "Threshold": 180
 }
 ]

```

68 Application Programmer’s Guide


```
 },
 {
 "Queue": 2,
 "MaxPeople": 8,
 "Name": "Queue2",
 "Enable": true,
 "Coordinates": [
 {
 "x": 2316,
 "y": 2596
 },
 {
 "x": 3991,
 "y": 2596
 }
 ],
 "QueueLevels": [
 {
 "Level": "High",
 "Count": 6,
 "AlarmEnable": true,
 "Threshold": 180
 },
 {
 "Level": "Medium",
 "Count": 3,
 "AlarmEnable": true,
 "Threshold": 180
 }
 ]
 }
 ]
 }
 ]
 }

```

**To change the Queue Management setup**


REQUEST

```
 http://<DeviceIP>/stw-cgi/eventsources.cgi?msubmenu=queuemanagementsetup
 &action=set&Channel=0&Enable=True&CalibrationMode=CameraHeight&CameraHeight=

```

SUNAPI 69


```
 250

```

REQUEST

```
 http://<DeviceIP>/stw cgi/eventsources.cgi?msubmenu=queuemanagementsetup&action=set&Channel=0&Enab
 le=True&CalibrationMode=ObjectSize&ObjectSizeCoordinates=2992,1390,2,1390

```

REQUEST

```
 http://<DeviceIP>/stw cgi/eventsources.cgi?msubmenu=queuemanagementsetup&action=set&Channel=0&Repo
 rtEnable=True&ReportFileName=QueueReport&ReportFileType=XLS

```

**To change the Queue configuration**


REQUEST

```
 http://<DeviceIP>/stw cgi/eventsources.cgi?msubmenu=queuemanagementsetup&action=set&Channel=0&Queu
 e.1.Name=Queue1&Queue.1.Enable=True&Queue.1.Coordinates=1316,1596,2991,1596&
 Queue.1.Level.High.Count=6&Queue.1.Level.High.AlarmEnable=True&Queue.1.Level
 .High.Threshold=180&Queue.1.Level.Medium.AlarmEnable=True&Queue.1.Level.Medi
 um.Threshold=180&Queue.2.Name=Queue2&Queue.2.Enable=True&Queue.2.Coordinates
 =2316,2596,3991,2596&Queue.2.Level.High.Count=5&Queue.2.Level.High.AlarmEnab
 le=True&Queue.2.Level.High.Threshold=150&Queue.2.Level.Medium.AlarmEnable=Tr
 ue&Queue.2.Level.Medium.Threshold=150

```

**To get the current Queue levels of all Queues**


REQUEST

```
 http://<DeviceIP>/stw cgi/eventsources.cgi?msubmenu=queuemanagementsetup&action=check&Channel=0

```

JSON RESPONSE

```
 {
 "QueueCount": [
 {
 "Channel": 0,
 "Queues": [

```

70 Application Programmer’s Guide


```
 {
 "Queue": 1,
 "Count": 8
 },
 {
 "Queue": 2,
 "Count": 15
 },
 {
 "Queue": 3,
 "Count": 25
 }
 ]
 }
 ]
 }

```

**To get the current Queue levels of selected Queues**


REQUEST

```
 http://<DeviceIP>/stw cgi/eventsources.cgi?msubmenu=queuemanagementsetup&action=check&Channel=0&Qu
 eueIndex=1,2

```

JSON RESPONSE

```
 {
 "QueueCount": [
 {
 "Channel": 0,
 "Queues": [
 {
 "Queue": 1,
 "Count": 8
 },
 {
 "Queue": 2,
 "Count": 15
 }
 ]
 }

```

SUNAPI 71


```
 ]
 }

```

**To get the scheduler/event action for Queue Management**


REQUEST

```
 http://<DeviceIP>/stw cgi/eventrules.cgi?msubmenu=scheduler&action=view&Type=QueueManagement

```

TEXT RESPONSE

```
 Channel.0.QueueManagement.ScheduleType=Daily
 Channel.0.QueueManagement.Hour=00
 Channel.0.QueueManagement.Minute=00
 Channel.0.QueueManagement.WeekDay=SUN
 Channel.0.QueueManagement.EventAction= AlarmOutput.1,SMTP,FTP,
 Channel.0.QueueManagement.AlarmOutput.1.Duration=5s

```

JSON RESPONSE

```
 {
 "QueueManagement": [
 {
 "Channel": 0,
 "ScheduleType": "Daily",
 "Hour": 0,
 "Minute": 0,
 "WeekDay": "SUN",
 "EventAction": [
 "AlarmOutput.1",
 "SMTP",
 "FTP"
 ],
 "AlarmOutputs": [
 {
 "AlarmOutput": 1,
 "Duration": "5s"
 }
 ]
 }
 ]

```

72 Application Programmer’s Guide


```
 }

```

**To update the scheduler/event action for Queue Management**


REQUEST

```
 http://<DeviceIP>/stw cgi/eventrules.cgi?msubmenu=scheduler&action=set&Type=QueueManagement&Schedu
 leType=Weekly&WeekDay=MON

```

REQUEST

```
 http://<DeviceIP>/stw cgi/eventrules.cgi?msubmenu=scheduler&action=set&Type=QueueManagement&EventA
 ction=AlarmOutput.1&AlarmOutput.1.Duration=20s

```

REQUEST

```
 http://<DeviceIP>/stw cgi/eventrules.cgi?msubmenu=scheduler&action=set&Type=QueueManagement&EventA
 ction=FTP,SMTP

```

**To get the supported event actions for Queue Management**


REQUEST

```
 http://<DeviceIP>/stw cgi/eventsources.cgi?msubmenu=sourceoptions&action=view

```

TEXT RESPONSE

```
 EventSource.QueueManagement.EventAction=FTP,SMTP,AlarmOutput

```

JSON RESPONSE

```
 {
 "EventSources": [
 {
 "EventSource": "QueueManagement",
 "EventAction": [
 "FTP",
 "SMTP",

```

SUNAPI 73


```
 "AlarmOutput"
 ]
 }
 ]
 }

```

**To check the current Queue event status**


REQUEST

```
 http://<DeviceIP>/stw cgi/eventstatus.cgi?msubmenu=eventstatus&action=check&Channel.0.EventType=Qu
 eueEvent

```

TEXT RESPONSE (All events)

```
 Channel.0.Queue.1.Level.High=True
 Channel.0.Queue.1.Level.Medium=False
 Channel.0.Queue.2.Level.High=False
 Channel.0.Queue.2.Level.Medium=False

```

JSON RESPONSE (All events)

```
 {
 "ChannelEvent": [
 {
 "Channel": 0,
 "QueueEvents": {
 "Queues": [
 {
 "Queue": 1,
 "QueueLevels": [
 {
 "High": true
 },
 {
 "Medium": false
 }
 ]
 },
 {
 "Queue": 2,

```

74 Application Programmer’s Guide


```
 "QueueLevels": [
 {
 "High": false
 },
 {
 "Medium": false
 }
 ]
 }
 ]
 }
 }
 ]
 }

```

**To monitor the status of Queue events**


REQUEST

```
 http://<DeviceIP>/stw cgi/eventstatus.cgi?msubmenu=eventstatus&action=monitor&Channel.0.EventType=
 QueueEvent

```

REQUEST

```
 http://<DeviceIP>/stw cgi/eventstatus.cgi?msubmenu=eventstatus&action=monitordiff&Channel.0.EventT
 ype=QueueEvent

```

TEXT RESPONSE (Single event)

```
 Channel.0.Queue.1.Level.High=True

```

JSON RESPONSE (Single event)

```
 {
 "ChannelEvent": [
 {
 "Channel": 0,
 "QueueEvents": {
 "Queues": [
 {

```

SUNAPI 75


```
 "Queue": 1,
 "QueueLevels": [
 {
 "High": true
 }
 ]
 }
 ]
 }
 }
 ]
 }

```

**To start a Queue search**


REQUEST

```
 http://<DeviceIP>/stw cgi/recording.cgi?msubmenu=queuesearch&action=control&Channel=0&Mode=Start&F
 romDate=2017-01-17T00:00:00Z&ToDate=2017-01 17T23:59:59Z&Queue.1.AveragePeople=True&Queue.2.AveragePeople=True&Queue.3.A
 veragePeople=True

```

REQUEST

```
 http://<DeviceIP>/stw cgi/recording.cgi?msubmenu=queuesearch&action=control&Channel=0&Mode=Start&F
 romDate=2017-01-17T00:00:00Z&ToDate=2017-01 17T23:59:59Z&Queue.1.Type.High.CumulativeTime=True&Queue.1.Type.Medium.Cumul
 ativeTime=True&Queue.2.Type.High.CumulativeTime=True&Queue.2.Type.Medium.Cum
 ulativeTime=True&Queue.3.Type.High.CumulativeTime=True&Queue.3.Type.Medium.C
 umulativeTime=True

```

REQUEST

```
 http://<DeviceIP>/stw cgi/recording.cgi?msubmenu=queuesearch&action=control&Channel=0&Mode=Start&F
 romDate=2017-01-17T00:00:00Z&ToDate=2017-01 17T23:59:59Z&Queue.1.AveragePeople=True&Queue.2.AveragePeople=True&Queue.3.A
 veragePeople=True&Queue.1.Type.High.CumulativeTime=True&Queue.1.Type.Medium.
 CumulativeTime=True&Queue.2.Type.High.CumulativeTime=True&Queue.2.Type.Mediu
 m.CumulativeTime=True&Queue.3.Type.High.CumulativeTime=True&Queue.3.Type.Med

```

76 Application Programmer’s Guide


```
 ium.CumulativeTime=True

```

JSON RESPONSE

```
 {
 "SearchToken": "123456"
 }

```

**To cancel a Queue search**


REQUEST

```
 http://<DeviceIP>/stw cgi/recording.cgi?msubmenu=queuesearch&action=control&Channel=0&Mode=Cancel

```

JSON RESPONSE

```
 {
 "Response": "Success"
 }

```

**To get status of a Queue search**


REQUEST

```
 http://<DeviceIP>/stw cgi/recording.cgi?msubmenu=queuesearch&action=view&Type=Status&SearchToken=1
 23456

```

JSON RESPONSE

```
 {
 "Status": "Completed"
 }

```

**To get the results of a Queue search for average People**


REQUEST

```
 http://<DeviceIP>/stw cgi/recording.cgi?msubmenu=queuesearch&action=view&Type=Results&SearchToken=
 123456

```

SUNAPI 77


JSON RESPONSE

```
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
 "0",
 "1",
 "2",
 "3",
 "4",

```

78 Application Programmer’s Guide


```
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
 "12",
 "13",
 "14",
 "15",
 "16",

```

SUNAPI 79


```
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

**To get the results of a Queue search for Cumulative Time**


REQUEST

```
 http://<DeviceIP>/stw cgi/recording.cgi?msubmenu=queuesearch&action=view&Type=Results&SearchToken=
 123456

```

JSON RESPONSE

```
 {
 "ResultInterval": "Hourly",
 "QueueResults": [
 {
 "Queue": 1,
 "QueueLevels": [
 {
 "Level": "High",
 "CumulativeTimeResult": [
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

```

80 Application Programmer’s Guide


```
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
 "Level": "Medium",
 "CumulativeTimeResult": [
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

```

SUNAPI 81


```
 "23"
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
 "Level": "Medium",
 "CumulativeTimeResult": [
 "0",

```

82 Application Programmer’s Guide


```
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
 }
 ]
 },
 {
 "Queue": 3,
 "QueueLevels": [
 {
 "Level": "High",
 "CumulativeTimeResult": [
 "0",
 "1",
 "2",
 "3",
 "4",
 "5",
 "6",
 "7",

```

SUNAPI 83


```
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
 "Level": "Medium",
 "CumulativeTimeResult": [
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

```

84 Application Programmer’s Guide


```
 "20",
 "21",
 "22",
 "23"
 ]
 }
 ]
 }
 ]
 }

```

**To get the results of a Queue search for Cumulative Time and Average People**


JSON RESPONSE

```
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

```

SUNAPI 85


```
 "21",
 "22",
 "23"
 ],
 "QueueLevels": [
 {
 "Level": "High",
 "CumulativeTimeResult": [
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
 "Level": "Medium",
 "CumulativeTimeResult": [
 "0",
 "1",
 "2",
 "3",

```

86 Application Programmer’s Guide


```
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
 }
 ]
 },
 {
 "Queue": 2,
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

```

SUNAPI 87


```
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
 ],
 "QueueLevels": [
 {
 "Level": "High",
 "CumulativeTimeResult": [
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

```

88 Application Programmer’s Guide


```
 {
 "Level": "Medium",
 "CumulativeTimeResult": [
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
 }
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

```

SUNAPI 89


```
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
 ],
 "QueueLevels": [
 {
 "Level": "High",
 "CumulativeTimeResult": [
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

```

90 Application Programmer’s Guide


```
 "19",
 "20",
 "21",
 "22",
 "23"
 ]
 },
 {
 "Level": "Medium",
 "CumulativeTimeResult": [
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
 }
 ]
 }
 ]
 }

```

SUNAPI 91


## **Chapter 15. People Count**

**Capabilities**

```
 http://<DeviceIP>/stw cgi/attributes.cgi/attributes/Recording/Support/PeopleCountSearch

 <attribute name="PeopleCountSearch" accesslevel="user" value="True"
 type="bool"/>

```

**Get People Count configuration**


REQUEST

```
 http://<DeviceIP>/stw-cgi/eventsources.cgi?msubmenu=peoplecount&action=view

```

TEXT RESPONSE

```
 Channel.0.MasterName=PeopleCount-Master
 Channel.0.Enable=True
 Channel.0.ReportEnable=True
 Channel.0.ReportFilename=peoplecountreport
 Channel.0.ReportFileType=XLSX
 Channel.0.CalibrationMode=CameraHeight
 Channel.0.CameraHeight=300
 Channel.0.ObjectSizeCoordinate=1316,1316,1675,1675
 Channel.0.Line.1.Name=Gate1
 Channel.0.Line.1.Enable=True
 Channel.0.Line.1.Mode=LeftToRightIn
 Channel.0.Line.1.Coordinate=1043,1875,2875,1943
 Channel.0.Line.2.Name=Gate2
 Channel.0.Line.2.Enable=True
 Channel.0.Line.2.Mode=LeftToRightIn
 Channel.0.Line.2.Coordinate=2912,893,1206,706

```

JSON RESPONSE

```
 {
 "PeopleCount": [
 {
 "Channel": 0,

```

92 Application Programmer’s Guide


```
 "MasterName": "PeopleCount-Master",
 "Enable": true,
 "ReportEnable": true,
 "ReportFilename": "peoplecountreport",
 "ReportFileType": "XLSX",
 "CalibrationMode": "CameraHeight",
 "CameraHeight": 300,
 "ObjectSizeCoordinate": [
 {
 "x": 1316,
 "y": 1316
 },
 {
 "x": 1675,
 "y": 1675
 }
 ],
 "Lines": [
 {
 "Line": 1,
 "Mode": "LeftToRightIn",
 "Name": "Gate1",
 "Enable": true,
 "Coordinates": [
 {
 "x": 1043,
 "y": 1875
 },
 {
 "x": 2875,
 "y": 1943
 }
 ]
 },
 {
 "Line": 2,
 "Mode": "LeftToRightIn",
 "Name": "Gate2",
 "Enable": true,
 "Coordinates": [
 {

```

SUNAPI 93


```
 "x": 2912,
 "y": 893
 },
 {
 "x": 1206,
 "y": 706
 }
 ]
 }
 ]
 }
 ]
 }

```

**To update the configuration**

```
 http://<DeviceIP>/stw cgi/eventsources.cgi?msubmenu=peoplecount&action=set&Channel=0&Enable=True&C
 alibrationMode=CameraHeight&CameraHeight=250

 http://<DeviceIP>/stw cgi/eventsources.cgi?msubmenu=peoplecount&action=set&Channel=0&Enable=True&C
 alibrationMode=ObjectSize&ObjectSizeCoordinates=2992,1390,2,1390

 http://<DeviceIP>/stw cgi/eventsources.cgi?msubmenu=peoplecount&action=set&Channel=0&Line.1.Name=F
 rontGate&Line.1.Enable=True&Line.1.Mode=LeftToRightIn&Line.1.Coordinates=1,2
,3,4&Line.2.Name=BackGate&Line.2.Enable=True&Line.2.Mode=RightToLeftIn&Line.
 2.Coordinates=5,6,7,8

 http://<DeviceIP>/stw cgi/eventsources.cgi?msubmenu=peoplecount&action=set&Channel=0&ReportEnable=
 True&ReportFileName=PeopleCountReport&ReportFileType=TXT

```

**To remove exclude region**

```
 http://<DeviceIP>/stw cgi/eventsources.cgi?msubmenu=peoplecount&action=remove&Channel=0&AreaIndex=

```

94 Application Programmer’s Guide


```
 1

```

**To check the live people count**

```
 http://<DeviceIP>/stw cgi/eventsources.cgi?msubmenu=peoplecount&action=check&Channel=0

```

JSON RESPONSE

```
 {
 "PeopleCount": [
 {
 "Lines": [
 {
 "LineIndex": 1,
 "Name": "Gate1",
 "InCount": 20,
 "OutCount": 15
 },
 {
 "LineIndex": 2,
 "Name": "Gate2",
 "InCount": 56,
 "OutCount": 52
 }
 ]
 }
 ]
 }

```

TEXT RESPONSE

```
 Channel.0.LineIndex=1
 Channel.0.LineIndex.1.Name=Gate1
 Channel.0.LineIndex.1.InCount=20
 Channel.0.LineIndex.1.OutCount=15
 Channel.0.LineIndex=2
 Channel.0.LineIndex.2.Name=Gate2
 Channel.0.LineIndex.2.InCount=56
 Channel.0.LineIndex.2.OutCount=52

```

SUNAPI 95


**To start a People Count search**


People count search is an asynchronous search, initially search session is started as below, resulting

search token is used later to check search status and to get the results.


Here, PeopleCount-Master is **fixed** name for the camera
**NOTE**

whereas, Gate1 or Gate2 is actual name of the line in configuration.


REQUEST

```
 http://<DeviceIP>/stw cgi/recording.cgi?msubmenu=peoplecountsearch&action=control&Channel=0&Mode=S
 tart&FromDate=2016-07-01T00:00:00Z&ToDate=2016-07 01T23:59:59Z&Camera.PeopleCount Master.Line.Gate1.Direction=In,Out&Camera.MasterCamera.Line.Gate2.Direction=
 In,Out

```

RESPONSE

```
 {
 "SearchToken": "PeopleCount-2016-07-24T02:32:51-614"
 }

```

**To cancel the People Count search**


REQUEST

```
 http://<DeviceIP>/stw cgi/recording.cgi?msubmenu=peoplecountsearch&action=control&Mode=Cancel&Sear
 chToken=PeopleCount-2016-07-24T02:32:51-614

```

RESPONSE

```
 {
 "Response": "Success"
 }

```

**To get the status of a People Count search**


REQUEST

```
 http://<DeviceIP>/stw cgi/recording.cgi?msubmenu=peoplecountsearch&action=view&Type=Status&SearchT

```

96 Application Programmer’s Guide


```
 oken=PeopleCount-2016-07-24T02:32:51-614

```

RESPONSE

```
 {
 "Status": "Completed"
 }

```

**To get the results of a People Count search**


REQUEST

```
 http://<DeviceIP>/stw cgi/recording.cgi?msubmenu=peoplecountsearch&action=view&Type=Results&Search
 Token=PeopleCount-2016-07-24T02:32:51-614

```

JSON RESPONSE

```
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

```

SUNAPI 97


```
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

```

TEXT RESPONSE

```
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

98 Application Programmer’s Guide


## **Chapter 16. Thermal Camera Integration**

The purpose of this section is to help quick integration; however, for detailed explanation
**NOTE**

of parameters, it is recommended to refer to the corresponding cgi documents

### **16.1. Attributes**

In attributes cgi response, under Image and Support sections, you can check the below attributes for the

thermal feature support:

```
 <attribute accesslevel="guest" value="True" type="bool" name="ThermalFeature
 s"/>

### **16.2. Color Palette Selection & Temperature Unit Selection**
```

**Supported Color Palettes:**

```
 WhiteHot, BlackHot, Rainbow, Custom, Sepia, Red, Iron

```

**Supported Temperature Units:**

```
 Celsius, Fahrenheit

#### **16.2.1. View**

 http://<Device IP>/stw-cgi/image.cgi?msubmenu=camera&action=view

 {
 "Camera": [
 {
 "Channel": 0,
 "CompensationMode": "Off",
 "SSNREnable": true,
 "SSNRMode": "Manual",
 "SSNRLevel": 12,
 "SSNR2DLevel": 12,
 "SSNR3DLevel": 12,
 "ThermalColorPalette": "Rainbow",
 "TemperatureUnit": "Celsius",

```

SUNAPI 99


```
 "DayNightAlarmIn": "SwitchToBWIfCloses",
 "WDRSeamlessTransition": "Off",
 "WDRLowLight": "Off",
 "WDRIRLEDEnable": "Off"
 }
 ]
 }

#### **16.2.2. Set Operation**
```

To change the color palette

```
 http://<Device IP>/stw cgi/image.cgi?msubmenu=camera&action=set&ThermalColorPalette=Sepia

### **16.3. Temperature Change Detection**

#### **16.3.1. Attributes**
```

In the Eventsource Support section, check the following:

```
 <attribute accesslevel="guest" value="True" type="bool" name="TemperatureCha
 ngeDetection"/>

```

To get MAX ROI support, under the Eventsource Limit section, check the following:

```
 <attribute accesslevel="guest" value="3" type="int" name="MaxTemperatureChan
 geDetectionArea"/>

### **16.4. Configuring Temperature Change Detection**

#### **16.4.1. Options Command**
```

This gives the supported gap both in Celsius and Fahrenheit.

```
 http://<Device IP>/stw cgi/eventsources.cgi?msubmenu=temperaturechangedetectionoptions&action=view

 {
 "TemperatureChangeDetectionOption": [

```

100 Application Programmer’s Guide


```
 {
 "Channel": 0,
 "SupportedGap": {
 "Celsius": "20,40,60,80,100",
 "Fahrenheit": "40,80,120,160,200"
 }
 }
 ]
 }

#### **16.4.2. Enable**

 http://<Device IP>/stw cgi/eventsources.cgi?msubmenu=temperaturechangedetection&action=set&Channel=
 0&Enable=True

#### **16.4.3. Set**
```

Can set the reference temperature to Average, Maximum, or Minimum temperature in the ROI.


Example:


If Average temperature in the ROI changes more than 60 degrees over 11 secs, it will trigger an event.

```
 http://<Device IP>/stw cgi/eventsources.cgi?msubmenu=temperaturechangedetection&action=set&Channel=
 0&TemperatureChange.ROI.1.Mode=Average&TemperatureChange.ROI.1.Gap=60&Temper
 atureChange.ROI.1.DetectionPeriod=11&TemperatureChange.ROI.1.Coordinates=142
,176,477,386

#### **16.4.4. View**

 http://<Device IP>/stw cgi/eventsources.cgi?msubmenu=temperaturechangedetection&action=view

 {
 "TemperatureChangeDetection": [
 {
 "Channel": 0,
 "Enable": true,

```

SUNAPI 101


```
 "TemperatureChange": [
 {
 "ROI": 1,
 "Mode": "Average",
 "Gap": 60,
 "DetectionPeriod": 11,
 "Coordinates": [
 {
 "x": 142,
 "y": 176
 },
 {
 "x": 477,
 "y": 386
 }
 ]
 }
 ]
 }
 ]
 }

### **16.5. TemperatureChange Detection Event Format**

 <wsnt:NotificationMessage>
 <wsnt:Topic
 Dialect="http://www.onvif.org/ver10/tev/topicExpression/ConcreteSet">tns1:Vi
 deoSource/tnssamsung:TemperatureChangeDetection</wsnt:Topic>
 <wsnt:Message>
 <tt:Message UtcTime="2018-03-29T11:01:40.857Z">
 <tt:Source>
 <tt:SimpleItem Name="VideoSource" Value="VideoSourceToken 01"/>
 <tt:SimpleItem Name="RuleName" Value="TemperatureChange-1"/>
 </tt:Source>
 <tt:Data>
 <tt:SimpleItem Name="State" Value="true"/>
 </tt:Data>
 </tt:Message>
 </wsnt:Message>

```

102 Application Programmer’s Guide


```
 </wsnt:NotificationMessage>

```

In radiometry-supported models like TNO-4030TR, the following additional submenus are supported.

### **16.6. Spot Temperature Reading**

For reading the temperature of the screen coordinates.

```
 http://<IP>/stw cgi/image.cgi?msubmenu=spottemperaturereading&action=view&Channel=0&ScreenRe
 solution=640x480&ScreenCoordinates=334,216

```

Sample response

```
 {
 "SpotTemperatureReading": [
 {
 "Channel": 0,
 "Temperature": 30,
 "Unit": "Celsius"
 }
 ]
 }

### **16.7. BoxTemperatureDetection**
```

Can configure a region to monitor avg, min, and max temperature within that region.


The **boxtemperaturedetection** submenu configures box temperature detection settings.

```
 http://<Device IP>/stw cgi/eventsources.cgi?msubmenu=boxtemperaturedetection&action=view&Channel=0

 {
 "BoxTemperatureDetection": [
 {
 "Channel": 0,
 "Enable": true,
 "ROIs": [
 {
 "ROI": 1,

```

SUNAPI 103


```
 "TemperatureType": "Average",
 "DetectionType": "Above",
 "ThresholdTemperature": 39,
 "Coordinates": [
 {
 "x": 43,
 "y": 23
 },
 {
 "x": 274,
 "y": 243
 }
 ],
 "Duration": 40,
 "NormalizedEmissivity": 27,
 "AreaOverlay": false,
 "AvgTemperatureOverlay": true,
 "MinTemperatureOverlay": true,
 "MaxTemperatureOverlay": true
 },
 {
 "ROI": 2,
 "TemperatureType": "Maximum",
 "DetectionType": "Increase",
 "ThresholdTemperature": 20,
 "Coordinates": [
 {
 "x": 364,
 "y": 42
 },
 {
 "x": 556,
 "y": 236
 }
 ],
 "Duration": 48,
 "NormalizedEmissivity": 40,
 "AreaOverlay": true,
 "AvgTemperatureOverlay": true,
 "MinTemperatureOverlay": true,
 "MaxTemperatureOverlay": false

```

104 Application Programmer’s Guide


```
 },
 {
 "ROI": 3,
 "TemperatureType": "Minimum",
 "DetectionType": "Below",
 "ThresholdTemperature": 5,
 "Coordinates": [
 {
 "x": 319,
 "y": 307
 },
 {
 "x": 562,
 "y": 451
 }
 ],
 "Duration": 39,
 "NormalizedEmissivity": 41,
 "AreaOverlay": true,
 "AvgTemperatureOverlay": false,
 "MinTemperatureOverlay": true,
 "MaxTemperatureOverlay": true
 }
 ]
 }
 ]
 }

#### **16.7.1. Changing Box Temperature Detection Settings**
```

REQUEST

```
 http://<Device IP>/stw cgi/eventsources.cgi?msubmenu=boxtemperaturedetection&action=set&Channel=0&R
 OI.1.Coordinate=63,37,346,205&ROI.1.TemperatureType=Maximum&ROI.1.DetectionT
 ype=Above&ROI.1.ThresholdTemperature=10&ROI.1.Duration=26&ROI.1.NormalizedEm
 issivity=33&ROI.1.AreaOverlay=True&ROI.1.AvgTemperatureOverlay=True&ROI.1.Mi
 nTemperatureOverlay=True&ROI.1.MaxTemperatureOverlay=True

#### **16.7.2. Removing Box Temperature Detection ROI Region 1**

```

SUNAPI 105


REQUEST

```
 http://<Device IP>/stw cgi/eventsources.cgi?msubmenu=boxtemperaturedetection&action=remove&ROIIndex
 =1&Channel=0

#### **16.7.3. BoxTemperatureDetectionOptions**

 http://<Device IP>/ stw cgi/eventsources.cgi?msubmenu=boxtemperaturedetectionoptions&action=view&Cha
 nnel=0

 {
 "BoxTemperatureDetectionOptions": [
 {
 "Channel": 0,
 "ThresholdTemperature": [
 {
 "TemperatureType": "Above",
 "Celsius": {
 "Min": -20,
 "Max": 130
 },
 "Fahrenheit": {
 "Min": -4,
 "Max": 266
 }
 },
 {
 "TemperatureType": "Below",
 "Celsius": {
 "Min": -20,
 "Max": 130
 },
 "Fahrenheit": {
 "Min": -4,
 "Max": 266
 }
 },
 {

```

106 Application Programmer’s Guide


```
 "TemperatureType": "Increase",
 "Celsius": {
 "Min": 10,
 "Max": 100
 },
 "Fahrenheit": {
 "Min": 50,
 "Max": 212
 }
 },
 {
 "TemperatureType": "Decrease",
 "Celsius": {
 "Min": 10,
 "Max": 100
 },
 "Fahrenheit": {
 "Min": 50,
 "Max": 212
 }
 }
 ]
 }
 ]
 }

#### **16.7.4. Box Temperature Metadata Reading (Available only as Metadata)**

 <tt:MetadataStream>
 <tt:Event>
 <wsnt:NotificationMessage>
 <wsnt:Topic
 Dialect="http://www.onvif.org/ver10/tev/topicExpression/ConcreteSet">tns1:Vi
 deoAnalytics/Radiometry/BoxTemperatureReading</wsnt:Topic>
 <wsnt:Message>
 <tt:Message UtcTime="2018-09-19T04:08:46.443Z">
 <tt:Source>
 <tt:SimpleItem Name="VideoSourceToken"
 Value="VideoSourceToken-01"/>
 <tt:SimpleItem
 Name="VideoAnalyticsConfigurationToken" Value="VideoAnalyticsConfigToken
```

SUNAPI 107


```
 01"/>
 <tt:SimpleItem Name="AnalyticsModuleName"
 Value="TemparetureDetectionModule-01"/>
 </tt:Source>
 <tt:Data>
 <tt:ElementItem Name="Reading">
 <ttr:BoxTemperatureReading ItemID="1"
 MaxTemperature="275.9" MinTemperature="275.5" AverageTemperature="275.7"/>
 </tt:ElementItem>
 <tt:SimpleItem Name="TimeStamp" Value="2018-09 19T04:08:46.443Z"/>
 </tt:Data>
 </tt:Message>
 </wsnt:Message>
 </wsnt:NotificationMessage>
 </tt:Event>
 </tt:MetadataStream>

#### **16.7.5. Box temperature Event**

 <wsnt:NotificationMessage>
 <wsnt:Topic
 Dialect="http://www.onvif.org/ver10/tev/topicExpression/ConcreteSet
 xmlns:wsnt=http://docs.oasis-open.org/wsn/b-2
 xmlns:tns1=http://www.onvif.org/ver10/topics
 xmlns:tnssamsung=http://www.samsungcctv.com/2011/event/topics">tns1:RuleEngi
 ne/Radiometry/TemperatureAlarm</wsnt:Topic>
 <wsnt:Message>
 <tt:Message UtcTime="2016-03-31T00:15:58.421Z"
 PropertyOperation="Initialized">
 <tt:Source>
 <tt:SimpleItem Name="VideoSourceToken"
 Value="VideoSourceConfigToken-01-0"/>
 <tt:SimpleItem Name="VideoSourceConfigurationToken"
 Value="cb4fbc38-e5f6-4ff0-b2e8-2e166b4414d1"/>
 <tt:SimpleItem Name="RuleName" Value="TemperatureDetection 1"/>
 <tt:SimpleItem Name="AreaName" Value="Area-1"/>
 </tt:Source>
 <tt:Data>
 <tt:SimpleItem Name="AlarmActive" Value="false"/>

```

108 Application Programmer’s Guide


```
 <tt:SimpleItem Name="TimeStamp" Value="2022-01 01T01:19:13.832Z"/>
 </tt:Data>
 </tt:Message>
 </wsnt:Message>
 </wsnt:NotificationMessage>

#### **16.7.6. SUNAPI Event Status**
```

Check

```
 http://<Device IP>/stw-cgi/eventstatus.cgi?msubmenu=eventstatus&action=check

```

Monitor

```
 http://<Device IP>/stw cgi/eventstatus.cgi?msubmenu=eventstatus&action=monitor

```

Monitor diff

```
 http://<Device IP>/stw cgi/eventstatus.cgi?msubmenu=eventstatus&action=monitordiff

```

The event would be delivered as below:

```
 Channel.0.BoxTemperatureDetection=True
 Channel.0.BoxTemperatureDetection.RegionID.1=True

```

SUNAPI 109


## **Chapter 17. Dual Channel Thermal Camera** **Integration**
### **17.1. Overview**

#### **17.1.1. Dual Channel**

TNM-3620TDY has two channels, each looking in the same direction and filming the same scene,

consisting of one visible channel and one thermal channel. The first channel is a general image channel,

and the second channel is a thermal imaging channel.

#### **17.1.2. Thermal Image Position Calibration**

You can start a calibration process to compensate for the difference in image resolution and the minute

position error between the two channels. Refer to image cgi stereosensorcalibrarion submenu.

#### **17.1.3. Thermal Detection Mode**

TNM-3620TDY has two different thermal detection modes: Body Temperature Detection mode and Normal

mode. Other events are restricted while the camera is running in the Body Temperature Detection mode.

The Normal mode provides the same way of representing events as before, such as Box Temperature

Detection. If the thermal detection mode changes, the attributes of the camera will also change, and it can

detect through the AttributeUpdate event. Refer to eventsources cgi thermaldetectionmode submenu.


Note that changing the thermal detection mode means changing to a completely different camera

(because supported events and image settings change depending on the mode), so it is recommended to

re-register your surveillance system.

### **17.2. Estimated Body Temperature Detection**

#### **17.2.1. Body Temperature Detection**

The Body Temperature Detection mode is a mode in which the temperature in a specific area is measured

by recognizing a person’s face. This event setting can only be set for the second channel, "thermal

channel," but the event is triggered identically on both channels. Refer to eventsources cgi

bodytemperaturedetection submenu for configuring the body temperature detection settings

#### **17.2.2. Temperature Measurement Region Setting**

The body temperature value is measured within the detected face area square. With the temperature

measurement region setting, the user can adjust the size and position of the detected face area square to

measure the body temperature value. Refer to eventsources cgi temperaturemeasurementregion

submenu for changing the temperature measurement region settings

#### **17.2.3. Improve Temperature Measurement Accuracy using blackbody device**

TNM-3620TDY provides blackbody and radiometry settings. It is used to improve the accuracy of body

temperature measurement. These settings work only when the camera is running in the Body


110 Application Programmer’s Guide


Temperature Detection mode. Refer to imagge cgi blackbodyconfig submenu for changing the settings.

#### **17.2.4. Supported Events difference-based thermal detection mode**

Supported events vary depending on the thermal detection mode set for the camera, and supported

events are different for each channel; you can check image information for each channel using the

following command:


[http://<Device IP>/stw-cgi/attributes.cgi/attributes/Eventsource/Support](http://<Device)


You can check whether the newly added BodyTemperatureDetection feature is supported with the

following command:

```
 http://<Device IP>/stw cgi/attributes.cgi/attributes/Eventsource/Support/[ChannelID]/
 BodyTemperatureDetection

```





|Supported Events|Normal Mode|Body Temperature Mode|
|---|---|---|
|Temperature detection|O|X|
|Motion detection|O|X|
|Tampering detection|O|X|
|IVA|O|X|
|Audio detection|O|X|
|Estimated body temperature<br>detection|X|O|


### **17.3. Sample ONVIF Event for Body temperature detection**

**NOTE** Temperature measured in Kelvin

```
 <wsnt:NotificationMessage xmlns:wsnt="http://docs.oasis-open.org/wsn/b-2">
 <wsnt:Topic
 Dialect="http://www.onvif.org/ver10/tev/topicExpression/ConcreteSet
 xmlns:wsnt=http://docs.oasis-open.org/wsn/b-2
 xmlns:tns1=http://www.onvif.org/ver10/topics">tns1:RuleEngine/Detection/Body
 Temperature</wsnt:Topic>
 <wsnt:Message>
 <tt:Message UtcTime="2020-07-14T15:54:44Z"
 xmlns:tt="https://www.onvif.org/ver10/schema/">
 <tt:Source>
 <tt:SimpleItem Name="VideoSource" Value="VideoSouceToken
```

SUNAPI 111


```
 1"/>
 <tt:SimpleItem Name="RuleName"
 Value="BodyTemperatureDetectionRule-1"/>
 </tt:Source>
 <tt:Data>
 <tt:SimpleItem Name="State" Value="true"/>
 <tt:SimpleItem Name="ObjectID" Value="100023"/>
 <tt:SimpleItem Name="Temperature" Value="312.0"/>
 </tt:Data>
 </tt:Message>
 </wsnt:Message>
 </wsnt:NotificationMessage>

### **17.4. BodyTemperatureDetection SUNAPI event status** **example**
```

REQUEST

```
 http://<Device IP>/stw-cgi/eventstatus.cgi?msubmenu=eventstatus&action=check

```

TEXT RESPONSE

```
 HTTP/1.0 200 OK
 Content-type: text/plain
 <Body>

 AlarmInput.1=False
 AlarmOutput.1=False
 AlarmOutput.2=False
 Channel.0.BodyTemperatureDetection=True
 Channel.1.BodyTemperatureDetection=True
 SystemEvent.TimeChange=False
 SystemEvent.PowerReboot=False
 SystemEvent.FWUpdate=False
 SystemEvent.FactoryReset=False
 SystemEvent.ConfigurationBackup=False
 SystemEvent.ConfigurationRestore=False
 SystemEvent.ConfigChange=False
 SystemEvent.SDFormat=False
 SystemEvent.SDFail=False

```

112 Application Programmer’s Guide


```
 SystemEvent.SDFull=False
 SystemEvent.SDInsert=False
 SystemEvent.SDRemove=True
 SystemEvent.NASConnect=False
 SystemEvent.NASDisconnect=True
 SystemEvent.NASFail=False
 SystemEvent.NASFull=False
 SystemEvent.NASFormat=False

```

JSON RESPONSE

```
 HTTP/1.0 200 OK
 Content-type: application/json
 <Body>

 {
 "AlarmInput": {
 "1": false
 },
 "AlarmOutput": {
 "1": false,
 "2": false
 },
 "ChannelEvent": [
 {
 "Channel": 0,
 "BodyTemperatureDetection": true
 },
 {
 "Channel": 1,
 "BodyTemperatureDetection": true
 }
 ],
 "SystemEvent": {
 "TimeChange": false,
 "PowerReboot": false,
 "FWUpdate": false,
 "FactoryReset": false,
 "ConfigurationBackup": false,
 "ConfigurationRestore": false,
 "ConfigChange": false,

```

SUNAPI 113


```
 "SDFormat": false,
 "SDFail": false,
 "SDFull": false,
 "SDInsert": false,
 "SDRemove": true,
 "NASConnect": false,
 "NASDisconnect": true,
 "NASFail": false,
 "NASFull": false,
 "NASFormat": false
 }
 }

### **17.5. BodyTemperatureDetection SUNAPI schema-based** **event status example**

#### **17.5.1. Getting event status schema of body temperature detection**
```

REQUEST

```
 http://<Device IP>/stw-cgi/ stw cgi/eventstatus.cgi?msubmenu=eventstatusschema&action=view&EventName=BodyTem
 peratureDetection

```

TEXT RESPONSE

```
 HTTP/1.0 200 OK
 Content-type: text/plain
 <Body>

 EventStatus.1.Name=BodyTemperatureDetection
 EventStatus.1.Schema.1.Name=Channel.<int>.BodyTemperatureDetection
 EventStatus.1.Schema.1.Value=<boolean>

```

JSON RESPONSE

```
 HTTP/1.0 200 OK
 Content-type: application/json
 <Body>

```

114 Application Programmer’s Guide


```
 {
 "type": "array",
 "items": [
 {
 "type": "object",
 "properties": {
 "Time": {
 "type": "string"
 },
 "EventName": {
 "enum": [
 "BodyTemperatureDetection"
 ]
 },
 "Source": {
 "type": "object",
 "properties": {
 "Channel": {
 "type": "number"
 },
 }
 },
 "Data": {
 "type": "object",
 "properties": {
 "State": {
 "type": "boolean"
 }
 }
 }
 }
 }
 ]
 }

#### **17.5.2. Getting scheme-based event status**
```

REQUEST

```
 http://<Device IP>/stw cgi/eventstatus.cgi?msubmenu=eventstatus&action=check&SchemaBased=True

```

SUNAPI 115


TEXT RESPONSE

```
 HTTP/1.0 200 OK
 Content-type: text/plain
 <Body>

 AlarmInput.1=False
 AlarmOutput.1=False
 AlarmOutput.2=False
 Channel.0.BodyTemperatureDetection=True
 Channel.1.BodyTemperatureDetection=True
 SystemEvent.TimeChange=False
 SystemEvent.PowerReboot=False
 SystemEvent.FWUpdate=False
 SystemEvent.FactoryReset=False
 SystemEvent.ConfigurationBackup=False
 SystemEvent.ConfigurationRestore=False
 SystemEvent.ConfigChange=False
 SystemEvent.SDFormat=False
 SystemEvent.SDFail=False
 SystemEvent.SDFull=False
 SystemEvent.SDInsert=False
 SystemEvent.SDRemove=True
 SystemEvent.NASConnect=False
 SystemEvent.NASDisconnect=True
 SystemEvent.NASFail=False
 SystemEvent.NASFull=False
 SystemEvent.NASFormat=False

```

JSON RESPONSE

```
 HTTP/1.0 200 OK
 Content-type: application/json
 <Body>

 {
 "EventStatus": [
 {
 "EventName": "AlarmOutput",
 "Time": "2020-08-20T12:03:08.454+00:00",

```

116 Application Programmer’s Guide


```
 "Source": {
 "Channel": 0
 },
 "Data": {
 "State": false
 }
 },
 {
 "EventName": "BodyTemperatureDetection",
 "Time": "2020-08-20T12:03:08.454+00:00",
 "Source": {
 "Channel": 0
 },
 "Data": {
 "State": false
 }
 },
 {
 "EventName": "BodyTemperatureDetection",
 "Time": "2020-08-20T12:03:08.454+00:00",
 "Source": {
 "Channel": 1
 },
 "Data": {
 "State": false
 }
 },
 {
 "EventName": "SystemEvent.TimeChange",
 "Time": "2020-08-20T12:03:08.454+00:00",
 "Source": {
 "Channel": 0
 },
 "Data": {
 "State": false
 }
 },
 ……
 ]
 }

```

SUNAPI 117


### **17.6. Metadata format for body temperature detection**

Follows ONVIF metadata format and temperature unit is in Kelvin.

```
 <tt:MetadataStream xmlns:tt="http://www.onvif.org/ver10/schema"
 xmlns:fc="http://www.onvif.org/ver20/analytics/humanface"
 xmlns:bd="http://www.onvif.org/ver20/analytics/humanbody">
 <tt:VideoAnalytics>
 <tt:Frame UtcTime="2019-05-15T12:24:57.321">
 <tt:Transformation>
 <tt:Translate x="-1.0" y="1.0" />
 <tt:Scale x="0.000781" y="-0.001042" />
 </tt:Transformation>
 <tt:Object ObjectId="15" Parent="12">
 <tt:Appearance>
 <tt:Shape>
 <tt:BoundingBox left="15.0" top="141.0" right="51.0"
 bottom="291.0" />
 <tt:CenterOfGravity x="31.0" y="218.0" />
 </tt:Shape>
 <tt:Class>
 <tt:Type Likelihood="0.8">HumanFace
 </tt:Type>
 </tt:Class>
 <tt:HumanFace>
 <fc:Temperature>311.75</fc:Temperature>
 </tt:HumanFace>
 </tt:Appearance>
 </tt:Object>
 </tt:Frame>
 </tt:VideoAnalytics>
 </tt:MetadataStream>

```

118 Application Programmer’s Guide


## **Chapter 18. AI Camera Integration**

The purpose of this section is to help quick integration; however, for detailed explanation
**NOTE**

of parameters, it is recommended to refer to the corresponding cgi documents.

### **18.1. IVA Object Type Filter**


If the filter values are not delivered, the filter would work as before. If the filter is set, only



**NOTE**



when the specified object type crosses the line or enters the area, an event will be

triggered.


### **18.2. Line Rule**

#### **18.2.1. Set operation**

```
 http://<Device IP>/stw cgi/eventsources.cgi?msubmenu=videoanalysis2&action=set&Channel=0&Line.1.Coo
 rdinate=612,334,1815,1434&Line.1.Mode=Right&DetectionType=MDAndIV&Line.1.Obj
 ectTypeFilter=Vehicle,Person&Line.1.RuleName=boundaryrule1

#### **18.2.2. View**

 {
 "VideoAnalysis": [
 {
 "Channel": 0,
 "DetectionType": "MDAndIV",
 "SensitivityLevel": 100,
 "ObjectSizeByDetectionTypes": [
 {
 "DetectionType": "MotionDetection",
 "MinimumObjectSize": "0,0",
 "MaximumObjectSize": "99,99",
 "MinimumObjectSizeInPixels": "42,42",
 "MaximumObjectSizeInPixels": "2560,1920",
 "DetectionResultOverlay": false
 },
 {
 "DetectionType": "IntelligentVideo",
 "MinimumObjectSize": "5,7",
 "MaximumObjectSize": "66,89",

```

SUNAPI 119


```
 "MinimumObjectSizeInPixels": "173,173",
 "MaximumObjectSizeInPixels": "1728,1728",
 "DetectionResultOverlay": false
 }
 ],
 "ROIs": [
 {
 "ROI": 1,
 "Mode": "Inside",
 "SensitivityLevel": 1,
 "ThresholdLevel": 5,
 "Coordinates": [
 {
 "x": 0,
 "y": 0
 },
 {
 "x": 0,
 "y": 1919
 },
 {
 "x": 2559,
 "y": 1919
 },
 {
 "x": 2559,
 "y": 0
 }
 ],
 "HandoverIndex": 0,
 "Duration": 0
 }
 ],
 "Lines": [
 {
 "Line": 1,
 "Coordinates": [
 {
 "x": 612,
 "y": 334
 },

```

120 Application Programmer’s Guide


```
 {
 "x": 1815,
 "y": 1434
 }
 ],
 "Mode": "Right",
 "HandoverIndex": 0,
 "RuleName": "boundaryrule1",
 "ObjectTypeFilter": [
 " Vehicle ",
 " Person "
 ]
 }
 ],
 "DefinedAreas": [
 {
 "DefinedArea": 1,
 "Type": "Inside",
 "Mode": [],
 "Coordinates": [
 {
 "x": 1343,
 "y": 548
 },
 {
 "x": 1176,
 "y": 932
 },
 {
 "x": 1667,
 "y": 1468
 },
 {
 "x": 1843,
 "y": 448
 }
 ],
 "AppearanceDuration": 10,
 "LoiteringDuration": 10,
 "HandoverIndex": 0,
 "IntrusionDuration": 0

```

SUNAPI 121


```
 }
 ]
 }
 ]
 }

### **18.3. Area Rule**

#### **18.3.1. Set operation**

 http://<Device IP>/stw cgi/eventsources.cgi?msubmenu=videoanalysis2&action=set&Channel=0&DefinedAre
 a.1.Coordinate=488,638,1971,282,2335,998,1839,1618&DefinedArea.1.Type=Inside
 &DefinedArea.1.Mode=AppearDisappear,Entering,Exiting,Intrusion,Loitering&Def
 inedArea.1.AppearanceDuration=10&DefinedArea.1.LoiteringDuration=10&DefinedA
 rea.1.IntrusionDuration=0&DefinedArea.1.ObjectTypeFilter=Vehicle,Person&Dete
 ctionType=MDAndIV&DefinedArea.1.RuleName=boundbox1

#### **18.3.2. View**

 {
 "VideoAnalysis": [
 {
 "Channel": 0,
 "DetectionType": "MDAndIV",
 "SensitivityLevel": 100,
 "ObjectSizeByDetectionTypes": [
 {
 "DetectionType": "MotionDetection",
 "MinimumObjectSize": "0,0",
 "MaximumObjectSize": "99,99",
 "MinimumObjectSizeInPixels": "42,42",
 "MaximumObjectSizeInPixels": "2560,1920",
 "DetectionResultOverlay": false
 },
 {
 "DetectionType": "IntelligentVideo",
 "MinimumObjectSize": "5,7",
 "MaximumObjectSize": "66,89",
 "MinimumObjectSizeInPixels": "173,173",
 "MaximumObjectSizeInPixels": "1728,1728",

```

122 Application Programmer’s Guide


```
 "DetectionResultOverlay": false
 }
 ],
 "ROIs": [
 {
 "ROI": 1,
 "Mode": "Inside",
 "SensitivityLevel": 1,
 "ThresholdLevel": 5,
 "Coordinates": [
 {
 "x": 0,
 "y": 0
 },
 {
 "x": 0,
 "y": 1919
 },
 {
 "x": 2559,
 "y": 1919
 },
 {
 "x": 2559,
 "y": 0
 }
 ],
 "HandoverIndex": 0,
 "Duration": 0
 }
 ],
 "Lines": [
 {
 "Line": 1,
 "Coordinates": [
 {
 "x": 612,
 "y": 334
 },
 {
 "x": 1815,

```

SUNAPI 123


```
 "y": 1434
 }
 ],
 "Mode": "Right",
 "HandoverIndex": 0
 }
 ],
 "DefinedAreas": [
 {
 "DefinedArea": 1,
 "Type": "Inside",
 "Mode": [
 "AppearDisappear",
 "Entering",
 "Exiting",
 "Intrusion",
 "Loitering"
 ],
 "Coordinates": [
 {
 "x": 488,
 "y": 638
 },
 {
 "x": 1971,
 "y": 282
 },
 {
 "x": 2335,
 "y": 998
 },
 {
 "x": 1839,
 "y": 1618
 }
 ],
 "AppearanceDuration": 10,
 "LoiteringDuration": 10,
 "HandoverIndex": 0,
 "IntrusionDuration": 0,
 "RuleName": "boundbox1",

```

124 Application Programmer’s Guide


```
 "ObjectTypeFilter": [
 " Vehicle ",
 " Person "
 ]
 }
 ]
 }
 ]
 }

### **18.4. Object Detection Submenu**

```

**NOTE** Only when Object detection or IVA is enabled, object metadata would be generated.


In **ObjectDetection** submenu, if no object types are selected, no event would be triggered and only

metadata would be generated.

#### **18.4.1. Set operation**

```
 http://<Device IP>/stw cgi/eventsources.cgi?msubmenu=objectdetection&action=set&Channel=0&ObjectTyp
 es=Vehicle,Person,Face,LicensePlate&Sensitivity=50&Enable=True&ExcludeArea.1
 .Coordinate=672,1002,1044,254,2291,326,2275,1662

#### **18.4.2. View operation**

 http://<Device IP>/stw cgi/eventsources.cgi?msubmenu=objectdetection&action=view

 {
 "ObjectDetection": [
 {
 "Channel": 0,
 "Enable": true,
 "Duration": 1,
 "Sensitivity": 80,
 "MinimumObjectSize": "4,7",
 "MaximumObjectSize": "50,89",
 "MinimumObjectSizeInPixels": "194,194",
 "MaximumObjectSizeInPixels": "1944,1944",

```

SUNAPI 125


```
 "ObjectTypes": [
 "Person",
 "Vehicle",
 "Face",
 "LicensePlate"
 ],
 "ExcludeAreas": [
 {
 "ExcludeArea": 1,
 "Coordinates": [
 {
 "x": 1248,
 "y": 502
 },
 {
 "x": 3173,
 "y": 502
 },
 {
 "x": 3317,
 "y": 1743
 },
 {
 "x": 972,
 "y": 1701
 }
 ]
 }
 ]
 }
 ]
 }

### **18.5. Metaimagetransfer Submenu (BestShot Feature)**
```

Used to enable the image sending feature in metadata


**NOTE** Object detection should be enabled for this functionality to work

#### **18.5.1. View the current settings**


126 Application Programmer’s Guide


```
 http://IP/eventsources.cgi?msubmenu=metaimagetransfer&action=view

 {
 " MetaImageTransfer ": [
 {
 "Channel": 0,
 "ObjectTypes": [
 "Vehicle",
 "Person",
 "Face",
 "LicensePlate"
 ],
 }
 ]
 }

#### **18.5.2. Set operation**

 http://IP/eventsources.cgi?msubmenu=metaimagetransfer&action=set&Channel=0&O
 bjectTypes=Face,LicensePlate

### **18.6. Digital Auto Tracking**
```

For setting the digital autotracking filter setting based on object types


**NOTE** Only Channel 1 supports this feature (Which is a DPTZ channel)

#### **18.6.1. View**

```
 http://<Device IP>/stw cgi/ptzconfig.cgi?msubmenu=digitalautotracking&action=view

 {
 "digitalautotracking": [
 {
 "Channel": 1,
 "ObjectTypeFilter": [
 "Person",
 "Vehicle"

```

SUNAPI 127


```
 ]
 }
 ]
 }

#### **18.6.2. Set**

 http://<Device IP>/stw cgi/ptzconfig.cgi?msubmenu=digitalautotracking&action=set&Channel=1&ObjectTy
 peFilter=Person,Vehicle

### **18.7. EventStatus Check**

#### **18.7.1. Object detection events**

 http://<Device IP>/stw-cgi/eventstatus.cgi?msubmenu=eventstatus&action=check

 AlarmInput.1=False
 AlarmOutput.1=False
 Channel.0.MotionDetection=False
 Channel.0.MotionDetection.RegionID.1=False
 Channel.0.FaceDetection=False
 Channel.0.Tampering=False
 Channel.0.AudioDetection=False
 Channel.0.DefocusDetection=False
 Channel.0.FogDetection=False
 Channel.0.Profile.1.DigitalAutoTracking=False
 Channel.0.Profile.2.DigitalAutoTracking=False
 Channel.0.Profile.3.DigitalAutoTracking=False
 Channel.0.Profile.4.DigitalAutoTracking=False
 Channel.0.Profile.5.DigitalAutoTracking=False
 Channel.0.Profile.6.DigitalAutoTracking=False
 Channel.0.Profile.7.DigitalAutoTracking=False
 Channel.0.Profile.8.DigitalAutoTracking=False
 Channel.0.Profile.9.DigitalAutoTracking=False
 Channel.0.Profile.10.DigitalAutoTracking=False
 Channel.0.VideoAnalytics.Passing=False
 Channel.0.VideoAnalytics.Intrusion=False
 Channel.0.VideoAnalytics.Entering=False
 Channel.0.VideoAnalytics.Exiting=False

```

128 Application Programmer’s Guide


```
 Channel.0.VideoAnalytics.Appearing=True
 Channel.0.VideoAnalytics.Loitering=False
 Channel.0.AudioAnalytics.Scream=False
 Channel.0.AudioAnalytics.Gunshot=False
 Channel.0.AudioAnalytics.Explosion=False
 Channel.0.AudioAnalytics.GlassBreak=False
 Channel.0.ObjectDetection=False
 Channel.0.ObjectDetection.Person=False
 Channel.0.ObjectDetection.Vehicle=False
 Channel.0.ObjectDetection.Face=False
 Channel.0.ObjectDetection.LicensePlate=False
 Channel.0.Connected=True
 SystemEvent.TimeChange=False
 SystemEvent.PowerReboot=False
 SystemEvent.FWUpdate=False
 SystemEvent.FactoryReset=False
 SystemEvent.ConfigurationBackup=False
 SystemEvent.ConfigurationRestore=False
 SystemEvent.ConfigChange=False
 SystemEvent.SDFormat=False
 SystemEvent.SDFail=False
 SystemEvent.SDFull=False
 SystemEvent.SDInsert=False
 SystemEvent.SDRemove=True
 SystemEvent.NASConnect=False
 SystemEvent.NASDisconnect=True
 SystemEvent.NASFail=False
 SystemEvent.NASFull=False
 SystemEvent.NASFormat=False

### **18.8. SchemaBased Dynamic Event format**

#### **18.8.1. Check**

 http://<Device IP>/stw cgi/eventstatus.cgi?msubmenu=eventstatus&action=check& SchemaBased=True

#### **18.8.2. Monitor**

 http://<Device IP>/stw
```

SUNAPI 129


```
 cgi/eventstatus.cgi?msubmenu=eventstatus&action=monitor& SchemaBased=True

#### **18.8.3. Monitor diff**

 http://<Device IP>/stw cgi/eventstatus.cgi?msubmenu=eventstatus&action=monitordiff& SchemaBased=True

 {
 "EventName": "ObjectDetection",
 "Time": "2019-06-16T00:22:46.802+00:00",
 "Source": {
 "Channel": 0
 },
 "Data": {
 "State": true,
 "ObjectTypes": "Face, Vehicle"
 }
 }

### **18.9. ONVIF/MetaEvent Notification (Based on ONVIF** **Draft)**
```

Sample object detection event in metadata is shown below:

```
 <tt:Event>
 <wsnt:NotificationMessage>
 <wsnt:Topic
 Dialect="http://www.onvif.org/ver10/tev/topicExpression/ConcreteSet">tns1:Ru
 leEngine/ObjectDetection/Object</wsnt:Topic>
 <wsnt:Message>
 <tt:Message UtcTime="2019-11-14T05:50:51.290Z"
 PropertyOperation="Changed">
 <tt:Source>
 <tt:SimpleItem Name="VideoSource"
 Value="VideoSourceToken-0"/>
 <tt:SimpleItem Name="RuleName"
 Value="ObjectDetectionRule-1"/>
 </tt:Source>
 <tt:Data>

```

130 Application Programmer’s Guide


```
 <tt:SimpleItem Name="ClassTypes" Value="Person
 Vehicle"/>
 </tt:Data>
 </tt:Message>
 </wsnt:Message>
 </wsnt:NotificationMessage>
 </tt:Event>

```

Whenever there is a change in detection types, ClassTypes field will be updated; if nothing
**NOTE**

is detected, an empty ClassType will be sent.

### **18.10. BestShot RTP Stream**

To receive the bestshot image in RTP, please refer to [4] SUNAPI_video.audio_2.6.3 in the References

section for more information.

### **18.11. Metadata Format**

The supported attributes are shown in the table shown below:


Those marked in RED are not supported in the current release and have fixed values as
**NOTE**

marked in the table below.

|Col1|Objects|Attributes|Supported attributes<br>items|
|---|---|---|---|
|**Attributes**|Person|Gender|Female, Male|
|||Upper(Color)|Black, Gray, White, Red,<br>Orange, Yellow, Green,<br>Blue, Purple<br>(up to 2 colors at the<br>same time)|
|||Lower(Color)||
|||Upper(Clothing)|Long, Short**(always**<br>**Long)**|
|||Lower(Clothing)|Long, Short**(always**<br>**Long)**|
|||Hat|Wear Hat or Not**(always**<br>**False)**|
|||Bag|Bag (If Bag is detected)|



SUNAPI 131


|Col1|Objects|Attributes|Supported attributes<br>items|
|---|---|---|---|
||Vehicle|Type|Car<br>(Sedan/SUV/Van…etc),<br>Bus, Truck, Motorcycle,<br>Bicycle|
|||Color|Black, Gray, White, Red,<br>Orange, Yellow, Green,<br>Blue, Purple<br>(up to 2 colors at the<br>same time)|
||Face|Gender|Female, Male|
|||Age|Young (0~19), Adult<br>(20~44), Middle (45~64),<br>Senior (65~)|
|||Mask|Wearing a mask or not|
|||Glasses|Wearing glasses or not|
||Licenseplate|||

#### **18.11.1. Sample Meta Frame with all fields (Only for reference)**

```
 <tt:MetadataStream xmlns:tt="http://www.onvif.org/ver10/schema"
 xmlns:fc="http://www.onvif.org/ver20/analytics/humanface"
 xmlns:bd="http://www.onvif.org/ver20/analytics/humanbody">
 <tt:VideoAnalytics>
 <tt:Frame UtcTime="2019-05-15T12:24:57.321">
 <tt:Transformation>
 <tt:Translate x="-1.0" y="1.0" />
 <tt:Scale x="0.000781" y="-0.001042" />
 </tt:Transformation>
 <tt:Object ObjectId="15" Parent="12">
 <tt:Appearance>
 <tt:Shape>
 <tt:BoundingBox left="15.0" top="141.0" right="51.0"
 bottom="291.0" />
 <tt:CenterOfGravity x="31.0" y="218.0" />
 </tt:Shape>
 <tt:Color>
 <tt:ColorCluster>
 <tt:Color X="58" Y="105" Z="212" />
 <tt:Covariance XX="7.2" YY="6" ZZ="3" />

```

132 Application Programmer’s Guide


```
 <tt:Weight>90</tt:Weight>
 <tt:ColorString>WHITE</tt:ColorString>
 </tt:ColorCluster>
 <tt:ColorCluster>
 <tt:Color X="165" Y="44" Z="139" />
 <tt:Covariance XX="4" YY="4" ZZ="4" />
 <tt:Weight>5</tt:Weight>
 <tt:ColorString>BLUE</tt:ColorString>
 </tt:ColorCluster>
 </tt:Color>
 <tt:Class>
 <tt:Type Likelihood="0.8">LicensePlate</tt:Type>
 </tt:Class>
 <tt:VehicleInfo>
 <tt:Type Likelihood="0.8"> car </tt:Type>
 </tt:VehicleInfo>
 <tt:HumanFace>
 <fc:Gender> Male </fc:Gender>
 <fc:AgeType>Adult</fc:AgeType>
 <fc:Accessory>
 <fc:Opticals>
 <fc:Wear>true</fc:Wear>
 </fc:Opticals>
 <fc:Mask>
 <fc:Wear>true</fc:Wear>
 </fc:Mask>
 <fc:Hat>
 <fc:Wear>false</fc:Wear>
 </fc:Hat>
 </fc:Accessory>
 </tt:HumanFace>
 <tt:HumanBody>
 <bd:Gender> Male </bd:Gender>
 <bd:Clothing>
 <bd:Hat>
 <bd:Wear>false</bd:Wear>
 </bd:Hat>
 <bd:Tops>
 <bd:Color>
 <tt:ColorCluster>
 <tt:Color X="58" Y="105" Z="212" />

```

SUNAPI 133


```
 <tt:Covariance XX="7.2" YY="6"
 ZZ="3" />
 <tt:Weight>90</tt:Weight>

 <tt:ColorString>WHITE</tt:ColorString>
 </tt:ColorCluster>
 <tt:ColorCluster>
 <tt:Color X="165" Y="44" Z="139" />
 <tt:Covariance XX="4" YY="4" ZZ="4"
 />
 <tt:Weight>5</tt:Weight>

 <tt:ColorString>BLUE</tt:ColorString>
 </tt:ColorCluster>
 </bd:Color>
 <bd:Length>Long</bd:Length>
 </bd:Tops>
 <bd:Bottoms>
 <bd:Color>
 <tt:ColorCluster>
 <tt:Color X="58" Y="105" Z="212" />
 <tt:Covariance XX="7.2" YY="6"
 ZZ="3" />
 <tt:Weight>90</tt:Weight>

 <tt:ColorString>WHITE</tt:ColorString>
 </tt:ColorCluster>
 <tt:ColorCluster>
 <tt:Color X="165" Y="44" Z="139" />
 <tt:Covariance XX="4" YY="4" ZZ="4"
 />
 <tt:Weight>5</tt:Weight>

 <tt:ColorString>BLUE</tt:ColorString>
 </tt:ColorCluster>
 </bd:Color>
 <bd:Length>Long</bd:Length>
 </bd:Bottoms>
 </bd:Clothing>
 <bd:Belonging>
 <bd:Bag>

```

134 Application Programmer’s Guide


```
 <bd:Category>Bag</bd:Category>
 </bd:Bag>
 </bd:Belonging>
 </tt:HumanBody >

 <tt:ImageRef>http://192.168.75.150/download/objectid_1_1548728068_100.jpg</t
 t:ImageRef>
 <tt:ImageRefShape>
 <tt:BoundingBox left="15.0" top="141.0" right="51.0"
 bottom="291.0" />
 <tt:CenterOfGravity x="31.0" y="218.0" />
 </tt:ImageRefShape>
 </tt:Appearance>
 </tt:Object>
 </tt:Frame>
 </tt:VideoAnalytics>
 </tt:MetadataStream>

```

**ImageRef**


A URL can also have a relative address.


**../download/objected_1_23323333_100.jpg**


SUNAPI 135


## **Chapter 19. Self-signed Certificate Creation and** **Use**
### **19.1. Attributes**

Client can check the following attributes to check if their device supports creation of a self-signed

certificate:


Request

```
 http://<IP>/stw cgi/attributes.cgi/attributes/Security/Limit/MaxSelfSignedCertificates

```

Response

```
 <attribute name="MaxSelfSignedCertificates" type="int" value="1" accesslevel
 ="guest"/>

### **19.2. Getting the List of Certificates**
```

Request (HTTP-GET)

```
 http://<IP>/stw-cgi/security.cgi?msubmenu=ssl&action=view

```

TEXT Response

```
 Policy=HTTP
 PublicCertificateInstalled=False
 SelfSignedCertificateInstalled=True
 PublicCertificateName= Certificate3
 CertificateInUse=
 Certificate.1.CertificateName =Certificate1
 Certificate.1.Type=Unique
 Certificate.1.Issuer=Hanwha
 Certificate.1.Subject=/C=KR/ST=LL/L=LL/O=LL/OU=hw/CN=192.168.77.11/emailAddr
 ess=test@hanwha.com
 Certificate.1.SubjectAlternativeName=192.168.77.11
 Certificate.1.IssueDate=2017-05-01
 Certificate.1.ExpiryDate=2018-05-01
 Certificate.1.Removable=False
 Certificate.2.CertificateName =Certificate2
 Certificate.2.Type=SelfSigned

```

136 Application Programmer’s Guide


```
 Certificate.2.Issuer=CA
 Certificate.2.Subject=/C=KR/ST=LL/L=LL/O=LL/OU=hw/CN=192.168.77.11/emailAddr
 ess=test@hanwha.com
 Certificate.2.SubjectAlternativeName=192.168.77.11
 Certificate.2.IssueDate=2017-06-01
 Certificate.2.ExpiryDate=2018-06-01
 Certificate.2.Removable=True
 Certificate.3.CertificateName =Certificate3
 Certificate.3.Issuer=Hanwha
 Certificate.3.Subject=/C=KR/ST=LL/L=LL/O=LL/OU=hw/CN=192.168.77.11/emailAddr
 ess=test@hanwha.com
 Certificate.3.SubjectAlternativeName=192.168.77.11
 Certificate.3.IssueDate=2017-07-01
 Certificate.3.ExpiryDate=2018-07-01
 Certificate.3.Removable=True

```

JSON Response

```
 {
 "Policy": "HTTP",
 "PublicCertificateInstalled": false,
 "SelfSignedCertificateInstalled": true,
 "PublicCertificateName": "Certificate3",
 "CertificateInUse": "",
 "Certificate": [
 {
 "Index": 1,
 "CertificateName": "Certificate1",
 "Type": "Unique",
 "Issuer": "Hanwha",
 "Subject":
 "/C=KR/ST=LL/L=LL/O=LL/OU=hw/CN=192.168.77.11/emailAddress=test@hanwha.com",
 "SubjectAlternativeName": "192.168.77.11",
 "IssueDate": "2017-05-01",
 "ExpiryDate": "2018-05-01",
 "Removable": false
 },
 {
 "Index": 2,
 "CertificateName": "Certificate2",
 "Type": "SelfSigned",

```

SUNAPI 137


```
 "Issuer": "CA",
 "Subject":
 "/C=KR/ST=LL/L=LL/O=LL/OU=hw/CN=192.168.77.11/emailAddress=test@hanwha.com",
 "SubjectAlternativeName": "192.168.77.11",
 "IssueDate": "2017-06-01",
 "ExpiryDate": "2018-06-01",
 "Removable": true
 },
 {
 "Index": 3,
 "CertificateName": "Certificate3",
 "Type": "Public",
 "Issuer": "Hanwha",
 "Subject":
 "/C=KR/ST=LL/L=LL/O=LL/OU=hw/CN=192.168.77.11/emailAddress=test@hanwha.com",
 "SubjectAlternativeName": "192.168.77.11",
 "IssueDate": "2017-07-01",
 "ExpiryDate": "2018-07-01",
 "Removable": true
 }
 ]
 }

### **19.3. Creating a Self-signed Certificate**
```

To create a new self-signed certificate for the device, the following cgi can be used:


Request (HTTP-GET)

```
 http://<IP>/stw cgi/security.cgi?msubmenu=ssl&action=add&CertificateName=newCert&Type=SelfSi
 gned&CommonName=192.168.75.123&SubjectAlternativeName=domain.com,testdom.com
 &ExpiryDate=2020-09 09&Country=KR&Province=Gyeonggi&Location=Bundang&Organization=Hanwha&Divisio
 n=SS&EmailID=test@hanwha.com,test2@hanwha.com

```

TEXT Response

```
 OK

```

138 Application Programmer’s Guide


JSON Response

```
 {
 "Response": "Success"
 }

### **19.4. Selecting a Certificate**
```

To select a certificate to use on the camera’s web server, the following method can be used:


Request (HTTP-GET)

```
 http://<IP>/stw cgi/security.cgi?msubmenu=ssl&action=set&Policy=HTTPSProprietary&Certificate
 InUse=newCert

### **19.5. Removing a Certificate**
```

Any certificates with Removable status true can be removed.


Request (HTTP-GET)

```
 http://<IP>/stw cgi/security.cgi?msubmenu=ssl&action=remove&CertificateName=Certificate2

```

TEXT Response:

```
 OK

```

JSON Response:

```
 {
 "Response": "Success"
 }

```

SUNAPI 139


## **Chapter 20. Intercom Camera Integration**
### **20.1. Overview**

#### **20.1.1. Supports the SIP (Session Initation Protocol)**

The TID-600R provides audio and video communications using standard SIP. It can integrate with external

SIP compatible systems through a SIP server.


Refer to **sipsetup**, **sipaccount**, **siprecipients** submenus of **network.cgi** for more details to change the

SIP settings.

#### **20.1.2. NAT Traversal**

The TID-600R provides NAT Traversal for seamless communication between devices located on the private

network and the external internet. Refer to nattraversal submenu of network.cgi for change the NAT

Traversal settings.

### **20.2. Difference of other cameras**

#### **20.2.1. Profile for VoIP**

Video delivery of SIP requires creating a profile for VoIP. The camera uses a VoIP-only profile when SIP is

connected; if no profile exists, only audio is sent. VoIP profile is activated if the camera supports SIP.

Whether or not SIP is supported can be checked in attribute below.

```
 http://<Device IP>/stw-cgi/attributes.cgi/attributes/Network/Support/SIP

```

VoIP profile is limited in supported codecs, resolution, and bitrates, so you need to check and set the video

codec information. Refer to videocodecinfo submenu of media.cgi to get video codec information.

#### **20.2.2. Power relay output**

The TID-600R model provides a power relay output. Unlike typical Open Collector type IC output, external

device control is possible through power connections without requiring additional circuit configuration.

The output ports that provide power relay can be found by the attributes below.

```
 http://<Device IP>/stw cgi/attributes.cgi/attributes/IO/Support/PowerRelayIndices

### **20.3. Events**

#### **20.3.1. Call Request**
```

The TID-600R supports SIP calls for audio and video communication. And you can also integrate with video

surveillance systems for call features. When a button is pressed or a touchless sensor is detected, a


140 Application Programmer’s Guide


CallRequest event will be triggered and an SIP call will be requested. The event will persist until the

recipient accepts the call, reaches the CallingTimeout, or sends a stop request command. If you want to

check the CallRequest event on the video surveillance system and stop a SIP call, Refer to sipcall submenu

of network.cgi, and refer to callrequest submenu of eventsources.cgi for change the CallRequest event

settings.


Note that the CallRequest event is the fixed event for intercom model cameras and cannot be disabled.

#### **20.3.2. DTMF Received**

It can perform defined actions by receiving DTMF(Dual Tone Multi Frequency) signals through SIP. User
defined actions such as recording, door opening, and alarm triggering can be performed through a

specific DTMF signal. This model supports DTMF reception over RTP payload (RFC2833) and SIP INFO

Method (RFC2976). Refer to dtmf submenu of eventsources.cgi for change the DTMF event settings.

#### **20.3.3. Tampering Switch**

The tampering switch is an event that can detect security threats caused by physical damage or

disassembly of the product by an external intruder. Refer to tamperingswitch submenu of

eventsources.cgi for change the tampering switch event settings.

### **20.4. Video codec information for VoIP-only profile**

#### **20.4.1. Getting all resolution information based on Encoding Type**

REQUEST

```
 http://<Device IP>/stw cgi/media.cgi?msubmenu=videocodecinfo&action=view&EncodingType=H264

```

TEXT RESPONSE

```
 HTTP/1.0 200 OK
 Content-type: text/plain
 <Body>

 Channel.0.EncodingType=H264
 H264.General.1920X1080.Width=1920
 H264.General.1920X1080.Height=1080
 H264.General.1920X1080.MaxFPS=30000
 H264.General.1920X1080.DefaultFPS=30000
 H264.General.1920X1080.MaxCBRTargetBitrate=20480
 H264.General.1920X1080.MinCBRTargetBitrate=1024
 H264.General.1920X1080.DefaultCBRTargetBitrate=2560
 H264.General.1920X1080.MaxVBRTargetBitrate=30720

```

SUNAPI 141


```
 H264.General.1920X1080.MinVBRTargetBitrate=1536
 H264.General.1920X1080.DefaultVBRTargetBitrate=2560
 H264.General.1920X1080.IsTruncated=Normal
 H264.General.1920X1080.FrameLockMaxFPS=30000
 H264.General.1280X1024.Width=1280
 H264.General.1280X1024.Height=1024
 H264.General.1280X1024.MaxFPS=30000
 H264.General.1280X1024.DefaultFPS=30000
 H264.General.1280X1024.MaxCBRTargetBitrate=20480
 H264.General.1280X1024.MinCBRTargetBitrate=1024
 H264.General.1280X1024.DefaultCBRTargetBitrate=2048
 H264.General.1280X1024.MaxVBRTargetBitrate=30720
 H264.General.1280X1024.MinVBRTargetBitrate=1536
 H264.General.1280X1024.DefaultVBRTargetBitrate=2048
 H264.General.1280X1024.IsTruncated=Crop
 H264.General.1280X1024.FrameLockMaxFPS=30000
 H264.General.1280X960.Width=1280
 H264.General.1280X960.Height=960
 H264.General.1280X960.MaxFPS=30000
 H264.General.1280X960.DefaultFPS=30000
 H264.General.1280X960.MaxCBRTargetBitrate=20480
 H264.General.1280X960.MinCBRTargetBitrate=1024
 H264.General.1280X960.DefaultCBRTargetBitrate=2048
 H264.General.1280X960.MaxVBRTargetBitrate=30720
 H264.General.1280X960.MinVBRTargetBitrate=1536
 H264.General.1280X960.DefaultVBRTargetBitrate=2048
 H264.General.1280X960.IsTruncated=Crop
 H264.General.1280X960.FrameLockMaxFPS=30000
 H264.General.1280X720.Width=1280
 H264.General.1280X720.Height=720
 H264.General.1280X720.MaxFPS=30000
 H264.General.1280X720.DefaultFPS=30000
 H264.General.1280X720.MaxCBRTargetBitrate=20480
 H264.General.1280X720.MinCBRTargetBitrate=1024
 H264.General.1280X720.DefaultCBRTargetBitrate=2048
 H264.General.1280X720.MaxVBRTargetBitrate=30720
 H264.General.1280X720.MinVBRTargetBitrate=1536
 H264.General.1280X720.DefaultVBRTargetBitrate=2048
 H264.General.1280X720.IsTruncated=Normal
 H264.General.1280X720.FrameLockMaxFPS=30000
 H264.General.1024X768.Width=1024

```

142 Application Programmer’s Guide


```
 H264.General.1024X768.Height=768
 H264.General.1024X768.MaxFPS=30000
 H264.General.1024X768.DefaultFPS=30000
 H264.General.1024X768.MaxCBRTargetBitrate=20480
 H264.General.1024X768.MinCBRTargetBitrate=1024
 H264.General.1024X768.DefaultCBRTargetBitrate=2048
 H264.General.1024X768.MaxVBRTargetBitrate=30720
 H264.General.1024X768.MinVBRTargetBitrate=1536
 H264.General.1024X768.DefaultVBRTargetBitrate=2048
 H264.General.1024X768.IsTruncated=Crop
 H264.General.1024X768.FrameLockMaxFPS=30000
 H264.General.800X600.Width=800
 H264.General.800X600.Height=600
 H264.General.800X600.MaxFPS=30000
 H264.General.800X600.DefaultFPS=30000
 H264.General.800X600.MaxCBRTargetBitrate=20480
 H264.General.800X600.MinCBRTargetBitrate=512
 H264.General.800X600.DefaultCBRTargetBitrate=1024
 H264.General.800X600.MaxVBRTargetBitrate=30720
 H264.General.800X600.MinVBRTargetBitrate=512
 H264.General.800X600.DefaultVBRTargetBitrate=1024
 H264.General.800X600.IsTruncated=Crop
 H264.General.800X600.FrameLockMaxFPS=30000
 H264.General.800X448.Width=800
 H264.General.800X448.Height=448
 H264.General.800X448.MaxFPS=30000
 H264.General.800X448.DefaultFPS=30000
 H264.General.800X448.MaxCBRTargetBitrate=20480
 H264.General.800X448.MinCBRTargetBitrate=512
 H264.General.800X448.DefaultCBRTargetBitrate=1024
 H264.General.800X448.MaxVBRTargetBitrate=30720
 H264.General.800X448.MinVBRTargetBitrate=512
 H264.General.800X448.DefaultVBRTargetBitrate=1024
 H264.General.800X448.IsTruncated=Normal
 H264.General.800X448.FrameLockMaxFPS=30000
 H264.General.720X576.Width=720
 H264.General.720X576.Height=576
 H264.General.720X576.MaxFPS=30000
 H264.General.720X576.DefaultFPS=30000
 H264.General.720X576.MaxCBRTargetBitrate=20480
 H264.General.720X576.MinCBRTargetBitrate=512

```

SUNAPI 143


```
 H264.General.720X576.DefaultCBRTargetBitrate=1024
 H264.General.720X576.MaxVBRTargetBitrate=30720
 H264.General.720X576.MinVBRTargetBitrate=512
 H264.General.720X576.DefaultVBRTargetBitrate=1024
 H264.General.720X576.IsTruncated=Crop
 H264.General.720X576.FrameLockMaxFPS=30000
 H264.General.720X480.Width=720
 H264.General.720X480.Height=480
 H264.General.720X480.MaxFPS=30000
 H264.General.720X480.DefaultFPS=30000
 H264.General.720X480.MaxCBRTargetBitrate=20480
 H264.General.720X480.MinCBRTargetBitrate=512
 H264.General.720X480.DefaultCBRTargetBitrate=1024
 H264.General.720X480.MaxVBRTargetBitrate=30720
 H264.General.720X480.MinVBRTargetBitrate=512
 H264.General.720X480.DefaultVBRTargetBitrate=1024
 H264.General.720X480.IsTruncated=Crop
 H264.General.720X480.FrameLockMaxFPS=30000
 H264.General.640X480.Width=640
 H264.General.640X480.Height=480
 H264.General.640X480.MaxFPS=30000
 H264.General.640X480.DefaultFPS=30000
 H264.General.640X480.MaxCBRTargetBitrate=20480
 H264.General.640X480.MinCBRTargetBitrate=512
 H264.General.640X480.DefaultCBRTargetBitrate=1024
 H264.General.640X480.MaxVBRTargetBitrate=30720
 H264.General.640X480.MinVBRTargetBitrate=512
 H264.General.640X480.DefaultVBRTargetBitrate=1024
 H264.General.640X480.IsTruncated=Crop
 H264.General.640X480.FrameLockMaxFPS=30000
 H264.General.640X360.Width=640
 H264.General.640X360.Height=360
 H264.General.640X360.MaxFPS=30000
 H264.General.640X360.DefaultFPS=30000
 H264.General.640X360.MaxCBRTargetBitrate=20480
 H264.General.640X360.MinCBRTargetBitrate=512
 H264.General.640X360.DefaultCBRTargetBitrate=1024
 H264.General.640X360.MaxVBRTargetBitrate=30720
 H264.General.640X360.MinVBRTargetBitrate=512
 H264.General.640X360.DefaultVBRTargetBitrate=1024
 H264.General.640X360.IsTruncated=Normal

```

144 Application Programmer’s Guide


```
 H264.General.640X360.FrameLockMaxFPS=30000
 H264.General.320X240.Width=320
 H264.General.320X240.Height=240
 H264.General.320X240.MaxFPS=30000
 H264.General.320X240.DefaultFPS=30000
 H264.General.320X240.MaxCBRTargetBitrate=20480
 H264.General.320X240.MinCBRTargetBitrate=256
 H264.General.320X240.DefaultCBRTargetBitrate=512
 H264.General.320X240.MaxVBRTargetBitrate=30720
 H264.General.320X240.MinVBRTargetBitrate=256
 H264.General.320X240.DefaultVBRTargetBitrate=512
 H264.General.320X240.IsTruncated=Crop
 H264.General.320X240.FrameLockMaxFPS=30000
 H264.Record.1920X1080.MaxFPS=30000
 H264.Record.1920X1080.DefaultFPS=30000
 H264.Record.1920X1080.MinCBRTargetBitrate=1024
 H264.Record.1920X1080.MaxCBRTargetBitrate=6144
 H264.Record.1920X1080.DefaultCBRTargetBitrate=5120
 H264.Record.1920X1080.MinVBRTargetBitrate=1536
 H264.Record.1920X1080.MaxVBRTargetBitrate=6144
 H264.Record.1920X1080.DefaultVBRTargetBitrate=5120
 H264.Record.1920X1080.FrameLockMaxFPS=30000
 H264.Record.1280X1024.MaxFPS=30000
 H264.Record.1280X1024.DefaultFPS=30000
 H264.Record.1280X1024.MinCBRTargetBitrate=1024
 H264.Record.1280X1024.MaxCBRTargetBitrate=6144
 H264.Record.1280X1024.DefaultCBRTargetBitrate=5120
 H264.Record.1280X1024.MinVBRTargetBitrate=1536
 H264.Record.1280X1024.MaxVBRTargetBitrate=6144
 H264.Record.1280X1024.DefaultVBRTargetBitrate=5120
 H264.Record.1280X1024.FrameLockMaxFPS=30000
 H264.Record.1280X960.MaxFPS=30000
 H264.Record.1280X960.DefaultFPS=30000
 H264.Record.1280X960.MinCBRTargetBitrate=1024
 H264.Record.1280X960.MaxCBRTargetBitrate=6144
 H264.Record.1280X960.DefaultCBRTargetBitrate=5120
 H264.Record.1280X960.MinVBRTargetBitrate=1536
 H264.Record.1280X960.MaxVBRTargetBitrate=6144
 H264.Record.1280X960.DefaultVBRTargetBitrate=5120
 H264.Record.1280X960.FrameLockMaxFPS=30000
 H264.Record.1280X720.MaxFPS=30000

```

SUNAPI 145


```
 H264.Record.1280X720.DefaultFPS=30000
 H264.Record.1280X720.MinCBRTargetBitrate=1024
 H264.Record.1280X720.MaxCBRTargetBitrate=6144
 H264.Record.1280X720.DefaultCBRTargetBitrate=5120
 H264.Record.1280X720.MinVBRTargetBitrate=1536
 H264.Record.1280X720.MaxVBRTargetBitrate=6144
 H264.Record.1280X720.DefaultVBRTargetBitrate=5120
 H264.Record.1280X720.FrameLockMaxFPS=30000
 H264.Record.1024X768.MaxFPS=30000
 H264.Record.1024X768.DefaultFPS=30000
 H264.Record.1024X768.MinCBRTargetBitrate=1024
 H264.Record.1024X768.MaxCBRTargetBitrate=6144
 H264.Record.1024X768.DefaultCBRTargetBitrate=5120
 H264.Record.1024X768.MinVBRTargetBitrate=1536
 H264.Record.1024X768.MaxVBRTargetBitrate=6144
 H264.Record.1024X768.DefaultVBRTargetBitrate=5120
 H264.Record.1024X768.FrameLockMaxFPS=30000
 H264.Record.800X600.MaxFPS=30000
 H264.Record.800X600.DefaultFPS=30000
 H264.Record.800X600.MinCBRTargetBitrate=512
 H264.Record.800X600.MaxCBRTargetBitrate=6144
 H264.Record.800X600.DefaultCBRTargetBitrate=5120
 H264.Record.800X600.MinVBRTargetBitrate=512
 H264.Record.800X600.MaxVBRTargetBitrate=6144
 H264.Record.800X600.DefaultVBRTargetBitrate=5120
 H264.Record.800X600.FrameLockMaxFPS=30000
 H264.Record.800X448.MaxFPS=30000
 H264.Record.800X448.DefaultFPS=30000
 H264.Record.800X448.MinCBRTargetBitrate=512
 H264.Record.800X448.MaxCBRTargetBitrate=6144
 H264.Record.800X448.DefaultCBRTargetBitrate=5120
 H264.Record.800X448.MinVBRTargetBitrate=512
 H264.Record.800X448.MaxVBRTargetBitrate=6144
 H264.Record.800X448.DefaultVBRTargetBitrate=5120
 H264.Record.800X448.FrameLockMaxFPS=30000
 H264.Record.720X576.MaxFPS=30000
 H264.Record.720X576.DefaultFPS=30000
 H264.Record.720X576.MinCBRTargetBitrate=512
 H264.Record.720X576.MaxCBRTargetBitrate=6144
 H264.Record.720X576.DefaultCBRTargetBitrate=5120
 H264.Record.720X576.MinVBRTargetBitrate=512

```

146 Application Programmer’s Guide


```
 H264.Record.720X576.MaxVBRTargetBitrate=6144
 H264.Record.720X576.DefaultVBRTargetBitrate=5120
 H264.Record.720X576.FrameLockMaxFPS=30000
 H264.Record.720X480.MaxFPS=30000
 H264.Record.720X480.DefaultFPS=30000
 H264.Record.720X480.MinCBRTargetBitrate=512
 H264.Record.720X480.MaxCBRTargetBitrate=6144
 H264.Record.720X480.DefaultCBRTargetBitrate=5120
 H264.Record.720X480.MinVBRTargetBitrate=512
 H264.Record.720X480.MaxVBRTargetBitrate=6144
 H264.Record.720X480.DefaultVBRTargetBitrate=5120
 H264.Record.720X480.FrameLockMaxFPS=30000
 H264.Record.640X480.MaxFPS=30000
 H264.Record.640X480.DefaultFPS=30000
 H264.Record.640X480.MinCBRTargetBitrate=512
 H264.Record.640X480.MaxCBRTargetBitrate=6144
 H264.Record.640X480.DefaultCBRTargetBitrate=5120
 H264.Record.640X480.MinVBRTargetBitrate=512
 H264.Record.640X480.MaxVBRTargetBitrate=6144
 H264.Record.640X480.DefaultVBRTargetBitrate=5120
 H264.Record.640X480.FrameLockMaxFPS=30000
 H264.Record.640X360.MaxFPS=30000
 H264.Record.640X360.DefaultFPS=30000
 H264.Record.640X360.MinCBRTargetBitrate=512
 H264.Record.640X360.MaxCBRTargetBitrate=6144
 H264.Record.640X360.DefaultCBRTargetBitrate=5120
 H264.Record.640X360.MinVBRTargetBitrate=512
 H264.Record.640X360.MaxVBRTargetBitrate=6144
 H264.Record.640X360.DefaultVBRTargetBitrate=5120
 H264.Record.640X360.FrameLockMaxFPS=30000
 H264.Record.320X240.MaxFPS=30000
 H264.Record.320X240.DefaultFPS=30000
 H264.Record.320X240.MinCBRTargetBitrate=256
 H264.Record.320X240.MaxCBRTargetBitrate=6144
 H264.Record.320X240.DefaultCBRTargetBitrate=5120
 H264.Record.320X240.MinVBRTargetBitrate=256
 H264.Record.320X240.MaxVBRTargetBitrate=6144
 H264.Record.320X240.DefaultVBRTargetBitrate=5120
 H264.Record.320X240.FrameLockMaxFPS=30000
 H264.VoIP.1280X720.Width=1280
 H264.VoIP.1280X720.Height=720

```

SUNAPI 147


```
 H264.VoIP.1280X720.MaxFPS=30000
 H264.VoIP.1280X720.DefaultFPS=30000
 H264.VoIP.1280X720.MaxCBRTargetBitrate=2048
 H264.VoIP.1280X720.MinCBRTargetBitrate=1024
 H264.VoIP.1280X720.DefaultCBRTargetBitrate=1024
 H264.VoIP.1280X720.MinVBRTargetBitrate=1536
 H264.VoIP.1280X720.MaxVBRTargetBitrate=2048
 H264.VoIP.1280X720.DefaultVBRTargetBitrate=1536
 H264.VoIP.1024X768.Width=1024
 H264.VoIP.1024X768.Height=768
 H264.VoIP.1024X768.MaxFPS=30000
 H264.VoIP.1024X768.DefaultFPS=30000
 H264.VoIP.1024X768.MaxCBRTargetBitrate=2048
 H264.VoIP.1024X768.MinCBRTargetBitrate=1024
 H264.VoIP.1024X768.DefaultCBRTargetBitrate=1024
 H264.VoIP.1024X768.MinVBRTargetBitrate=1536
 H264.VoIP.1024X768.MaxVBRTargetBitrate=2048
 H264.VoIP.1024X768.DefaultVBRTargetBitrate=1536
 H264.VoIP.800X600.Width=800
 H264.VoIP.800X600.Height=600
 H264.VoIP.800X600.MaxFPS=30000
 H264.VoIP.800X600.DefaultFPS=30000
 H264.VoIP.800X600.MaxCBRTargetBitrate=1024
 H264.VoIP.800X600.MinCBRTargetBitrate=512
 H264.VoIP.800X600.DefaultCBRTargetBitrate=512
 H264.VoIP.800X600.MinVBRTargetBitrate=512
 H264.VoIP.800X600.MaxVBRTargetBitrate=1024
 H264.VoIP.800X600.DefaultVBRTargetBitrate=512
 H264.VoIP.800X448.Width=800
 H264.VoIP.800X448.Height=448
 H264.VoIP.800X448.MaxFPS=30000
 H264.VoIP.800X448.DefaultFPS=30000
 H264.VoIP.800X448.MaxCBRTargetBitrate=1024
 H264.VoIP.800X448.MinCBRTargetBitrate=512
 H264.VoIP.800X448.DefaultCBRTargetBitrate=512
 H264.VoIP.800X448.MinVBRTargetBitrate=512
 H264.VoIP.800X448.MaxVBRTargetBitrate=1024
 H264.VoIP.800X448.DefaultVBRTargetBitrate=512
 H264.VoIP.720X576.Width=720
 H264.VoIP.720X576.Height=576
 H264.VoIP.720X576.MaxFPS=30000

```

148 Application Programmer’s Guide


```
 H264.VoIP.720X576.DefaultFPS=30000
 H264.VoIP.720X576.MaxCBRTargetBitrate=1024
 H264.VoIP.720X576.MinCBRTargetBitrate=512
 H264.VoIP.720X576.DefaultCBRTargetBitrate=512
 H264.VoIP.720X576.MinVBRTargetBitrate=512
 H264.VoIP.720X576.MaxVBRTargetBitrate=1024
 H264.VoIP.720X576.DefaultVBRTargetBitrate=512
 H264.VoIP.720X480.Width=720
 H264.VoIP.720X480.Height=480
 H264.VoIP.720X480.MaxFPS=30000
 H264.VoIP.720X480.DefaultFPS=30000
 H264.VoIP.720X480.MaxCBRTargetBitrate=1024
 H264.VoIP.720X480.MinCBRTargetBitrate=512
 H264.VoIP.720X480.DefaultCBRTargetBitrate=512
 H264.VoIP.720X480.MinVBRTargetBitrate=512
 H264.VoIP.720X480.MaxVBRTargetBitrate=1024
 H264.VoIP.720X480.DefaultVBRTargetBitrate=512
 H264.VoIP.640X480.Width=640
 H264.VoIP.640X480.Height=480
 H264.VoIP.640X480.MaxFPS=30000
 H264.VoIP.640X480.DefaultFPS=30000
 H264.VoIP.640X480.MaxCBRTargetBitrate=1024
 H264.VoIP.640X480.MinCBRTargetBitrate=512
 H264.VoIP.640X480.DefaultCBRTargetBitrate=512
 H264.VoIP.640X480.MinVBRTargetBitrate=512
 H264.VoIP.640X480.MaxVBRTargetBitrate=1024
 H264.VoIP.640X480.DefaultVBRTargetBitrate=512
 H264.VoIP.640X360.Width=640
 H264.VoIP.640X360.Height=360
 H264.VoIP.640X360.MaxFPS=30000
 H264.VoIP.640X360.DefaultFPS=30000
 H264.VoIP.640X360.MaxCBRTargetBitrate=1024
 H264.VoIP.640X360.MinCBRTargetBitrate=512
 H264.VoIP.640X360.DefaultCBRTargetBitrate=512
 H264.VoIP.640X360.MinVBRTargetBitrate=512
 H264.VoIP.640X360.MaxVBRTargetBitrate=1024
 H264.VoIP.640X360.DefaultVBRTargetBitrate=512
 H264.VoIP.320X240.Width=320
 H264.VoIP.320X240.Height=240
 H264.VoIP.320X240.MaxFPS=30000
 H264.VoIP.320X240.DefaultFPS=30000

```

SUNAPI 149


```
 H264.VoIP.320X240.MaxCBRTargetBitrate=512
 H264.VoIP.320X240.MinCBRTargetBitrate=256
 H264.VoIP.320X240.DefaultCBRTargetBitrate=256
 H264.VoIP.320X240.MinVBRTargetBitrate=256
 H264.VoIP.320X240.MaxVBRTargetBitrate=512
 H264.VoIP.320X240.DefaultVBRTargetBitrate=256

```

JSON RESPONSE

```
 HTTP/1.0 200 OK
 Content-type: application/json
 <Body>

 {
 "VideoCodecInfo": [
 {
 "Channel": 0,
 "ViewModes": [
 {
 "ViewMode": "Overview",
 "Codecs": [
 {
 "EncodingType": "H264",
 "General": [
 {
 "Width": 1920,
 "Height": 1080,
 "MaxFPS": 30000,
 "DefaultFPS": 30000,
 "MaxCBRTargetBitrate": 20480,
 "MinCBRTargetBitrate": 1024,
 "DefaultCBRTargetBitrate": 2560,
 "MaxVBRTargetBitrate": 30720,
 "MinVBRTargetBitrate": 1536,
 "DefaultVBRTargetBitrate": 2560,
 "IsTruncated": "Normal",
 "FrameLockMaxFPS": 30000
 },
 {
 "Width": 1280,
 "Height": 1024,

```

150 Application Programmer’s Guide


```
 "MaxFPS": 30000,
 "DefaultFPS": 30000,
 "MaxCBRTargetBitrate": 20480,
 "MinCBRTargetBitrate": 1024,
 "DefaultCBRTargetBitrate": 2048,
 "MaxVBRTargetBitrate": 30720,
 "MinVBRTargetBitrate": 1536,
 "DefaultVBRTargetBitrate": 2048,
 "IsTruncated": "Crop",
 "FrameLockMaxFPS": 30000
 },
 {
 "Width": 1280,
 "Height": 960,
 "MaxFPS": 30000,
 "DefaultFPS": 30000,
 "MaxCBRTargetBitrate": 20480,
 "MinCBRTargetBitrate": 1024,
 "DefaultCBRTargetBitrate": 2048,
 "MaxVBRTargetBitrate": 30720,
 "MinVBRTargetBitrate": 1536,
 "DefaultVBRTargetBitrate": 2048,
 "IsTruncated": "Crop",
 "FrameLockMaxFPS": 30000
 },
 {
 "Width": 1280,
 "Height": 720,
 "MaxFPS": 30000,
 "DefaultFPS": 30000,
 "MaxCBRTargetBitrate": 20480,
 "MinCBRTargetBitrate": 1024,
 "DefaultCBRTargetBitrate": 2048,
 "MaxVBRTargetBitrate": 30720,
 "MinVBRTargetBitrate": 1536,
 "DefaultVBRTargetBitrate": 2048,
 "IsTruncated": "Normal",
 "FrameLockMaxFPS": 30000
 },
 {
 "Width": 1024,

```

SUNAPI 151


```
 "Height": 768,
 "MaxFPS": 30000,
 "DefaultFPS": 30000,
 "MaxCBRTargetBitrate": 20480,
 "MinCBRTargetBitrate": 1024,
 "DefaultCBRTargetBitrate": 2048,
 "MaxVBRTargetBitrate": 30720,
 "MinVBRTargetBitrate": 1536,
 "DefaultVBRTargetBitrate": 2048,
 "IsTruncated": "Crop",
 "FrameLockMaxFPS": 30000
 },
 {
 "Width": 800,
 "Height": 600,
 "MaxFPS": 30000,
 "DefaultFPS": 30000,
 "MaxCBRTargetBitrate": 20480,
 "MinCBRTargetBitrate": 512,
 "DefaultCBRTargetBitrate": 1024,
 "MaxVBRTargetBitrate": 30720,
 "MinVBRTargetBitrate": 512,
 "DefaultVBRTargetBitrate": 1024,
 "IsTruncated": "Crop",
 "FrameLockMaxFPS": 30000
 },
 {
 "Width": 800,
 "Height": 448,
 "MaxFPS": 30000,
 "DefaultFPS": 30000,
 "MaxCBRTargetBitrate": 20480,
 "MinCBRTargetBitrate": 512,
 "DefaultCBRTargetBitrate": 1024,
 "MaxVBRTargetBitrate": 30720,
 "MinVBRTargetBitrate": 512,
 "DefaultVBRTargetBitrate": 1024,
 "IsTruncated": "Normal",
 "FrameLockMaxFPS": 30000
 },
 {

```

152 Application Programmer’s Guide


```
 "Width": 720,
 "Height": 576,
 "MaxFPS": 30000,
 "DefaultFPS": 30000,
 "MaxCBRTargetBitrate": 20480,
 "MinCBRTargetBitrate": 512,
 "DefaultCBRTargetBitrate": 1024,
 "MaxVBRTargetBitrate": 30720,
 "MinVBRTargetBitrate": 512,
 "DefaultVBRTargetBitrate": 1024,
 "IsTruncated": "Crop",
 "FrameLockMaxFPS": 30000
 },
 {
 "Width": 720,
 "Height": 480,
 "MaxFPS": 30000,
 "DefaultFPS": 30000,
 "MaxCBRTargetBitrate": 20480,
 "MinCBRTargetBitrate": 512,
 "DefaultCBRTargetBitrate": 1024,
 "MaxVBRTargetBitrate": 30720,
 "MinVBRTargetBitrate": 512,
 "DefaultVBRTargetBitrate": 1024,
 "IsTruncated": "Crop",
 "FrameLockMaxFPS": 30000
 },
 {
 "Width": 640,
 "Height": 480,
 "MaxFPS": 30000,
 "DefaultFPS": 30000,
 "MaxCBRTargetBitrate": 20480,
 "MinCBRTargetBitrate": 512,
 "DefaultCBRTargetBitrate": 1024,
 "MaxVBRTargetBitrate": 30720,
 "MinVBRTargetBitrate": 512,
 "DefaultVBRTargetBitrate": 1024,
 "IsTruncated": "Crop",
 "FrameLockMaxFPS": 30000
 },

```

SUNAPI 153


```
 {
 "Width": 640,
 "Height": 360,
 "MaxFPS": 30000,
 "DefaultFPS": 30000,
 "MaxCBRTargetBitrate": 20480,
 "MinCBRTargetBitrate": 512,
 "DefaultCBRTargetBitrate": 1024,
 "MaxVBRTargetBitrate": 30720,
 "MinVBRTargetBitrate": 512,
 "DefaultVBRTargetBitrate": 1024,
 "IsTruncated": "Normal",
 "FrameLockMaxFPS": 30000
 },
 {
 "Width": 320,
 "Height": 240,
 "MaxFPS": 30000,
 "DefaultFPS": 30000,
 "MaxCBRTargetBitrate": 20480,
 "MinCBRTargetBitrate": 256,
 "DefaultCBRTargetBitrate": 512,
 "MaxVBRTargetBitrate": 30720,
 "MinVBRTargetBitrate": 256,
 "DefaultVBRTargetBitrate": 512,
 "IsTruncated": "Crop",
 "FrameLockMaxFPS": 30000
 }
 ],
 "Record": [
 {
 "Width": 1920,
 "Height": 1080,
 "MaxFPS": 30000,
 "DefaultFPS": 30000,
 "MinCBRTargetBitrate": 1024,
 "MaxCBRTargetBitrate": 6144,
 "DefaultCBRTargetBitrate": 5120,
 "MinVBRTargetBitrate": 1536,
 "MaxVBRTargetBitrate": 6144,
 "DefaultVBRTargetBitrate": 5120,

```

154 Application Programmer’s Guide


```
 "FrameLockMaxFPS": 30000
 },
 {
 "Width": 1280,
 "Height": 1024,
 "MaxFPS": 30000,
 "DefaultFPS": 30000,
 "MinCBRTargetBitrate": 1024,
 "MaxCBRTargetBitrate": 6144,
 "DefaultCBRTargetBitrate": 5120,
 "MinVBRTargetBitrate": 1536,
 "MaxVBRTargetBitrate": 6144,
 "DefaultVBRTargetBitrate": 5120,
 "FrameLockMaxFPS": 30000
 },
 {
 "Width": 1280,
 "Height": 960,
 "MaxFPS": 30000,
 "DefaultFPS": 30000,
 "MinCBRTargetBitrate": 1024,
 "MaxCBRTargetBitrate": 6144,
 "DefaultCBRTargetBitrate": 5120,
 "MinVBRTargetBitrate": 1536,
 "MaxVBRTargetBitrate": 6144,
 "DefaultVBRTargetBitrate": 5120,
 "FrameLockMaxFPS": 30000
 },
 {
 "Width": 1280,
 "Height": 720,
 "MaxFPS": 30000,
 "DefaultFPS": 30000,
 "MinCBRTargetBitrate": 1024,
 "MaxCBRTargetBitrate": 6144,
 "DefaultCBRTargetBitrate": 5120,
 "MinVBRTargetBitrate": 1536,
 "MaxVBRTargetBitrate": 6144,
 "DefaultVBRTargetBitrate": 5120,
 "FrameLockMaxFPS": 30000
 },

```

SUNAPI 155


```
 {
 "Width": 1024,
 "Height": 768,
 "MaxFPS": 30000,
 "DefaultFPS": 30000,
 "MinCBRTargetBitrate": 1024,
 "MaxCBRTargetBitrate": 6144,
 "DefaultCBRTargetBitrate": 5120,
 "MinVBRTargetBitrate": 1536,
 "MaxVBRTargetBitrate": 6144,
 "DefaultVBRTargetBitrate": 5120,
 "FrameLockMaxFPS": 30000
 },
 {
 "Width": 800,
 "Height": 600,
 "MaxFPS": 30000,
 "DefaultFPS": 30000,
 "MinCBRTargetBitrate": 512,
 "MaxCBRTargetBitrate": 6144,
 "DefaultCBRTargetBitrate": 5120,
 "MinVBRTargetBitrate": 512,
 "MaxVBRTargetBitrate": 6144,
 "DefaultVBRTargetBitrate": 5120,
 "FrameLockMaxFPS": 30000
 },
 {
 "Width": 800,
 "Height": 448,
 "MaxFPS": 30000,
 "DefaultFPS": 30000,
 "MinCBRTargetBitrate": 512,
 "MaxCBRTargetBitrate": 6144,
 "DefaultCBRTargetBitrate": 5120,
 "MinVBRTargetBitrate": 512,
 "MaxVBRTargetBitrate": 6144,
 "DefaultVBRTargetBitrate": 5120,
 "FrameLockMaxFPS": 30000
 },
 {
 "Width": 720,

```

156 Application Programmer’s Guide


```
 "Height": 576,
 "MaxFPS": 30000,
 "DefaultFPS": 30000,
 "MinCBRTargetBitrate": 512,
 "MaxCBRTargetBitrate": 6144,
 "DefaultCBRTargetBitrate": 5120,
 "MinVBRTargetBitrate": 512,
 "MaxVBRTargetBitrate": 6144,
 "DefaultVBRTargetBitrate": 5120,
 "FrameLockMaxFPS": 30000
 },
 {
 "Width": 720,
 "Height": 480,
 "MaxFPS": 30000,
 "DefaultFPS": 30000,
 "MinCBRTargetBitrate": 512,
 "MaxCBRTargetBitrate": 6144,
 "DefaultCBRTargetBitrate": 5120,
 "MinVBRTargetBitrate": 512,
 "MaxVBRTargetBitrate": 6144,
 "DefaultVBRTargetBitrate": 5120,
 "FrameLockMaxFPS": 30000
 },
 {
 "Width": 640,
 "Height": 480,
 "MaxFPS": 30000,
 "DefaultFPS": 30000,
 "MinCBRTargetBitrate": 512,
 "MaxCBRTargetBitrate": 6144,
 "DefaultCBRTargetBitrate": 5120,
 "MinVBRTargetBitrate": 512,
 "MaxVBRTargetBitrate": 6144,
 "DefaultVBRTargetBitrate": 5120,
 "FrameLockMaxFPS": 30000
 },
 {
 "Width": 640,
 "Height": 360,
 "MaxFPS": 30000,

```

SUNAPI 157


```
 "DefaultFPS": 30000,
 "MinCBRTargetBitrate": 512,
 "MaxCBRTargetBitrate": 6144,
 "DefaultCBRTargetBitrate": 5120,
 "MinVBRTargetBitrate": 512,
 "MaxVBRTargetBitrate": 6144,
 "DefaultVBRTargetBitrate": 5120,
 "FrameLockMaxFPS": 30000
 },
 {
 "Width": 320,
 "Height": 240,
 "MaxFPS": 30000,
 "DefaultFPS": 30000,
 "MinCBRTargetBitrate": 256,
 "MaxCBRTargetBitrate": 6144,
 "DefaultCBRTargetBitrate": 5120,
 "MinVBRTargetBitrate": 256,
 "MaxVBRTargetBitrate": 6144,
 "DefaultVBRTargetBitrate": 5120,
 "FrameLockMaxFPS": 30000
 }
 ],
 "VoIP": [
 {
 "Width": 1280,
 "Height": 720,
 "MaxFPS": 30000,
 "DefaultFPS": 30000,
 "MaxCBRTargetBitrate": 2048,
 "MinCBRTargetBitrate": 1024,
 "DefaultCBRTargetBitrate": 1024,
 "MinVBRTargetBitrate": 1536,
 "MaxVBRTargetBitrate": 2048,
 "DefaultVBRTargetBitrate": 1536
 },
 {
 "Width": 1024,
 "Height": 768,
 "MaxFPS": 30000,
 "DefaultFPS": 30000,

```

158 Application Programmer’s Guide


```
 "MaxCBRTargetBitrate": 2048,
 "MinCBRTargetBitrate": 1024,
 "DefaultCBRTargetBitrate": 1024,
 "MinVBRTargetBitrate": 1536,
 "MaxVBRTargetBitrate": 2048,
 "DefaultVBRTargetBitrate": 1536
 },
 {
 "Width": 800,
 "Height": 600,
 "MaxFPS": 30000,
 "DefaultFPS": 30000,
 "MaxCBRTargetBitrate": 1024,
 "MinCBRTargetBitrate": 512,
 "DefaultCBRTargetBitrate": 512,
 "MinVBRTargetBitrate": 512,
 "MaxVBRTargetBitrate": 1024,
 "DefaultVBRTargetBitrate": 512
 },
 {
 "Width": 800,
 "Height": 448,
 "MaxFPS": 30000,
 "DefaultFPS": 30000,
 "MaxCBRTargetBitrate": 1024,
 "MinCBRTargetBitrate": 512,
 "DefaultCBRTargetBitrate": 512,
 "MinVBRTargetBitrate": 512,
 "MaxVBRTargetBitrate": 1024,
 "DefaultVBRTargetBitrate": 512
 },
 {
 "Width": 720,
 "Height": 576,
 "MaxFPS": 30000,
 "DefaultFPS": 30000,
 "MaxCBRTargetBitrate": 1024,
 "MinCBRTargetBitrate": 512,
 "DefaultCBRTargetBitrate": 512,
 "MinVBRTargetBitrate": 512,
 "MaxVBRTargetBitrate": 1024,

```

SUNAPI 159


```
 "DefaultVBRTargetBitrate": 512
 },
 {
 "Width": 720,
 "Height": 480,
 "MaxFPS": 30000,
 "DefaultFPS": 30000,
 "MaxCBRTargetBitrate": 1024,
 "MinCBRTargetBitrate": 512,
 "DefaultCBRTargetBitrate": 512,
 "MinVBRTargetBitrate": 512,
 "MaxVBRTargetBitrate": 1024,
 "DefaultVBRTargetBitrate": 512
 },
 {
 "Width": 640,
 "Height": 480,
 "MaxFPS": 30000,
 "DefaultFPS": 30000,
 "MaxCBRTargetBitrate": 1024,
 "MinCBRTargetBitrate": 512,
 "DefaultCBRTargetBitrate": 512,
 "MinVBRTargetBitrate": 512,
 "MaxVBRTargetBitrate": 1024,
 "DefaultVBRTargetBitrate": 512
 },
 {
 "Width": 640,
 "Height": 360,
 "MaxFPS": 30000,
 "DefaultFPS": 30000,
 "MaxCBRTargetBitrate": 1024,
 "MinCBRTargetBitrate": 512,
 "DefaultCBRTargetBitrate": 512,
 "MinVBRTargetBitrate": 512,
 "MaxVBRTargetBitrate": 1024,
 "DefaultVBRTargetBitrate": 512
 },
 {
 "Width": 320,
 "Height": 240,

```

160 Application Programmer’s Guide


```
 "MaxFPS": 30000,
 "DefaultFPS": 30000,
 "MaxCBRTargetBitrate": 512,
 "MinCBRTargetBitrate": 256,
 "DefaultCBRTargetBitrate": 256,
 "MinVBRTargetBitrate": 256,
 "MaxVBRTargetBitrate": 512,
 "DefaultVBRTargetBitrate": 256
 }
 ]
 }
 ]
 }
 ]
 }
 ]
 }

### **20.5. Usage Scenarios**

#### **20.5.1. VMS Usage (When SIP not supported)**
```

When using with VMS that does not support SIP. Based on the callrequest submenu settings, callrequest

event would be notified in eventstatus and metadata when call button is pressed. On receiving this

callrequest event, VMS can establish RTSP Connection to Doorcam with Video, Audio and

AudioBackChannel. On successful verification of the person at door, either power relay connected to door

or emergency alarm can be activated.


Additionally VMS can also check for any ongoing SIP call using the sipcall submenu and if VMS accepts the

CallRequest, a command must be requested to terminate SIP call.

#### **20.5.2. SIP Call Usage**

On camera Sipsetup, Nat traversal settings, Sipaccount settings and sip recipients needs to be configured

properly before usage. If operator has to do some action after receiving the call, DTMF event settings

needs to be configured appropriately (Example: on receving a DTMF code camera can operate the

powerrelay) When call button is pressed, a SIP call would be initiated with the registered recipients. After

accepting the call on the recipient end, operator can send specific DTMF code either to raise alarm or

operate the relay / open the door.

### **20.6. SUNAPI event status example**

#### **20.6.1. Getting event status**


SUNAPI 161


REQUEST

```
 http://<Device IP>/stw-cgi/eventstatus.cgi?msubmenu=eventstatus&action=check

```

TEXT RESPONSE

```
 HTTP/1.0 200 OK
 Content-type: text/plain
 <Body>

 AlarmInput.1=False
 AlarmInput.2=False
 AlarmOutput.1=False
 AlarmOutput.2=False
 Channel.0.MotionDetection=False
 Channel.0.MotionDetection.RegionID.1=False
 Channel.0.Tampering=False
 Channel.0.AudioDetection=False
 Channel.0.VideoAnalytics.Passing=False
 Channel.0.VideoAnalytics.Intrusion=False
 Channel.0.VideoAnalytics.Entering=False
 Channel.0.VideoAnalytics.Exiting=False
 Channel.0.VideoAnalytics.Appearing=False
 Channel.0.VideoAnalytics.Loitering=False
 Channel.0.AudioAnalytics.Scream=False
 Channel.0.AudioAnalytics.Gunshot=False
 Channel.0.AudioAnalytics.Explosion=False
 Channel.0.AudioAnalytics.GlassBreak=False
 Channel.0.ShockDetection=False
 Channel.0.CallRequest=False
 Channel.0.TamperingSwitch=False
 Channel.0.DTMFReceived=False
 SystemEvent.TimeChange=False
 SystemEvent.PowerReboot=False
 SystemEvent.FWUpdate=False
 SystemEvent.FactoryReset=False
 SystemEvent.ConfigurationBackup=False
 SystemEvent.ConfigurationRestore=False
 SystemEvent.ConfigChange=False
 SystemEvent.SDFormat=False
 SystemEvent.SDFail=False

```

162 Application Programmer’s Guide


```
 SystemEvent.SDFull=False
 SystemEvent.SDInsert=True
 SystemEvent.SDRemove=False
 SystemEvent.NASConnect=False
 SystemEvent.NASDisconnect=True
 SystemEvent.NASFail=False
 SystemEvent.NASFull=False
 SystemEvent.NASFormat=False

```

JSON RESPONSE

```
 HTTP/1.0 200 OK
 Content-type: application/json
 <Body>

 {
 "AlarmInput": {
 "1": false,
 "2": false
 },
 "AlarmOutput": {
 "1": false,
 "2": false
 },
 "ChannelEvent": [
 {
 "Channel": 0,
 "MotionDetection": false,
 "MotionDetectionRegions": {
 "1": false
 },
 "Tampering": false,
 "AudioDetection": false,
 "VideoAnalytics": {
 "Passing": false,
 "Intrusion": false,
 "Entering": false,
 "Exiting": false,
 "Appearing": false,
 "Loitering": false
 },

```

SUNAPI 163


```
 "AudioAnalytics": {
 "Scream": false,
 "Gunshot": false,
 "Explosion": false,
 "GlassBreak": false
 },
 "ShockDetection": false,
 "CallRequest": false,
 "TamperingSwitch": false,
 "DTMFReceived": false
 }
 ],
 "SystemEvent": {
 "TimeChange": false,
 "PowerReboot": false,
 "FWUpdate": false,
 "FactoryReset": false,
 "ConfigurationBackup": false,
 "ConfigurationRestore": false,
 "ConfigChange": false,
 "SDFormat": false,
 "SDFail": false,
 "SDFull": false,
 "SDInsert": true,
 "SDRemove": false,
 "NASConnect": false,
 "NASDisconnect": true,
 "NASFail": false,
 "NASFull": false,
 "NASFormat": false
 }
 }

#### **20.6.2. Getting scheme-based event status**
```

REQUEST

```
 http://<Device IP>/stw cgi/eventstatus.cgi?msubmenu=eventstatus&action=check&SchemaBased=True

```

164 Application Programmer’s Guide


TEXT RESPONSE

```
 HTTP/1.0 200 OK
 Content-type: text/plain
 <Body>

 AlarmInput.1=False
 AlarmInput.2=False
 AlarmOutput.1=False
 AlarmOutput.2=False
 Channel.0.MotionDetection=True
 Channel.0.MotionDetection.RegionID.1=False
 Channel.0.MotionDetection.RegionID.2=False
 Channel.0.Tampering=False
 Channel.0.AudioDetection=False
 Channel.0.VideoAnalytics.Passing=False
 Channel.0.VideoAnalytics.Intrusion=False
 Channel.0.VideoAnalytics.Entering=False
 Channel.0.VideoAnalytics.Exiting=False
 Channel.0.VideoAnalytics.Appearing=False
 Channel.0.VideoAnalytics.Loitering=False
 Channel.0.AudioAnalytics.Scream=False
 Channel.0.AudioAnalytics.Gunshot=False
 Channel.0.AudioAnalytics.Explosion=False
 Channel.0.AudioAnalytics.GlassBreak=False
 Channel.0.ShockDetection=False
 Channel.0.CallRequest=False
 Channel.0.TamperingSwitch=False
 Channel.0.DTMFReceived=False
 Channel.0.DTMFReceived.Index.1=False
 SystemEvent.TimeChange=False
 SystemEvent.PowerReboot=False
 SystemEvent.FWUpdate=False
 SystemEvent.FactoryReset=False
 SystemEvent.ConfigurationBackup=False
 SystemEvent.ConfigurationRestore=False
 SystemEvent.ConfigChange=False
 SystemEvent.SDFormat=False
 SystemEvent.SDFail=False
 SystemEvent.SDFull=False
 SystemEvent.SDInsert=True

```

SUNAPI 165


```
 SystemEvent.SDRemove=False
 SystemEvent.NASConnect=False
 SystemEvent.NASDisconnect=True
 SystemEvent.NASFail=False
 SystemEvent.NASFull=False
 SystemEvent.NASFormat=False

```

JSON RESPONSE

```
 HTTP/1.0 200 OK
 Content-type: application/json
 <Body>

 {
 "EventStatus": [
 {
 "EventName": "AlarmInput",
 "Time": "2021-05-03T09:59:00.862+00:00",
 "Source": {
 "Channel": 0
 },
 "Data": {
 "State": false
 }
 },
 {
 "EventName": "AlarmInput",
 "Time": "2021-05-03T09:59:00.863+00:00",
 "Source": {
 "Channel": 0
 },
 "Data": {
 "State": false
 }
 },
 {
 "EventName": "AlarmOutput",
 "Time": "2021-05-03T09:59:00.863+00:00",
 "Source": {
 "Channel": 0
 },

```

166 Application Programmer’s Guide


```
 "Data": {
 "State": false
 }
 },
 {
 "EventName": "AlarmOutput",
 "Time": "2021-05-03T09:59:00.863+00:00",
 "Source": {
 "Channel": 0
 },
 "Data": {
 "State": false
 }
 },
 {
 "EventName": "MotionDetection",
 "Time": "2021-05-03T09:59:00.863+00:00",
 "Source": {
 "Channel": 0,
 "ROIID": 1
 },
 "Data": {
 "State": false
 }
 },
 {
 "EventName": "MotionDetection",
 "Time": "2021-05-03T09:59:00.863+00:00",
 "Source": {
 "Channel": 0,
 "ROIID": 2
 },
 "Data": {
 "State": false
 }
 },
 {
 "EventName": "Tampering",
 "Time": "2021-05-03T09:59:00.863+00:00",
 "Source": {
 "Channel": 0

```

SUNAPI 167


```
 },
 "Data": {
 "State": false
 }
 },
 {
 "EventName": "AudioDetection",
 "Time": "2021-05-03T09:59:00.863+00:00",
 "Source": {
 "Channel": 0
 },
 "Data": {
 "State": false
 }
 },
 {
 "EventName": "AudioAnalytics.Scream",
 "Time": "2021-05-03T09:59:00.863+00:00",
 "Source": {
 "Channel": 0
 },
 "Data": {
 "State": false
 }
 },
 {
 "EventName": "AudioAnalytics.Gunshot",
 "Time": "2021-05-03T09:59:00.863+00:00",
 "Source": {
 "Channel": 0
 },
 "Data": {
 "State": false
 }
 },
 {
 "EventName": "AudioAnalytics.Explosion",
 "Time": "2021-05-03T09:59:00.863+00:00",
 "Source": {
 "Channel": 0
 },

```

168 Application Programmer’s Guide


```
 "Data": {
 "State": false
 }
 },
 {
 "EventName": "AudioAnalytics.GlassBreak",
 "Time": "2021-05-03T09:59:00.863+00:00",
 "Source": {
 "Channel": 0
 },
 "Data": {
 "State": false
 }
 },
 {
 "EventName": "ShockDetection",
 "Time": "2021-05-03T09:59:00.863+00:00",
 "Source": {
 "Channel": 0
 },
 "Data": {
 "State": false
 }
 },
 {
 "EventName": "CallRequest",
 "Time": "2021-05-03T09:59:00.863+00:00",
 "Source": {
 "Channel": 0
 },
 "Data": {
 "State": false
 }
 },
 {
 "EventName": "TamperingSwitch",
 "Time": "2021-05-03T09:59:00.863+00:00",
 "Source": {
 "Channel": 0
 },
 "Data": {

```

SUNAPI 169


```
 "State": false
 }
 },
 {
 "EventName": "DTMFReceived",
 "Time": "2021-05-03T09:59:00.863+00:00",
 "Source": {
 "Channel": 0,
 "Index": 1
 },
 "Data": {
 "State": false
 }
 },
 {
 "EventName": "SystemEvent.TimeChange",
 "Time": "2021-05-03T09:59:00.864+00:00",
 "Source": {
 "Channel": 0
 },
 "Data": {
 "State": false
 }
 },
 {
 "EventName": "SystemEvent.PowerReboot",
 "Time": "2021-05-03T09:59:00.864+00:00",
 "Source": {
 "Channel": 0
 },
 "Data": {
 "State": false
 }
 },
 {
 "EventName": "SystemEvent.FWUpdate",
 "Time": "2021-05-03T09:59:00.864+00:00",
 "Source": {
 "Channel": 0
 },
 "Data": {

```

170 Application Programmer’s Guide


```
 "State": false
 }
 },
 {
 "EventName": "SystemEvent.FactoryReset",
 "Time": "2021-05-03T09:59:00.864+00:00",
 "Source": {
 "Channel": 0
 },
 "Data": {
 "State": false
 }
 },
 {
 "EventName": "SystemEvent.ConfigurationBackup",
 "Time": "2021-05-03T09:59:00.864+00:00",
 "Source": {
 "Channel": 0
 },
 "Data": {
 "State": false
 }
 },
 {
 "EventName": "SystemEvent.ConfigurationRestore",
 "Time": "2021-05-03T09:59:00.864+00:00",
 "Source": {
 "Channel": 0
 },
 "Data": {
 "State": false
 }
 },
 {
 "EventName": "SystemEvent.ConfigChange",
 "Time": "2021-05-03T09:59:00.864+00:00",
 "Source": {
 "Channel": 0
 },
 "Data": {
 "State": false

```

SUNAPI 171


```
 }
 },
 {
 "EventName": "SystemEvent.SDFormat",
 "Time": "2021-05-03T09:59:00.864+00:00",
 "Source": {
 "Channel": 0
 },
 "Data": {
 "State": false
 }
 },
 {
 "EventName": "SystemEvent.SDFail",
 "Time": "2021-05-03T09:59:00.864+00:00",
 "Source": {
 "Channel": 0
 },
 "Data": {
 "State": false
 }
 },
 {
 "EventName": "SystemEvent.SDFull",
 "Time": "2021-05-03T09:59:00.864+00:00",
 "Source": {
 "Channel": 0
 },
 "Data": {
 "State": false
 }
 },
 {
 "EventName": "SystemEvent.SDInsert",
 "Time": "2021-05-03T09:59:00.864+00:00",
 "Source": {
 "Channel": 0
 },
 "Data": {
 "State": true
 }

```

172 Application Programmer’s Guide


```
 },
 {
 "EventName": "SystemEvent.SDRemove",
 "Time": "2021-05-03T09:59:00.864+00:00",
 "Source": {
 "Channel": 0
 },
 "Data": {
 "State": false
 }
 },
 {
 "EventName": "SystemEvent.NASConnect",
 "Time": "2021-05-03T09:59:00.864+00:00",
 "Source": {
 "Channel": 0
 },
 "Data": {
 "State": false
 }
 },
 {
 "EventName": "SystemEvent.NASDisconnect",
 "Time": "2021-05-03T09:59:00.864+00:00",
 "Source": {
 "Channel": 0
 },
 "Data": {
 "State": true
 }
 },
 {
 "EventName": "SystemEvent.NASFail",
 "Time": "2021-05-03T09:59:00.864+00:00",
 "Source": {
 "Channel": 0
 },
 "Data": {
 "State": false
 }
 },

```

SUNAPI 173


```
 {
 "EventName": "SystemEvent.NASFull",
 "Time": "2021-05-03T09:59:00.864+00:00",
 "Source": {
 "Channel": 0
 },
 "Data": {
 "State": false
 }
 },
 {
 "EventName": "SystemEvent.NASFormat",
 "Time": "2021-05-03T09:59:00.864+00:00",
 "Source": {
 "Channel": 0
 },
 "Data": {
 "State": false
 }
 }
 ]
 }

### **20.7. Metadata format**

#### **20.7.1. CallRequest event**

 <wsnt:NotificationMessage xmlns:wsnt="http://docs.oasis-open.org/wsn/b-2">
 <wsnt:Topic
 Dialect="http://www.onvif.org/ver10/tev/topicExpression/ConcreteSet
 xmlns:wsnt=http://docs.oasis-open.org/wsn/b-2
 xmlns:tns1=http://www.onvif.org/ver10/topics">tns1:Device/Trigger/CallReques
 t</wsnt:Topic>
 <wsnt:Message>
 <tt:Message UtcTime="2020-07-14T15:54:44Z"
 xmlns:tt="https://www.onvif.org/ver10/schema/">
 <tt:Source>
 <tt:SimpleItem Name="SourceToken" Value="CallRequest-1"/>
 </tt:Source>
 <tt:Data>
 <tt:SimpleItem Name="State" Value="true"/>

```

174 Application Programmer’s Guide


```
 </tt:Data>
 </tt:Message>
 </wsnt:Message>
 </wsnt:NotificationMessage>

#### **20.7.2. TamperingSwitch event**

 <wsnt:NotificationMessage xmlns:wsnt="http://docs.oasis-open.org/wsn/b-2">
 <wsnt:Topic
 Dialect="http://www.onvif.org/ver10/tev/topicExpression/ConcreteSet
 xmlns:wsnt=http://docs.oasis-open.org/wsn/b-2
 xmlns:tns1=http://www.onvif.org/ver10/topics">tns1:Device/Trigger/TamperingS
 witch</wsnt:Topic>
 <wsnt:Message>
 <tt:Message UtcTime="2020-07-14T15:54:44Z"
 xmlns:tt="https://www.onvif.org/ver10/schema/">
 <tt:Source>
 <tt:SimpleItem Name="SourceToken"
 Value="TamperingSwitchToken-1"/>
 </tt:Source>
 <tt:Data>
 <tt:SimpleItem Name="State" Value="true"/>
 </tt:Data>
 </tt:Message>
 </wsnt:Message>
 </wsnt:NotificationMessage>

#### **20.7.3. DTMF event**

 <wsnt:NotificationMessage xmlns:wsnt="http://docs.oasis-open.org/wsn/b-2">
 <wsnt:Topic
 Dialect="http://www.onvif.org/ver10/tev/topicExpression/ConcreteSet
 xmlns:wsnt=http://docs.oasis-open.org/wsn/b-2
 xmlns:tns1=http://www.onvif.org/ver10/topics">tns1:Device/Trigger/DTMF</wsnt
 :Topic>
 <wsnt:Message>
 <tt:Message UtcTime="2020-07-14T15:54:44Z"
 xmlns:tt="https://www.onvif.org/ver10/schema/">
 <tt:Source>
 <tt:SimpleItem Name="RuleName" Value="DTMF-1"/>

```

SUNAPI 175


```
 </tt:Source>
 <tt:Data>
 <tt:SimpleItem Name="State" Value="true"/>
 </tt:Data>
 </tt:Message>
 </wsnt:Message>
 </wsnt:NotificationMessage>

```

176 Application Programmer’s Guide


## **Chapter 21. Sample Application to get Device** **Information**

Simple client example using cURL library.

```
 #include <string.h>
 #include <iostream>
 #include <sys/stat.h>
 #include <fcntl.h>
 #include <curl/curl.h>
 using namespace std;

 class CurlObject
 {
 public:
 CurlObject(string &, string &, string &); //URL, Username, Password
 virtual ~CurlObject();
 bool Get();         //Process the request
 string GetLastError();   // To get Error Message
 string GetResponseBody();  // To get Response Body
 string GetResponseHeader(); // To get Response Header
 private:
 void SetDefaultCurlOptions();
 static int StringWriter(char *, size_t, size_t, string *); //Callback
 Function
 private:
 CURL *mpCurl;
 char mErrorStr[CURL_ERROR_SIZE];
 string mUrl;
 string mAuth;
 string mResponseBody;
 string mResponseHeader;
 };

 CurlObject::CurlObject(string &sUri, string &sUser, string &sPassword)
 {
 mUrl = sUri;
 mAuth = sUser + ":" + sPassword;
 memset(mErrorStr, 0, sizeof(mErrorStr));
 mpCurl = curl_easy_init();
 SetDefaultCurlOptions();

```

SUNAPI 177


```
 cout << mUrl << endl;
 }

 CurlObject::~CurlObject()
 {
 curl_easy_cleanup(mpCurl);
 }

 void CurlObject::SetDefaultCurlOptions()
 {
 if (mpCurl)
 {
 curl_easy_setopt(mpCurl, CURLOPT_NOSIGNAL, 1);
 curl_easy_setopt(mpCurl, CURLOPT_TIMEOUT, 60);    //Request
 Timeout
 curl_easy_setopt(mpCurl, CURLOPT_CONNECTTIMEOUT, 10); //Connection
 Timeout
 curl_easy_setopt(mpCurl, CURLOPT_ERRORBUFFER, mErrorStr);
 curl_easy_setopt(mpCurl, CURLOPT_URL, mUrl.c_str());
 curl_easy_setopt(mpCurl, CURLOPT_HTTPAUTH, CURLAUTH_DIGEST);
 //Digest Authentication
 curl_easy_setopt(mpCurl, CURLOPT_USERPWD, mAuth.c_str());
 curl_easy_setopt(mpCurl, CURLOPT_HEADER, 0);
 curl_easy_setopt(mpCurl, CURLOPT_FOLLOWLOCATION, 1);
 curl_easy_setopt(mpCurl, CURLOPT_SSL_VERIFYHOST, 2);
 //SSL
 curl_easy_setopt(mpCurl, CURLOPT_SSL_VERIFYPEER, 0);
 //SSL
 curl_easy_setopt(mpCurl, CURLOPT_HEADERFUNCTION, StringWriter);
 //Callback Function
 curl_easy_setopt(mpCurl, CURLOPT_WRITEHEADER, &mResponseHeader);
 //Response Header
 }
 }

 string CurlObject::GetLastError()
 {
 return mErrorStr;
 }

 string CurlObject::GetResponseBody()

```

178 Application Programmer’s Guide


```
 {
 return mResponseBody;
 }

 string CurlObject::GetResponseHeader()
 {
 return mResponseHeader;
 }

 bool CurlObject::Get()
 {
 bool retVal = true;
 if (mpCurl)
 {
 curl_easy_setopt(mpCurl, CURLOPT_HTTPGET, 1);
 curl_easy_setopt(mpCurl, CURLOPT_WRITEFUNCTION, StringWriter);
 curl_easy_setopt(mpCurl, CURLOPT_WRITEDATA, &mResponseBody);
 if (curl_easy_perform(mpCurl) != CURLE_OK)
 {
 cout << mErrorStr << endl;
 retVal = false;
 }
 }
 return retVal;
 }

 int CurlObject::StringWriter(char *pData, size_t size, size_t nmem, string
 *sBuffer)
 {
 int result = 0;
 if (sBuffer)
 {
 sBuffer->append(pData, size * nmem);
 result = size * nmem;
 }
 return result;
 }

 int main(int argc, char *argv[])
 {
 string sIp = argv[1];

```

SUNAPI 179


```
 //Device IP
 string sUser = argv[2];
 //Username
 string sPwd = argv[3];
 //Password
 string sCommand = "/stw-cgi/system.cgi?msubmenu=deviceinfo&action=view";
 //SUNAPI Command
 string sUrl = sIp + sCommand;
 CurlObject *pCurl = new CurlObject(sUrl, sUser, sPwd);
 if (pCurl)
 {
 if (pCurl->Get())
 cout << pCurl->GetResponseBody() << endl; //Response Body
 else
 cout << pCurl->GetLastError() << endl; //Error Message
 delete pCurl;
 }
 return 0;
 }

```

180 Application Programmer’s Guide


## **Chapter 22. References**

[1] SUNAPI_ipinstaller_2.6.3.pdf


[2] SUNAPI_network_2.6.3.pdf


[3] SUNAPI_system_2.6.3.pdf


[4] SUNAPI_video_audio_2.6.3.pdf


[5] SUNAPI_ptz_2.6.3.pdf


[6] SUNAPI_recording_2.6.3.pdf


[7] SUNAPI_event_2.6.3.pdf


[8] SUNAPI_attributes_2.6.3.pdf


[9] SUNAPI_image_2.6.3.pdf


[10] SUNAPI_io_2.6.3.pdf


[11] SUNAPI_security_2.6.3.pdf


[[12] ONVIF Streaming Spec](https://www.onvif.org/specs/stream/ONVIF-Streaming-Spec.pdf)


[13] SUNAPI_bypass_2.6.3.pdf


[14] SUNAPI_ai_2.6.3.pdf


[15] SUNAPI_display_2.6.3.pdf


[16] SUNAPI_transfer_2.6.3.pdf


SUNAPI 181


