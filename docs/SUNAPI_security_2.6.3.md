# Security


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

1. Overview . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . 6

1.1. Description . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . 6

2. IP Address Filtering . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . 7

2.1. Description . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . 7

2.2. Syntax . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . 7

2.3. Parameters . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . 7

2.4. Examples . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . 8

2.4.1. Getting the current IP filtering settings . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . 8

2.4.2. Setting an IPv6 address and enabling filtering . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . 10

2.4.3. Updating an IPv6 address and disabling filtering . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . 11

2.4.4. Deleting an IPv4 address from IP filtering list . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . 11

3. 802.1x Setup. . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . 13

3.1. Description . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . 13

3.2. Syntax . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . 13

3.3. Parameters . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . 13

3.4. Examples . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . 14

3.4.1. Getting the current 802.1x settings. . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . 14

3.4.2. Setting the EAPOL . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . 16

3.4.3. Installing an 802.1x certificate . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . 16

3.4.4. Deleting a certificate . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . 18

4. RTSP Authentication . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . 19

4.1. Description . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . 19

4.2. Syntax . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . 19

4.3. Parameters . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . 19

4.4. Examples . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . 19

4.4.1. Getting the current RTSP authentication settings . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . 19

4.4.2. Enabling anonymous RTSP authentication . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . 20

5. SSL (HTTPS) Settings. . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . 21

5.1. Description . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . 21

5.2. Syntax . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . 21

5.3. Parameters . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . 21

5.4. Examples . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . 24

5.4.1. Getting the current SSL settings . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . 24

5.4.2. Enabling HTTPS. . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . 27

5.4.3. Installing a certificate . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . 27

5.4.4. Add a self-signed certificate . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . 28


2 Security


5.4.5. Use a specific certificate . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . 29

5.4.6. Deleting a certificate . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . 29

6. Guest User Login. . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . 30

6.1. Description . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . 30

6.2. Syntax . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . 30

6.3. Parameters . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . 30

6.4. Examples . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . 30

6.4.1. Getting the current guest login setting . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . 30

6.4.2. Enabling guest login . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . 31

7. User Configuration . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . 32

7.1. Description . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . 32

7.2. Syntax . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . 32

7.3. Parameters . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . 32

7.4. Examples . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . 37

7.4.1. Getting current users settings . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . 37

7.4.2. Getting ‘user1’ . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . 42

7.4.3. Adding a user . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . 43

7.4.4. Updating ‘user2’ to give permission for PTZ control . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . 45

7.4.5. Updating password . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . 45

7.4.6. Deleting ‘user2’ . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . 46

7.4.7. Getting current users count & maximum users count. . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . 47

8. User Group Configuration . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . 48

8.1. Description . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . 48

8.2. Syntax . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . 48

8.3. Parameters . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . 48

8.4. Examples . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . 50

8.4.1. Getting current user group settings . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . 50

8.4.2. Getting ‘Group 1’ user group settings . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . 55

8.4.3. Adding a user group . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . 59

8.4.4. Updating a user group . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . 59

8.4.5. Removing a user group. . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . 59

9. Authority. . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . 60

9.1. Description . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . 60

9.2. Syntax . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . 60

9.3. Parameters . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . 60

9.4. Examples . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . 61

9.4.1. Getting current permission settings . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . 61

9.4.2. Setting the access permission . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . 62

10. Additional Password . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . 63

10.1. Description . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . 63


SUNAPI 3


10.2. Syntax . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . 63

10.3. Parameters . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . 63

10.4. Examples . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . 64

10.4.1. Getting additional password settings for all users . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . 64

10.4.2. Getting additional password settings for user "User1". . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . 65

10.4.3. Adding a Password for a User . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . 66

10.4.4. Updating Password . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . 66

10.4.5. Removing all Passwords for a User . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . 66

10.4.6. Removing Password Index 1,2,3 . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . 66

11. Getting public key . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . 67

11.1. Description . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . 67

11.2. Syntax . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . 67

11.3. Parameters . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . 67

11.4. Examples . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . 67

12. Configure default camera user credentials in NVR . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . 70

12.1. Description . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . 70

12.2. Syntax . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . 70

12.3. Parameters . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . 70

12.4. Examples . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . 71

12.4.1. Viewing a user. . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . 71

12.4.2. Adding a user . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . 72

12.4.3. Updating a user . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . 72

12.4.4. Removing a user. . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . 72

13. Getting Client Mutual Authenticate Status . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . 73

13.1. Description . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . 73

13.2. Syntax . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . 73

13.3. Parameters . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . 73

13.4. Examples . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . 74

14. Getting TLS Configuration . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . 76

14.1. Description . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . 76

14.2. Syntax . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . 76

14.3. Parameters . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . 76

14.4. Examples . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . 77

14.4.1. Getting all versions of the TLS configurations. . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . 77

14.4.2. Getting ‘TLSv1_3’ configuration . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . 78

14.4.3. Enabling TLS v1.2 and v1.3 . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . 79

14.4.4. Setting cipher mode to compatible mode . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . 80

15. Getting Camera’s validation status from NVR . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . 81

15.1. Description . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . 81

15.2. Syntax . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . 81


4 Security


15.3. Parameters . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . 81

15.4. Examples . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . 81

16. CA Certificate Settings . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . 84

16.1. Description . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . 84

16.2. Syntax . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . 84

16.3. Parameters . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . 84

16.4. Examples . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . 85

16.4.1. Getting the CA certificates . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . 85

16.4.2. Installing CA certificate . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . 87

16.4.3. Deleting a certificate . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . 88


SUNAPI 5


## **Chapter 1. Overview**
### **1.1. Description**

Hanwha Vision provides network security and authentication methods to support secure data transfers.

**security.cgi** configures the general security settings for Hanwha Vision video surveillance devices.


The following submenus of security.cgi are used for network security settings:


 - **ipfilter** : Requests and configures IP address filtering to block or allow certain IP addresses.


 - **802Dot1x** : Requests and configures the parameters required for accessing an 802.1x protected

network. **rtsp** : Requests and selects the RTSP authentication method.


 - **ssl** : Requests and configures the SSL (Secure Socket Layer) settings.


 - **guest** : Requests and enables/disables guest logins.


 - **users** : Requests, adds and deletes system users and sets access permissions.


 - **usergroups** : Requests, adds and deletes system user groups and sets access permissions for the user

groups.


 - **authority** : Sets several access permissions and auto logout times.


 - **additionalpassword** : Sets multiple passwords for the user.


 - **rsa** : Requests public RSA key


 - **camerausers** : Configures to try connecting cameras with the corresponding IDs and passwords when

NVR discovers them or test connection has been found.


 - **clienthttpsstatus** : Requests the mutual authentication status of the client.


 - **tlsversion:** Requests and configures the TLS (Transport Layer Security) settings.


 - **cameravalidationstatus** : Requests the camera validation status from NVR.


 - **cacertificate** : Configures and handles the CA certificate used in a device.


It is highly recommended not to use plain text passwords in the submenus. Password



**NOTE**



encryption should be used. Refer to the Application Programming Guide Document for

details.



6 Security


## **Chapter 2. IP Address Filtering**
### **2.1. Description**

The **ipfilter** submenu configures IP address filtering. This submenu controls the device access based IP

filter settings. The feature provides both Allow and Deny filtering types. Deny filtering allows all IP

addresses except the listed addresses, while Allow filtering blocks all IP addresses except the listed

addresses.


**Access level**

|Action|Camera|NVR|
|---|---|---|
|view|Admin|User|
|set|Admin|User|
|add, update|Admin|User|
|remove|Admin|User|


### **2.2. Syntax**

```
 http://<Device IP>/stw-cgi/security.cgi?msubmenu=
 ipfilter &action=<value>[&<parameter>=<value>...]

### **2.3. Parameters**

```














|Action|Parameter|Request/<br>Response|Type/<br>Value|Description|
|---|---|---|---|---|
|view||||Reads the IP address filtering settings.|
|set|AccessType|REQ, RES|<enum><br>Allow, Deny|Access type<br>• Allow: Allows access to listed IP<br>addresses<br>• Deny: Blocks access to listed IP<br>addresses<br>**Note**<br>**AccessType** must be sent together<br>with the**set** action.|
||IPType|REQ, RES|<enum>|IP type|


SUNAPI 7


|Action|Parameter|Request/<br>Response|Type/<br>Value|Description|
|---|---|---|---|---|
|add, update|IPIndex|REQ, RES|<int>|Position of a IP address in the list<br>**Note**<br>**IPType**, **IPIndex**, and**Enable** must<br>be sent together for the**update**<br>action.|
||IPType|REQ, RES|<enum><br>IPv4, IPv6|IP type<br>The IP type is either IPv4 or IPv6.<br>**Note**<br>**IPType**, **Address**, and**Enable**<br>parameters must be sent together<br>for the**add** action.|
||Address|REQ, RES|<string>|IP address to be configured for device<br>access<br>IPv4 and IPv6 are both allowed.|
||Mask|REQ, RES|<int>|Netmask for the IP address|
||Enable|REQ, RES|<bool><br>True, False|Whether to apply IPv4 or IPv6 address<br>filtering|
|remove|IPType|REQ|<enum><br>IPv4, IPv6|IP type that is to be removed.<br>**Note**<br>**IPType** and**IPIndex** must be sent<br>together for the**remove** action.|
||IPIndex|REQ|<int>|IP Index that is to be removed.|

### **2.4. Examples**

#### **2.4.1. Getting the current IP filtering settings**

REQUEST

```
 http://<Device IP>/stw-cgi/security.cgi?msubmenu=ipfilter&action=view

```

TEXT RESPONSE

```
 HTTP/1.0 200 OK
 Content-type: text/plain
 <Body>

```

8 Security


```
 "ipfilter.IPType.IPIndex=Address/Mask/Enable"
 AccessType=Deny
 ipfilter.IPv4.1=192.168.75.135/32/False
 ipfilter.IPv6.1=2001:1:1:1:1:1:1:1/128/True

```

JSON RESPONSE (For Camera)

```
 HTTP/1.0 200 OK
 Content-type: application/json
 <Body>

 {
 "AccessType": "Deny",
 "IPFilters": [
 {
 "IPType": "IPv4",
 "Filters": [
 {
 "IPIndex": 1,
 "Address": "192.168.75.135",
 "Mask": 32,
 "Enable": false
 }
 ]
 },
 {
 "IPType": "IPv6",
 "Filters": [
 {
 "IPIndex": 1,
 "Address": "2001:1:1:1:1:1:1:1",
 "Mask": 128,
 "Enable": true
 }
 ]
 }
 ]
 }

```

SUNAPI 9


JSON RESPONSE (For NVR)

```
 HTTP/1.0 200 OK
 Content-type: application/json
 <Body>

 {
 "IPFilters": [
 {
 "IPType": "IPv4",
 "AccessType": "Deny",
 "Filters": [
 {
 "IPIndex": 1,
 "Address": "192.168.75.135",
 "Mask": 32,
 "Enable": false
 }
 ]
 },
 {
 "IPType": "IPv6",
 "AccessType": "Allow",
 "Filters": [
 {
 "IPIndex": 1,
 "Address": "2001:1:1:1:1:1:1:1",
 "Mask": 128,
 "Enable": true
 }
 ]
 }
 ]
 }

#### **2.4.2. Setting an IPv6 address and enabling filtering**
```

To add the IP address to be filtered with the **add** action, the **IPType**, **Address**, and **Enable** parameters

must be set.


10 Security


REQUEST

```
 http://<Device IP>/stw cgi/security.cgi?msubmenu=ipfilter&action=add&&IPType=IPv6&Address=fe80::209
 1:18ff:fe71:1111&Mask=32&Enable=True

```

TEXT RESPONSE

```
 HTTP/1.0 200 OK
 Content-type: text/plain
 <Body>

 OK
 IPIndex=1

```

JSON RESPONSE

```
 HTTP/1.0 200 OK
 Content-type: application/json
 <Body>

 {
 "Response": "Success"
 }

#### **2.4.3. Updating an IPv6 address and disabling filtering**
```

To modify a filtered address via the **update** action, the **IPType**, **IPIndex**, and **Enable** parameters must be

set.


REQUEST

```
 http://<Device IP>/stw cgi/security.cgi?msubmenu=ipfilter&action=update&IPIndex=1&IPType=IPv6&Addre
 ss=fe80::2091:18ff:fe71:1111&Mask=32&Enable=False

#### **2.4.4. Deleting an IPv4 address from IP filtering list**
```

To remove a filtered address with the **remove** action, the **IPType** and **IPIndex** parameters must be set.


SUNAPI 11


REQUEST

```
 http://<Device IP>/stw cgi/security.cgi?msubmenu=ipfilter&action=remove&IPIndex=1&IPType=IPv4

```

12 Security


## **Chapter 3. 802.1x Setup**
### **3.1. Description**

The **802Dot1x** submenu requests and configures the parameters required for accessing an 802.1x

protected network.


**Access level**

|Action|Camera|NVR|
|---|---|---|
|view|Admin|User|
|set|Admin|User|
|install|Admin|User|
|remove|Admin|User|


### **3.2. Syntax**

```
 http://<Device IP>/stw-cgi/security.cgi?msubmenu=
 802Dot1x &action=<value>[&<parameter>=<value>...]

### **3.3. Parameters**

```




















|Action|Parameter|Request/<br>Response|Type/<br>Value|Description|
|---|---|---|---|---|
|view||||Reads the 802.1x settings|
||Status|RES|<enum><br>Unauthorized,<br>Authorized, Stopped|Status (read-only)|
||CACertificateInstalled|RES|<bool><br>True, False|Whether or not a CA certificate is<br>installed|
||ClientCertificateInstall<br>ed|RES|<bool><br>True, False|Whether or not a public certificate<br>containing the client certificate<br>key is installed|
||ClientPrivateKeyInstall<br>ed|RES|<bool><br>True, False|Whether or not a public certificate<br>containing the client private key is<br>installed|
||IsPasswordSet|RES|<bool><br>True, False|Whether or not the EAPOL<br>password is set|
|set|InterfaceName|REQ, RES|<string>|Interface name (read-only for<br>network cameras)|


SUNAPI 13


|Action|Parameter|Request/<br>Response|Type/<br>Value|Description|
|---|---|---|---|---|
||Enable|REQ, RES|<bool><br>True, False|Whether to activate 802.1x mode|
||EAPOLVersion|REQ, RES|<enum><br>1, 2|EAPOL (Extensible Authentication<br>Protocol over LAN) version|
||EAPOLId|REQ, RES|<string>|EAPOL ID|
||EAPOLPassword|REQ, RES|<string>|EAPOL password|
||IsEAPOLPasswordEnc<br>rypted|REQ|<bool><br>True, False|If set to true, EAPOLPassword is<br>encrypted using the public key<br>provided by the**rsa** submenu of<br>**security**.cgi and sent as post<br>payload. Refer to the Application<br>Programmer’s Guide.|
||ClientCertificateInUse|REQ, RES|<string>|Set or get the client certificate to<br>(in) use|
||CACertificateInUse|REQ,RES|<string>|Set or get the CA certificate to (in)<br>use|
||EAPOLType|REQ, RES|<enum><br>EAP-TLS, LEAP|EAPOL type|
|install|InterfaceName|REQ|<string>|Interface name<br>**NVR ONLY**<br>|
|remove|CertificateType|REQ|<enum><br>CACertificate,<br>ClientCertificate,<br>ClientPrivateKey|Certificate type<br>**Note**<br>**CertificateType** must be sent<br>together with the**remove**<br>action|
||InterfaceName|REQ|<string>|Interface name<br>**NVR ONLY**<br>|

### **3.4. Examples**

#### **3.4.1. Getting the current 802.1x settings**

REQUEST

```
 http://<Device IP>/stw-cgi/security.cgi?msubmenu=802Dot1x&action=view

```

14 Security


TEXT RESPONSE

```
 HTTP/1.0 200 OK
 Content-type: text/plain
 <Body>

 InterfaceName=1a5a97d2-464a-4222-91c6-140ff36b82b6
 Enable=False
 EAPOLType=EAP-TLS
 Status=Stopped
 CACertificateInstalled=False
 ClientCertificateInstalled=False
 ClientPrivateKeyInstalled=False
 ClientCertificateInUse=
 CACertificateInUse=
 EAPOLVersion=1
 EAPOLId=test
 EAPOLPassword=test

```

JSON RESPONSE

```
 HTTP/1.0 200 OK
 Content-type: application/json
 <Body>

 {
 "IEEE802Dot1x": [
 {
 "InterfaceName": "NetworkInterface1",
 "Enable": false,
 "Status": "Stopped",
 "CACertificateInstalled": false,
 "ClientCertificateInstalled": false,
 "ClientPrivateKeyInstalled": false,
 "ClientCertificateInUse": "",
 "CACertificateInUse": "",
 "EAPOLVersion": "1",
 "EAPOLId": "",
 "EAPOLPassword": "",
 "EAPOLType": "EAP-TLS",

```

SUNAPI 15


```
 "IsPasswordSet": false
 }
 ]
 }

#### **3.4.2. Setting the EAPOL**
```

Setting the EAPOL version to ‘1’, the EAPOL ID to ‘test’ and the EAPOL password to ‘123’


REQUEST

```
 http://<Device IP>/stw cgi/security.cgi?msubmenu=802Dot1x&action=set&EAPOLVersion=1&EAPOLId=test&EA
 POLPassword=123

```

The following request example is for NVR only.


REQUEST

```
 http://<Device IP>/stw cgi/security.cgi?msubmenu=802Dot1x&action=set&InterfaceName=Network2&EAPOLVe
 rsion=1&EAPOLId=test& EAPOLPassword=123

#### **3.4.3. Installing an 802.1x certificate**
```

REQUEST

```
 http://<Device IP>/stw-cgi/security.cgi?msubmenu=802Dot1x&action=install

```

When requesting for an 802.1x certificate to be installed, data should be sent via the POST method in the

following format.


The certtype value is the CACertificate, ClientCertificate or ClientPrivateKey. The certlength value is the

data size of the certificate. The certdata value is certificate data.

```
 <SetData802Dot1x>
 <PublicCertType>certtype</PublicCertType>
 <CertLength>certlength</CertLength>
 <CertData>certdata</CertData>
 </SetData802Dot1x>

```

(The following example is for NVR only.)


16 Security


```
<SetData802Dot1x>
<CertificateName>certname</CertificateName>
<PublicCertType>certtype</PublicCertType>
<CertLength>certlength</CertLength>
<CertData>certdata</CertData>
</SetData802Dot1x>

```

Now ssl and cacertificate handles all the certificates used in a device. So we recommend



**NOTE**



using those submenus to install new certificates and just use **ClientCertificateInUse** and

**CACertificateInUse** parameter to set the certificates that you want to use.



**CURL command**


802.1x certificate install can be tested with CURL as below. To learn about CURL, please refer to

[http://curl.haxx.se.](http://curl.haxx.se)


To get a JSON response add the -H ted with CURL as shown below in the header of the
**NOTE**

request.

```
 curl -v --digest -u <userid>:<password> --data-urlencode @802dot1x.xml
 "http://<Device IP>/stw-cgi/security.cgi?msubmenu=802Dot1x&action=install"
 -H "Expect:"

```

(The following example is for NVR only.)

```
 curl --digest -u <userid>:<password> "http://<Device IP>/stw cgi/security.cgi?msubmenu=802Dot1x&action=install&InterfaceName=Network2" -H
 "Expect:" --data-urlencode @802dot1x.xml

```

The above command will produce a request to the device as below:

```
 POST /stw-cgi/security.cgi?msubmenu=802Dot1x&action=install HTTP/1.1
 Content-Length: 1985
 Content-Type: application/x-www-form-urlencoded

```

TEXT RESPONSE

```
 OK

```

SUNAPI 17


JSON RESPONSE

```
 {
 "Response": "Success"
 }

#### **3.4.4. Deleting a certificate**
```

REQUEST

```
 http://<Device IP>/stw cgi/security.cgi?msubmenu=802Dot1x&action=remove&CertificateType=CACertifica
 te

```

The following request example is for NVR only.


REQUEST

```
 http://<Device IP>/stw cgi/security.cgi?msubmenu=802Dot1x&action=remove&InterfaceName=Network2&Cert
 ificateType=CACertificate

```

18 Security


## **Chapter 4. RTSP Authentication**
### **4.1. Description**

The **rtsp** submenu selects the RTSP authentication method.


**Access level**

|Action|Camera|NVR|
|---|---|---|
|view|Admin|User|
|set|Admin|User|


### **4.2. Syntax**

```
 http://<Device IP>/stw-cgi/security.cgi?msubmenu=
 rtsp &action=<value>[&<parameter>=<value>...]

### **4.3. Parameters**

```










|Action|Parameter|Request/<br>Response|Type/<br>Value|Description|
|---|---|---|---|---|
|view||||Reads the RTSP authentication<br>settings.|
||RTSPAuthentication|RES|<enum><br>Anonymous,<br>Protected|Whether to allow anonymous<br>access without login for RTSP URL<br>requests|
|set|RTSPAuthentication|REQ, RES|<enum><br>Anonymous,<br>Protected|Whether to allow anonymous<br>access without logging in for<br>RTSP URL requests (read-only for<br>NVR)<br>**Note**<br>**RTSPAuthentication** must be<br>sent together with the**set**<br>action.|

### **4.4. Examples**




#### **4.4.1. Getting the current RTSP authentication settings**

SUNAPI 19


REQUEST

```
 http://<Device IP>/stw-cgi/security.cgi?msubmenu=rtsp&action=view

```

TEXT RESPONSE

```
 HTTP/1.0 200 OK
 Content-type: text/plain
 <Body>

 RTSPAuthentication=Protected

```

JSON RESPONSE

```
 HTTP/1.0 200 OK
 Content-type: application/json
 <Body>

 {
 "RTSPAuthentication": "Protected"
 }

#### **4.4.2. Enabling anonymous RTSP authentication**
```

To use the **set** action, the **RTSPAuthentication** parameter must be set at the same time.


REQUEST

```
 http://<Device IP>/stw cgi/security.cgi?msubmenu=rtsp&action=set&RTSPAuthentication=Anonymous

```

20 Security


## **Chapter 5. SSL (HTTPS) Settings**
### **5.1. Description**

The **ssl** submenu configures the SSL (Secure Socket Layer) settings.


**Access level**

|Action|Camera|NVR|
|---|---|---|
|view|Admin|User|
|set|Admin|User|
|install|Admin|User|
|remove|Admin|User|


### **5.2. Syntax**

```
 http://<Device IP>/stw-cgi/security.cgi?msubmenu=
 ssl &action=<value>[&<parameter>=<value>...]

### **5.3. Parameters**

```





































|Action|Parameter|Request/<br>Response|Type/<br>Value|Description|
|---|---|---|---|---|
|view||||Reads the SSL (HTTPS) settings|
||PublicCertificateInstall<br>ed|RES|<bool><br>True, False|Whether or not a public certificate<br>is installed (read-only)|
||PublicCertificateName|RES|<csv>|Public certificate name|
||UpdateDeviceHostna<br>me|RES|<bool>|Whether device hostname is<br>updated|
||CertificateInUse|RES|<string>|Name of certificate currently in<br>use|
||Certificate.#.Certificat<br>eName|RES|<string>|Certificate name|
||Certificate.#.Type|RES|<enum><br>Unique, SelfSigned,<br>Public|Certificate type|
||Certificate.#.Subject|RES|<string>|Subject of the certificate|
||Certificate.#.SubjectAl<br>ternativeName|RES|<string>|Subject alternative name (SAN)|



SUNAPI 21


|Action|Parameter|Request/<br>Response|Type/<br>Value|Description|
|---|---|---|---|---|
||Certificate.#.Issuer|RES|<string>|Issuer|
||Certificate.#.IssueDat<br>e|RES|<string>|Issued date|
||Certificate.#.ExpiryDat<br>e|RES|<string>|Expiry date|
||Certificate.#.Version|RES|<string>|Version|
||Certificate.#.SerialNu<br>mber|RES|<string>|Serial number|
||Certificate.#.Signatur<br>e|RES|<string>|Signature|
||Certificate.#.Thumbpr<br>int|RES|<string>|Thumbprint|
||Certificate.#.IsRemov<br>able|RES|<bool>|Whether the certificate can be<br>deleted|
||Certificate.#.IsEncrypt<br>ed|RES|<bool>|Whether the certificate is<br>encrypted|
|add|CertificateName|REQ|<string>|The name of the certificate|
||Type|REQ|<enum><br>SelfSigned|The type of the certificate<br>• SelfSigned: Access using a<br>built-in certificate from the<br>device|
||CommonName|REQ|<string>|Common name (CN)|
||SubjectAlternativeNa<br>me|REQ|<string>|Subject alternative name (SAN)|
||ExpiryDate|REQ|<string>|Certificate expiry date|
||Country|REQ|<string>|Country ©<br>**Note**<br>ISO-3166-1 alpha-2 codes|
||Province|REQ|<string>|Province (ST)|
||Location|REQ|<string>|Location (L)|
||Organization|REQ|<string>|Organization (O)|
||Division|REQ|<string>|Division (OU)|


22 Security


|Action|Parameter|Request/<br>Response|Type/<br>Value|Description|
|---|---|---|---|---|
||EmailID|REQ|<string>|E-mail address<br>**Note**<br>Multiple e-mails are separated<br>by commas|
|set|Policy|REQ, RES|<enum><br>HTTP,<br>HTTPSProprietary,<br>HTTPSPublic,<br>HTTPandHTTPSPropri<br>etary,<br>HTTPandHTTPSPublic|Select the SSL method:<br>• HTTP: Access using only HTTP<br>• HTTPSProprietary: Access<br>using a built-in certificate in<br>the device<br>• HTTPSPublic: Access using a<br>certificate that the user has<br>installed (HTTPSPublic mode<br>is valid only when the<br>certificate is installed)<br>• HTTPandHTTPSProprietary:<br>HTTP and HTTPSProprietary<br>mode mode<br>• HTTPandHTTPSPublic: HTTP<br>and HTTPSPublic mode|
||UpdateDeviceHostna<br>me|REQ|<bool><br>True, False|Whether or not device hostname<br>is updated|
||CertificateInUse|REQ|<string>|Name of certificate currently in<br>use|
||ClientCertificateAuthe<br>nticationEnable|REQ, RES|<bool><br>True, False|Whether or not mutual<br>authentication is enabled|



SUNAPI 23


|Action|Parameter|Request/<br>Response|Type/<br>Value|Description|
|---|---|---|---|---|
||ClientCertificateAuthe<br>nticationMode|REQ, RES|<enum><br>ALLOW_ALL_CERT,<br>ALLOW_CERT_FROM_K<br>NOWN_CA,<br>ALLOW_CERT_FROM_V<br>ALID_CLIENT_AND_KN<br>OWN_CA|Select the mode of certificate<br>authentication<br>• ALLOW_ALL_CERT: Allows all<br>connections<br>• ALLOW_CERT_FROM_KNOWN_<br>CA: Allows only mutually<br>authenticated connections<br>• ALLOW_CERT_FROM_VALID_CL<br>IENT_AND_KNOWN_CA: Allows<br>only mutually authenticated<br>connections (including Device<br>ID authentication)<br>**Note**<br>Only works if**Policy** is<br>HTTPSProprietary.|
|remove|CertificateName|REQ|<string>|Certificate name|
|install||||POST method|

### **5.4. Examples**

#### **5.4.1. Getting the current SSL settings**

REQUEST

```
 http://<Device IP>/stw-cgi/security.cgi?msubmenu=ssl&action=view

```

TEXT RESPONSE

```
 HTTP/1.0 200 OK
 Content-type: text/plain
 <Body>

 Policy=HTTPandHTTPSProprietary
 PublicCertificateInstalled=False
 SelfSignedCertificateInstalled=True
 PublicCertificateName=
 UpdateDeviceHostname=False
 CertificateInUse=CA

```

24 Security


```
 ClientCertificateAuthenticationEnable=False
 ClientCertificateAuthenticationMode=ALLOW_ALL_CERT
 Certificate.1.CertificateName=HTW_default
 Certificate.1.Type=Unique
 Certificate.1.Subject=/C=KR/O=Hanwha Vision/OU=Security
 Device/CN=00091867F9BC.hanwhavision.com/serialNumber=5f55694d-f741-41a6 9c6f-ceb4b1ee124c
 Certificate.1.SubjectAlternativeName=00091867F9BC.hanwhavision.com
 Certificate.1.Issuer=/C=KR/O=Hanwha Vision/OU=Security Solution/CN=Hanwha
 Vision Private Root CA 2
 Certificate.1.IssueDate=Dec 1 10:05:06 2020 GMT
 Certificate.1.ExpiryDate=Nov 24 10:05:06 2050 GMT
 Certificate.1.Version=V3
 Certificate.1.SerialNumber=00 12 35 8F
 Certificate.1.Signature=sha256WithRSAEncryption
 Certificate.1.Thumbprint=e268cf387b1a19c5ea3c04be2f24a2053069d8742b9741f1d03
 4937872ce8538
 Certificate.1.IsRemovable=False
 Certificate.1.IsEncrypted=False
 Certificate.2.CertificateName=test
 Certificate.2.Type=Public
 Certificate.2.Subject=/C=FR/ST=Radius/O=Example
 Inc./CN=user@example.org/emailAddress=user@example.org
 Certificate.2.SubjectAlternativeName= Certificate.2.Issuer=/C=FR/ST=Radius/L=Somewhere/O=Example
 Inc./emailAddress=admin@example.org/CN=Example Certificate Authority
 Certificate.2.IssueDate=Jul 1 04:36:15 2021 GMT
 Certificate.2.ExpiryDate=May 10 04:36:15 2031 GMT
 Certificate.2.Version=V3
 Certificate.2.SerialNumber=00
 Certificate.2.Signature=sha256WithRSAEncryption
 Certificate.2.Thumbprint=2b58473f4655282053630336ad25a84eae3e53155030a6fa10e
 dc3576feec51d
 Certificate.2.IsRemovable=True
 Certificate.2.IsEncrypted=True

```

JSON RESPONSE

```
 HTTP/1.0 200 OK
 Content-type: application/json
 <Body>

```

SUNAPI 25


```
 {
 "Policy": "HTTPandHTTPSProprietary",
 "PublicCertificateInstalled": false,
 "SelfSignedCertificateInstalled": true,
 "PublicCertificateName": "",
 "UpdateDeviceHostname": false,
 "CertificateInUse": "CA",
 "ClientCertificateAuthenticationEnable": false,
 "ClientCertificateAuthenticationMode": "ALLOW_ALL_CERT",
 "Certificates": [
 {
 "CertificateName": "HTW_default",
 "Type": "Unique",
 "Subject": "/C=KR/O=Hanwha Vision/OU=Security
 Device/CN=00091867F9BC.hanwhavision.com/serialNumber=5f55694d-f741-41a6 9c6f-ceb4b1ee124c",
 "SubjectAlternativeName": "00091867F9BC.hanwhavision.com",
 "Issuer": "/C=KR/O=Hanwha Vision/OU=Security Solution/CN=Hanwha
 Vision Private Root CA 2",
 "IssueDate": "Dec 1 10:05:06 2020 GMT",
 "ExpiryDate": "Nov 24 10:05:06 2050 GMT",
 "Version": "V3",
 "SerialNumber": "00 12 35 8F ",
 "Signature": "sha256WithRSAEncryption",
 "Thumbprint":
 "e268cf387b1a19c5ea3c04be2f24a2053069d8742b9741f1d034937872ce8538",
 "IsRemovable": false,
 "IsEncrypted": false
 },
 {
 "CertificateName": "test",
 "Type": "Public",
 "Subject": "/C=FR/ST=Radius/O=Example
 Inc./CN=user@example.org/emailAddress=user@example.org",
 "SubjectAlternativeName": "-",
 "Issuer": "/C=FR/ST=Radius/L=Somewhere/O=Example
 Inc./emailAddress=admin@example.org/CN=Example Certificate Authority",
 "IssueDate": "Jul 1 04:36:15 2021 GMT",
 "ExpiryDate": "May 10 04:36:15 2031 GMT",
 "Version": "V3",
 "SerialNumber": "00",

```

26 Security


```
 "Signature": "sha256WithRSAEncryption",
 "Thumbprint":
 "2b58473f4655282053630336ad25a84eae3e53155030a6fa10edc3576feec51d",
 "IsRemovable": true,
 "IsEncrypted": true
 }
 ]
 }

#### **5.4.2. Enabling HTTPS**
```

To use the **set** action, the **Policy** parameter must be set at the same time.


REQUEST

```
 http://<Device IP>/stw cgi/security.cgi?msubmenu=ssl&action=set&Policy=HTTPSPublic

#### **5.4.3. Installing a certificate**
```

REQUEST

```
 http://<Device IP>/stw-cgi/security.cgi?msubmenu=ssl&action=install

```

When requesting a certificate to be installed, data should be sent via the POST method in the following

format.


The certname value is the certificate name. The certlength value is the certificate data size. The certdata

value is the certificate data. The keylength is the key data size. The keydata value is the key data.

```
 <SetHTTPSData>
 <PublicCertName>certname</PublicCertName>
 <CertLength>certlength</CertLength>
 <CertData>certdata</CertData>
 <KeyLength>keylength</KeyLength>
 <KeyData>keydata</KeyData>
 </SetHTTPSData>

```

**CURL command**


The certificate install can be tested with CURL as below. To learn about CURL, please refer to

[http://curl.haxx.se.](http://curl.haxx.se)


SUNAPI 27


**NOTE** To get a JSON response, add the -H "Accept: application/json" header to the request.

```
 curl -v --digest -u <userid>:<password> --data-urlencode @ssl.xml
 "http://<Device IP>/stw-cgi/security.cgi?msubmenu=ssl&action=install" -H
 "Expect:"

```

The above command will produce a request to the device that looks like below:

```
 POST /stw-cgi/security.cgi?msubmenu=ssl&action=install HTTP/1.1
 Content-Length: 3775
 Content-Type: application/x-www-form-urlencoded

```

TEXT RESPONSE

```
 OK

```

JSON RESPONSE

```
 {
 "Response": "Success"
 }

#### **5.4.4. Add a self-signed certificate**
```

REQUEST

```
 http://<Device IP>/stw cgi/security.cgi?msubmenu=ssl&action=add&CertificateName=certName&Type=SelfS
 igned&CommonName=192.168.75.123&SubjectAlternativeName=domain.com,testdom.co
 m&ExpiryDate=2021-09 09&Country=KR&Province=Gyeonggi&Location=Bundang&Organization=Hanwha&Divisio
 n=RSDT&EmailID=test@hanwha.com

```

TEXT RESPONSE

```
 OK

```

JSON RESPONSE

```
 {
 "Response": "Success"

```

28 Security


```
 }

#### **5.4.5. Use a specific certificate**
```

To delete a certificate with **remove** action, the **CertificateName** parameter must be set at the same time.


REQUEST

```
 http://<Device IP>/stw cgi/security.cgi?msubmenu=ssl&action=remove&CertificateName=certname

#### **5.4.6. Deleting a certificate**
```

To delete a certificate with the **remove** action, the **CertificateName** parameter must be set at the same

time.


REQUEST

```
 http://<Device IP>/stw cgi/security.cgi?msubmenu=ssl&action=remove&CertificateName=certname

```

SUNAPI 29


## **Chapter 6. Guest User Login**
### **6.1. Description**

The **guest** submenu enables or disables guest logins.


**NOTE** This chapter applies to the network cameras only.


**Access level**

|Action|Camera|
|---|---|
|view|Admin|
|set|Admin|


### **6.2. Syntax**

```
 http://<Device IP>/stw-cgi/security.cgi?msubmenu=
 guest &action=<value>[&<parameter>=<value>...]

### **6.3. Parameters**

```










|Action|Parameter|Request/<br>Response|Type/<br>Value|Description|
|---|---|---|---|---|
|view||||Reads the guest user login settings.|
|set|Enable|REQ, RES|<bool><br>True, False|Enables or disables guest logins.<br>**Note**<br>**Enable** must be sent together with<br>the**set** action.|

### **6.4. Examples**

#### **6.4.1. Getting the current guest login setting**

REQUEST




```
 http://<Device IP>/stw-cgi/security.cgi?msubmenu=guest&action=view

```

TEXT RESPONSE

```
 HTTP/1.0 200 OK
 Content-type: text/plain

```

30 Security


```
 <Body>

 Enable=False

```

JSON RESPONSE

```
 HTTP/1.0 200 OK
 Content-type: application/json
 <Body>

 {
 "Enable": false
 }

#### **6.4.2. Enabling guest login**
```

To use the **set** action, the **Enable** parameter must be set at the same time.


REQUEST

```
 http://<Device IP>/stw cgi/security.cgi?msubmenu=guest&action=set&Enable=True

```

SUNAPI 31


## **Chapter 7. User Configuration**
### **7.1. Description**

The **users** submenu adds and deletes system users and sets access permissions.


**Access level**

|Action|Camera|NVR|
|---|---|---|
|view|User|User|
|add, update|Admin|Admin|
|remove|Admin|Admin|
|check|Admin||


### **7.2. Syntax**

```
 http://<Device IP>/stw-cgi/security.cgi?msubmenu=
 users &action=<value>[&<parameter>=<value>...]

### **7.3. Parameters**

```








|Action|Parameter|Request/<br>Response|Type/<br>Value|Description|
|---|---|---|---|---|
|view|UserID|REQ|<string>|User ID<br>‘admin’ cannot be used as the**UserID**<br>value.|
|add, update|Index|REQ, RES|<int>|Index of the registered user account.<br>**Note**<br>**Index**, **UserID**, and**Password**<br>must be sent together for the<br>**update** action.|
||UserID|REQ, RES|<string>|User ID<br>**Note**<br>**UserID** and**Password** must be<br>sent together with the**add** action.|


32 Security


|Action|Parameter|Request/<br>Response|Type/<br>Value|Description|
|---|---|---|---|---|
||UserName|REQ, RES|<string>|User name<br>This parameter is for users only; the<br>admin user name cannot be changed.<br>**NVR ONLY**<br>|
||Enable|REQ, RES|<bool><br>True, False|Whether to activate or deactivate the<br>user account.<br>**CAMERA ONLY**<br>|
||VideoProfileAccess|REQ, RES|<bool><br>True, False|Whether to grant video profile<br>permission.<br>If**VideoProfileAccess** is set to False,<br>only the default profile will be allowed<br>when accessing video. If<br>**VideoProfileAccess** is set to True, all<br>profiles are allowed when accessing<br>video.<br>This parameter can’t be false, if<br>"VideoProfileSettingAccess" is set to<br>true.<br>**CAMERA ONLY**<br>|
||PTZAccess|REQ, RES|<bool><br>True, False|Whether to grant PTZ control<br>permission.<br>For PTZ models,the values for<br>**PTZAccess**, **AlarmOutputAccess**, and<br>**AudioOutAccess** should be the same.<br>**CAMERA ONLY**<br>|
||AudioInAccess|REQ, RES|<bool><br>True, False|Whether to grant audio input control<br>permission.<br>**CAMERA ONLY**<br>|
||AudioOutAccess|REQ, RES|<bool><br>True, False|Whether to grant audio output control<br>permission.<br>For PTZ models, the values for<br>**PTZAccess**, **AlarmOutputAccess**, and<br>**AudioOutAccess** should be the same.<br>**CAMERA ONLY**<br>|



SUNAPI 33


|Action|Parameter|Request/<br>Response|Type/<br>Value|Description|
|---|---|---|---|---|
||AlarmOutputAccess|REQ, RES|<bool><br>True, False|Whether to grant alarm output control<br>permission.<br>For PTZ models, values for**PTZAccess**,<br>**AlarmOutputAccess**, and<br>**AudioOutAccess** should be the same.<br>**CAMERA ONLY**<br>|
||ViewerAccess|REQ, RES|<bool><br>True, False|Whether to grant access permission to<br>a viewer<br>**ViewerAccess** is valid only when<br>UserID is NOT set to Admin.<br>**NVR ONLY**<br>|
||AdminAccess|REQ, RES|<bool><br>True, False|Whether or not to grant admin<br>permission.<br>If this parameter is True, it means that<br>user has full access rights (e.g.<br>administrator).<br>**CAMERA ONLY**<br>|
||PrivacyAreaAccess|REQ, RES|<bool><br>True, False|Whether to grant access pertmission<br>to create/remove privacy areas<br>If this parameter is True, the user can<br>create a new privacy area or configure<br>one. PTZAccess will be enbled<br>automatically when the device<br>supports PTZ.<br>This parameter can’t be false, if<br>"VideoSetupAccess" is set to true.<br>**CAMERA ONLY**<br>|
||Password|REQ, RES|<string>|User password|
||IsPasswordEncrypted|REQ|<bool><br>True, False|When set to true, password is<br>encrypted using the public key<br>provided by the**rsa** submenu of<br>**security**.cgi, and sent as post payload.<br>Refer to the Application<br>Programmer’s Guide.|



34 Security


|Action|Parameter|Request/<br>Response|Type/<br>Value|Description|
|---|---|---|---|---|
||GroupID|REQ, RES|<string>|Group ID<br>**GroupID** is invalid, if**UserLevel** is set<br>to Admin,<br>**NVR ONLY**<br>|
||UserLevel|RES|<enum><br>Guest,<br>Admin,<br>User|User level<br>If**UserLevel** is set to Admin for NVR,<br>**GroupID** is invalid.<br>**NVR ONLY**<br>|
||VideoProfileSettingAcces<br>s|REQ, RES|<bool><br>True,False|It allows user to<br>set/add/update/control/remove<br>below submenus.<br>"videosource","videoprofile","videopr<br>ofilepolicy". And it also allows<br>"VideoProfileAccess".<br>If this parameter is set to true,<br>"VideoProfileAccess" automatically<br>becomes true.|
||ImageSettingAccess|REQ, RES|<bool><br>True,False|It allows user to<br>set/add/update/control/remove<br>below submenus.<br>"camera","presetimageconfig","video<br>source","ssdr","imagepreset2","white<br>balance","imagepresetschedule","ima<br>geenhancements","imageenhanceme<br>nts2","lpcapturesetup","imagecgi-<br>scheduler","irled","overlay","multiima<br>geosd","multilineosd","ptzcontrolcgi-<br>aux"|



SUNAPI 35


|Action|Parameter|Request/<br>Response|Type/<br>Value|Description|
|---|---|---|---|---|
||VideoSetupAccess|REQ, RES|<bool><br>True,False|It allows user to<br>set/add/update/control/remove<br>below submenus.<br>"flip","usbconfig","videooutput","vide<br>oinput","fisheyesetup" And it also<br>allows "PTZAccess",<br>"PrivacyAreaAccess".<br>If this parameter is set to true,<br>"PrivacyAreaAccess", "PTZAccess"<br>automatically becomes true.|
||FocusSetupAccess|REQ, RES|<bool><br>True,False|It allows user to<br>set/add/update/control/remove<br>below submenus.<br>"focuspreset","focus"|
||PlayBackAccess|REQ, RES|<bool><br>True,False|It allows user to<br>set/add/update/control/remove<br>below submenus view action.<br>storageinfo(view),sdcardinfo(view),ov<br>erlapped(view),timeline(view),calenda<br>rsearch(view)|
|remove|Index|REQ|<int>|Index number of the user that is to be<br>removed<br>**Note**<br>Either**Index** or**UserID** must be<br>sent together with the**remove**<br>action.<br>**CAMERA ONLY**<br>|
||UserID|REQ|<string>|User ID that is to be removed<br>**CAMERA ONLY**<br>|
|check|CurrentUserCount|RES|<int>|It shows how many current users are<br>there.**CAMERA ONLY**<br>|
||MaxUserCount|RES|<int>|It indicates maximum user count that<br>can be created.**CAMERA ONLY**<br>|


**Note**

To find out the max users supported by the device, refer to the Attributes/Security/Limit/MaxUser


36 Security


attribute in the device attributes section.

### **7.4. Examples**

#### **7.4.1. Getting current users settings**

REQUEST

```
 http://<Device IP>/stw-cgi/security.cgi?msubmenu=users&action=view

```

TEXT RESPONSE

```
 HTTP/1.0 200 OK
 Content-type: text/plain
 <Body>

 "Users.Index=UserID/Password/Enable/VideoProfileAccess/PTZAccess/AudioInAcce
 ss/AudioOutAccess/AlarmOutputAccess/AdminAccess/PrivacyAreaAccess"
 Users.0=admin//True/True/True/True/True/True/True/True
 Users.1=user1//False/False/False/False/False/False/False/False
 Users.2=user2//False/False/False/False/False/False/False/False
 Users.3=user3//False/False/False/False/False/False/False/False
 Users.4=user4//False/False/False/False/False/False/False/False
 Users.5=user5//False/False/False/False/False/False/False/False
 Users.6=user6//False/False/False/False/False/False/False/False
 Users.7=user7//False/False/False/False/False/False/False/False
 Users.8=user8//False/False/False/False/False/False/False/False
 Users.9=user9//False/False/False/False/False/False/False/False
 Users.10=user10//False/False/False/False/False/False/False/False

```

JSON RESPONSE

```
 HTTP/1.0 200 OK
 Content-type: application/json
 <Body>

 {
 "Users": [
 {
 "Index": 0,
 "UserID": "admin",

```

SUNAPI 37


```
 "Password": "",
 "Enable": true,
 "VideoProfileAccess": true,
 "PTZAccess": true,
 "AudioInAccess": true,
 "AudioOutAccess": true,
 "AlarmOutputAccess": true,
 "AdminAccess": true,
 "PrivacyAreaAccess": true
 },
 {
 "Index": 1,
 "UserID": "user1",
 "Password": "",
 "Enable": false,
 "VideoProfileAccess": false,
 "PTZAccess": false,
 "AudioInAccess": false,
 "AudioOutAccess": false,
 "AlarmOutputAccess": false,
 "AdminAccess": false,
 "PrivacyAreaAccess": false
 },
 {
 "Index": 2,
 "UserID": "user2",
 "Password": "",
 "Enable": false,
 "VideoProfileAccess": false,
 "PTZAccess": false,
 "AudioInAccess": false,
 "AudioOutAccess": false,
 "AlarmOutputAccess": false,
 "AdminAccess": false,
 "PrivacyAreaAccess": false
 },
 {
 "Index": 3,
 "UserID": "user3",
 "Password": "",
 "Enable": false,

```

38 Security


```
 "VideoProfileAccess": false,
 "PTZAccess": false,
 "AudioInAccess": false,
 "AudioOutAccess": false,
 "AlarmOutputAccess": false,
 "AdminAccess": false,
 "PrivacyAreaAccess": false
 },
 {
 "Index": 4,
 "UserID": "user4",
 "Password": "",
 "Enable": false,
 "VideoProfileAccess": false,
 "PTZAccess": false,
 "AudioInAccess": false,
 "AudioOutAccess": false,
 "AlarmOutputAccess": false,
 "AdminAccess": false,
 "PrivacyAreaAccess": false
 },
 {
 "Index": 5,
 "UserID": "user5",
 "Password": "",
 "Enable": false,
 "VideoProfileAccess": false,
 "PTZAccess": false,
 "AudioInAccess": false,
 "AudioOutAccess": false,
 "AlarmOutputAccess": false,
 "AdminAccess": false,
 "PrivacyAreaAccess": false
 },
 {
 "Index": 6,
 "UserID": "user6",
 "Password": "",
 "Enable": false,
 "VideoProfileAccess": false,
 "PTZAccess": false,

```

SUNAPI 39


```
 "AudioInAccess": false,
 "AudioOutAccess": false,
 "AlarmOutputAccess": false,
 "AdminAccess": false,
 "PrivacyAreaAccess": false
 },
 {
 "Index": 7,
 "UserID": "user7",
 "Password": "",
 "Enable": false,
 "VideoProfileAccess": false,
 "PTZAccess": false,
 "AudioInAccess": false,
 "AudioOutAccess": false,
 "AlarmOutputAccess": false,
 "AdminAccess": false,
 "PrivacyAreaAccess": false
 },
 {
 "Index": 8,
 "UserID": "user8",
 "Password": "",
 "Enable": false,
 "VideoProfileAccess": false,
 "PTZAccess": false,
 "AudioInAccess": false,
 "AudioOutAccess": false,
 "AlarmOutputAccess": false,
 "AdminAccess": false,
 "PrivacyAreaAccess": false
 },
 {
 "Index": 9,
 "UserID": "user9",
 "Password": "",
 "Enable": false,
 "VideoProfileAccess": false,
 "PTZAccess": false,
 "AudioInAccess": false,
 "AudioOutAccess": false,

```

40 Security


```
 "AlarmOutputAccess": false,
 "AdminAccess": false,
 "PrivacyAreaAccess": false
 },
 {
 "Index": 10,
 "UserID": "user10",
 "Password": "",
 "Enable": false,
 "VideoProfileAccess": false,
 "PTZAccess": false,
 "AudioInAccess": false,
 "AudioOutAccess": false,
 "AlarmOutputAccess": false,
 "AdminAccess": false,
 "PrivacyAreaAccess": false
 }
 ]
 }

```

The following response example is for NVR only.


TEXT RESPONSE

```
 HTTP/1.0 200 OK
 Content-type: text/plain
 <Body>

 "Users.Index=UserID/UserName/Password/GroupID/UserLevel/ViewerAccess"
 Users.0=admin/admin/7i8o9p0[//Admin/True
 Users.1=tarak/tarak/7i8o9p0[/Group 1/User/True
 Users.2=gopal/gopal/7i8o9p0[/Group 2/User/True

```

JSON RESPONSE

```
 HTTP/1.0 200 OK
 Content-type: application/json
 <Body>

 {

```

SUNAPI 41


```
 "Users": [
 {
 "Index": 0,
 "UserID": "admin",
 "UserName": "admin",
 "Password": "7i8o9p0[",
 "GroupID": "",
 "ViewerAccess": true,
 "UserLevel": "Admin"
 },
 {
 "Index": 1,
 "UserID": "tarak",
 "UserName": "tarak",
 "Password": "7i8o9p0[",
 "GroupID": "Group 1",
 "ViewerAccess": true,
 "UserLevel": "User"
 },
 {
 "Index": 2,
 "UserID": "anumolu",
 "UserName": "anumolu",
 "Password": "7i8o9p0[",
 "GroupID": "Group 2",
 "ViewerAccess": true,
 "UserLevel": "User"
 }
 ]
 }

#### **7.4.2. Getting ‘user1’**
```

REQUEST

```
 http://<Device IP>/stw cgi/security.cgi?msubmenu=users&action=view&UserID=user1

```

TEXT RESPONSE

```
 HTTP/1.0 200 OK
 Content-type: text/plain

```

42 Security


```
 <Body>

 "Users.Index=UserID/Password/Enable/VideoProfileAccess/PTZAccess/AudioInAcce
 ss/AudioOutAccess/AlarmOutputAccess/AdminAccess/PrivacyAreaAccess"
 Users.1=user1//False/False/False/False/False/False/False/False

```

JSON RESPONSE

```
 HTTP/1.0 200 OK
 Content-type: application/json
 <Body>

 {
 "Users": [
 {
 "Index": 1,
 "UserID": "user1",
 "Password": "",
 "Enable": false,
 "VideoProfileAccess": false,
 "PTZAccess": false,
 "AudioInAccess": false,
 "AudioOutAccess": false,
 "AlarmOutputAccess": false,
 "AdminAccess": false,
 "PrivacyAreaAccess": false
 }
 ]
 }

#### **7.4.3. Adding a user**
```

This is an example in which a user is added that has permission to access all video profiles but without PTZ

control.


To add a user, the **UserID** and **Password** parameters must be set together.


REQUEST

```
 http://<Device IP>/stw cgi/security.cgi?msubmenu=users&action=add&UserID=user2&Password=123&VideoPr

```

SUNAPI 43


```
 ofileAccess=True&PTZAccess=False

```

TEXT RESPONSE

```
 HTTP/1.0 200 OK
 Content-type: text/plain
 <Body>

 OK
 Index=1

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

The following example is for NVR only.


REQUEST

```
 http://<Device IP>/stw cgi/security.cgi?msubmenu=users&action=add&UserId=user1&UserName=username1&P
 assword=password1&GroupId=group1&UserLevel=User&ViewerAccess=False

```

TEXT RESPONSE

```
 HTTP/1.0 200 OK
 Content-type: text/plain
 <Body>

 OK

```

44 Security


JSON RESPONSE

```
 HTTP/1.0 200 OK
 Content-type: application/json
 <Body>

 {
 "Response": "Success"
 }

#### **7.4.4. Updating ‘user2’ to give permission for PTZ control**
```

To update user information for the cameras, the **UserID**, **Index**, and **Password** parameters must be sent

together.


REQUEST

```
 http://<Device IP>/stw cgi/security.cgi?msubmenu=users&action=update&UserID=user2&Index=2&Password=
 123&VideoProfileAccess=True&PTZAccess=True

```

The following request example is for NVR only.


REQUEST

```
 http://<Device IP>/stw cgi/security.cgi?msubmenu=users&action=update&UserId=admin&Password=1111aaa

#### **7.4.5. Updating password**
```

When a user (including admin users) wants to change their current password, it’s recommended to use an

encrypted password using the RSA PublicKey retrievable from the **rsa** submenu.


if below attribute is supported, current password verification is supported. Value can be 'Optional' or

'Mandatory', if its optional current password verification is optional, if its mandatory only below JSON

format can be used for changing password.

```
 <attribute name="CurrentPasswordVerification" type="enum" value="Optional"
 accesslevel="suser"/>

```

JSON FORMAT (This should be encrypted using the RSA public key and base64 encoding.)

```
 {

```

SUNAPI 45


```
 "CurrentPassword":"q1w2e3r4t5!!",
 "NewPassword":"qwerty99!!"
 }

```

The post body is sent in the below format,

**Base64(RSAEncrypt(JsonString))**


If above attribute is not supported, only new password can be encypted using the RSA public key,

(example if new password is "qwerty99!!" then only this password needs to be encrypted)


The post body is sent in the below format,

**Base64(RSAEncrypt(newpassword))**


REQUEST

```
 http://192.168.75.196/stw cgi/security.cgi?msubmenu=users&action=update&&UserID=user1&Index=1&IsPasswo
 rdEncrypted=True

```

POST BODY

```
 gH3EsB2O9IfcNY02fQLyOMYA//3ES1nGDT2UUInzN51i0Bw849tuJsdASRWrJt5P+oC1mH05vt2W
 7VqICpTZSK4bg578nonpBbv3uTtsTzMyqDrK71hNsblcISZSDTYLa61IeawC88X1//0UTsIHUtT4
 XKaiEEAyMFXo7E12dj3itf1ySj//Emo7zq321bRqE3ELOxKQnNFJi7DQf92gHcCN3Tr1WosK3vIA
 uZNiOD2txsEIBPxWdS+4RGZNAKzDy62yrJaoIe1lvU3xLA94KH7mGgtsebdXx1X6xay0wTyEtBf8
 /TSt2in/PHKx8ZGJxqTq0eSZDsf40nFXkl5K7w==

```

If an admin is changing the password of a normal user, verifying the current password is not required.

Only the password string can be encrypted using the RSA public key and be sent in the POST body.


**NOTE** Plain text password updates will soon be deprecated.

#### **7.4.6. Deleting ‘user2’**

REQUEST

```
 http://<Device IP>/stw cgi/security.cgi?msubmenu=users&action=remove&UserID=user2

```

**Deleting ‘user2’ via the user’s index number**


Assuming the 'user2' index is '3', user2 can be deleted by using the index number.


46 Security


REQUEST

```
 http://<Device IP>/stw-cgi/security.cgi?msubmenu=users&action=remove&Index=3

#### **7.4.7. Getting current users count & maximum users count**
```

REQUEST

```
 http://<Device IP>/stw-cgi/security.cgi?msubmenu=users&action=check

```

JSON RESPONSE

```
 HTTP/1.0 200 OK
 Content-type: application/json
 <Body>

 {
 "CurrentUserCount": 10,
 "MaxUserCount": 10
 }

```

SUNAPI 47


## **Chapter 8. User Group Configuration**
### **8.1. Description**

The **usergroups** submenu adds and deletes system user groups and sets access permissions for the user

groups.


**NOTE** This chapter applies to NVR only.


**Access level**

|Action|NVR|
|---|---|
|view|User|
|add, update|Admin|
|remove|Admin|


### **8.2. Syntax**

```
 http://<Device IP>/stw-cgi/security.cgi?msubmenu=
 usergroups &action=<value>[&<parameter>=<value>...]

### **8.3. Parameters**

```

















|Action|Parameter|Request/<br>Response|Type/<br>Value|Description|
|---|---|---|---|---|
|view|UserGroupID|REQ|<string>|User group ID|
|add,<br>update|Index|REQ, RES|<int>|User group index<br>**Note**<br>**Index** must be sent for the<br>**update** action.|
||UserGroupID|REQ, RES|<string>|User group ID|
||LiveChannel|REQ, RES|<csv><br>#, None|Live channel<br>• None: Disables all channels|
||SearchChannel|REQ, RES|<csv><br>#, None|Search channel<br>• None: Disables all channels|
||BackupChannel|REQ, RES|<csv><br>#, None|Backup channel<br>• None: Disables all channels|



48 Security


|Action|Parameter|Request/<br>Response|Type/<br>Value|Description|
|---|---|---|---|---|
||PTZAccess|REQ, RES|<bool><br>True, False|Whether to grant permission for<br>PTZ control<br>**PTZAccess** is valid only when<br>**LiveChannel** is enabled.|
||RecordStartAccess|REQ, RES|<bool><br>True, False|Whether to grant access<br>permission to start recording|
||RecordStopAccess|REQ, RES|<bool><br>True, False|Whether to grant access<br>permission to stop recording|
||AlarmOutputAccess|REQ, RES|<bool><br>True, False|Whether to grant permission to<br>access the alarm output|
||ShutdownAccess|REQ, RES|<bool><br>True, False|Whether to grant permission to<br>access shutdown|
||MenuAccess|REQ, RES|<csv><br>System, Device,<br>Record, Event,<br>Network, None|Accessible menu|
||SystemMenuAccess|REQ, RES|<csv><br>DateTimeLanguage,<br>SystemManagement,<br>SystemLog, EventLog,<br>BackupLog, Holiday,<br>None|Accessible system menu|
||DeviceMenuAccess|REQ, RES|<csv><br>CameraRegistration,<br>CameraSetup,<br>LiveSetup,<br>ChannelSetup,<br>DeviceFormat, iSCSI,<br>RAID, HDDAlarm,<br>Monitor, POSConf,<br>POSEventConf, None|Accessible device menu|
||RecordMenuAccess|REQ, RES|<csv><br>RecordingSchedule,<br>NvrRecordSetup,<br>NetCamRecordSetup,<br>RecordOption, None|Accessible record menu|



SUNAPI 49


|Action|Parameter|Request/<br>Response|Type/<br>Value|Description|
|---|---|---|---|---|
||EventMenuAccess|REQ, RES|<csv><br>NvrSensorDetection,<br>NetCamSensorDetecti<br>on,<br>NvrEventDetection,<br>NetCamEventDetectio<br>n,<br>VideoLossDetection,<br>AlarmSchedule,<br>Gsensor, None|Accessible event menu|
||NetworkMenuAccess|REQ, RES|<csv><br>NetworkInterface,<br>NetworkPort, DDNS,<br>IPFilter, SSL, 802.1x,<br>LiveStreaming, SMTP,<br>EventMail,<br>GroupAndRecipientE<br>mail, SNMP,<br>DHCPServer,MTS,<br>None|Accessible network menu|
|remove|Index|REQ|<int>|User group index<br>**Note**<br>Either**Index** or**UserGroupID**<br>must be sent together with<br>the**remove** action.|
||UserGroupID|REQ|<string>|User group ID that is to be<br>removed|

### **8.4. Examples**

#### **8.4.1. Getting current user group settings**

REQUEST

```
 http://<Device IP>/stw-cgi/security.cgi?msubmenu=usergroups&action=view

```

TEXT RESPONSE

```
 HTTP/1.0 200 OK
 Content-type: text/plain
 <Body>

```

50 Security


```
 Index.1.UserGroupID=Group 1
 Index.1.LiveChannel=0,1,2,3,4,5,6,7,8,9,10,11,12,13,14,15,16,17,18,19,20,21,
 22,23,24,25,26,27,28,29,30,31,32,33,34,35,36,37,38,39,40,41,42,43,44,45,46,4
 7,48,49,50,51,52,53,54,55,56,57,58,59,60,61,62,63
 Index.1.SearchChannel=0,1,2,3,4,5,6,7,8,9,10,11,12,13,14,15,16,17,18,19,20,2
 1,22,23,24,25,26,27,28,29,30,31,32,33,34,35,36,37,38,39,40,41,42,43,44,45,46
,47,48,49,50,51,52,53,54,55,56,57,58,59,60,61,62,63
 Index.1.BackupChannel=0,1,2,3,4,5,6,7,8,9,10,11,12,13,14,15,16,17,18,19,20,2
 1,22,23,24,25,26,27,28,29,30,31,32,33,34,35,36,37,38,39,40,41,42,43,44,45,46
,47,48,49,50,51,52,53,54,55,56,57,58,59,60,61,62,63
 Index.1.MenuAccess=System,Device,Record,Event,Network
 Index.1.SystemMenuAccess=DateTimeLanguage,SystemManagement,SystemLog,BackupL
 og,EventLog
 Index.1.DeviceMenuAccess=CameraRegistration,CameraSetup,LiveSetup,ChannelSet
 up,DeviceFormat,HDDAlarm,iSCSI,RAID,Monitor
 Index.1.RecordMenuAccess=RecordingSchedule,NvrRecordSetup,NetCamRecordSetup,
 RecordOption
 Index.1.EventMenuAccess=NvrSensorDetection,NetCamSensorDetection,NvrEventDet
 ection,NetCamEventDetection,VideoLossDetection,AlarmSchedule
 Index.1.NetworkMenuAccess=NetworkInterface,NetworkPort,DDNS,IPFilter,SSL,802
 .1x,LiveStreaming,SMTP,EventMail,GroupAndRecipientEmail,SNMP,DHCPServer
 Index.1.RecordStartAccess=True
 Index.1.RecordStopAccess=True
 Index.1.PTZAccess=True
 Index.1.AlarmOutputAccess=True
 Index.1.ShutdownAccess=True
 Index.2.UserGroupID=Group 2
 Index.2.LiveChannel=None
 Index.2.SearchChannel=None
 Index.2.BackupChannel=None
 Index.2.MenuAccess=None
 Index.2.SystemMenuAccess=None
 Index.2.DeviceMenuAccess=None
 Index.2.RecordMenuAccess=None
 Index.2.EventMenuAccess=None
 Index.2.NetworkMenuAccess=None
 Index.2.RecordStartAccess=False
 Index.2.RecordStopAccess=False
 Index.2.PTZAccess=False
 Index.2.AlarmOutputAccess=False

```

SUNAPI 51


```
 Index.2.ShutdownAccess=False

```

JSON RESPONSE

```
 HTTP/1.0 200 OK
 Content-type: application/json
 <Body>

 {
 "UserGroups": [
 {
 "Index": 1,
 "UserGroupID": "Group 1",
 "LiveChannel": [
 "0", "1", "2", "3", "4", "5", "6", "7", "8", "9",
 "10", "11", "12", "13", "14", "15", "16", "17", "18", "19",
 "20", "21", "22", "23", "24", "25", "26", "27", "28", "29",
 "30", "31", "32", "33", "34", "35", "36", "37", "38", "39",
 "40", "41", "42", "43", "44", "45", "46", "47", "48", "49",
 "50", "51", "52", "53", "54", "55", "56", "57", "58", "59",
 "60", "61", "62", "63"
 ],
 "SearchChannel": [
 "0", "1", "2", "3", "4", "5", "6", "7", "8", "9",
 "10", "11", "12", "13", "14", "15", "16", "17", "18", "19",
 "20", "21", "22", "23", "24", "25", "26", "27", "28", "29",
 "30", "31", "32", "33", "34", "35", "36", "37", "38", "39",
 "40", "41", "42", "43", "44", "45", "46", "47", "48", "49",
 "50", "51", "52", "53", "54", "55", "56", "57", "58", "59",
 "60", "61", "62", "63"
 ],
 "BackupChannel": [
 "0", "1", "2", "3", "4", "5", "6", "7", "8", "9",
 "10", "11", "12", "13", "14", "15", "16", "17", "18", "19",
 "20", "21", "22", "23", "24", "25", "26", "27", "28", "29",
 "30", "31", "32", "33", "34", "35", "36", "37", "38", "39",
 "40", "41", "42", "43", "44", "45", "46", "47", "48", "49",
 "50", "51", "52", "53", "54", "55", "56", "57", "58", "59",
 "60", "61", "62", "63"
 ],
 "MenuAccess": [

```

52 Security


```
 "System",
 "Device",
 "Record",
 "Event",
 "Network"
 ],
 "SystemMenuAccess": [
 "DateTimeLanguage",
 "SystemManagement",
 "SystemLog",
 "BackupLog",
 "EventLog"
 ],
 "DeviceMenuAccess": [
 "CameraRegistration",
 "CameraSetup",
 "LiveSetup",
 "ChannelSetup",
 "DeviceFormat",
 "HDDAlarm",
 "iSCSI",
 "RAID",
 "Monitor"
 ],
 "RecordMenuAccess": [
 "RecordingSchedule",
 "NvrRecordSetup",
 "NetCamRecordSetup",
 "RecordOption"
 ],
 "EventMenuAccess": [
 "NvrSensorDetection",
 "NetCamSensorDetection",
 "NvrEventDetection",
 "NetCamEventDetection",
 "VideoLossDetection",
 "AlarmSchedule"
 ],
 "NetworkMenuAccess": [
 "NetworkInterface",
 "NetworkPort",

```

SUNAPI 53


```
 "DDNS",
 "IPFilter",
 "SSL",
 "802.1x",
 "LiveStreaming",
 "SMTP",
 "EventMail",
 "GroupAndRecipientEmail",
 "SNMP",
 "DHCPServer"
 ],
 "RecordStartAccess": true,
 "RecordStopAccess": true,
 "PTZAccess": true,
 "AlarmOutputAccess": true,
 "ShutdownAccess": true
 },
 {
 "Index": 2,
 "UserGroupID": "Group 2",
 "LiveChannel": [
 "None"
 ],
 "SearchChannel": [
 "None"
 ],
 "BackupChannel": [
 "None"
 ],
 "MenuAccess": [
 "None"
 ],
 "SystemMenuAccess": [
 "None"
 ],
 "DeviceMenuAccess": [
 "None"
 ],
 "RecordMenuAccess": [
 "None"
 ],

```

54 Security


```
 "EventMenuAccess": [
 "None"
 ],
 "NetworkMenuAccess": [
 "None"
 ],
 "RecordStartAccess": false,
 "RecordStopAccess": false,
 "PTZAccess": false,
 "AlarmOutputAccess": false,
 "ShutdownAccess": false
 }
 ]
 }

#### **8.4.2. Getting ‘Group 1’ user group settings**
```

REQUEST

```
 http://<Device IP>/stw cgi/security.cgi?msubmenu=usergroups&action=view&UserGroupID=Group 1

```

TEXT RESPONSE

```
 HTTP/1.0 200 OK
 Content-type: text/plain
 <Body>

 Index.1.UserGroupID=Group 1
 Index.1.LiveChannel=0,1,2,3,4,5,6,7,8,9,10,11,12,13,14,15,16,17,18,19,20,21,
 22,23,24,25,26,27,28,29,30,31,32,33,34,35,36,37,38,39,40,41,42,43,44,45,46,4
 7,48,49,50,51,52,53,54,55,56,57,58,59,60,61,62,63
 Index.1.SearchChannel=0,1,2,3,4,5,6,7,8,9,10,11,12,13,14,15,16,17,18,19,20,2
 1,22,23,24,25,26,27,28,29,30,31,32,33,34,35,36,37,38,39,40,41,42,43,44,45,46
,47,48,49,50,51,52,53,54,55,56,57,58,59,60,61,62,63
 Index.1.BackupChannel=0,1,2,3,4,5,6,7,8,9,10,11,12,13,14,15,16,17,18,19,20,2
 1,22,23,24,25,26,27,28,29,30,31,32,33,34,35,36,37,38,39,40,41,42,43,44,45,46
,47,48,49,50,51,52,53,54,55,56,57,58,59,60,61,62,63
 Index.1.MenuAccess=System,Device,Record,Event,Network
 Index.1.SystemMenuAccess=DateTimeLanguage,SystemManagement,SystemLog,BackupL
 og,EventLog

```

SUNAPI 55


```
 Index.1.DeviceMenuAccess=CameraRegistration,CameraSetup,LiveSetup,ChannelSet
 up,DeviceFormat,HDDAlarm,iSCSI,RAID,Monitor
 Index.1.RecordMenuAccess=RecordingSchedule,NvrRecordSetup,NetCamRecordSetup,
 RecordOption
 Index.1.EventMenuAccess=NvrSensorDetection,NetCamSensorDetection,NvrEventDet
 ection,NetCamEventDetection,VideoLossDetection,AlarmSchedule
 Index.1.NetworkMenuAccess=NetworkInterface,NetworkPort,DDNS,IPFilter,SSL,802
 .1x,LiveStreaming,SMTP,EventMail,GroupAndRecipientEmail,SNMP,DHCPServer
 Index.1.RecordStartAccess=True
 Index.1.RecordStopAccess=True
 Index.1.PTZAccess=True
 Index.1.AlarmOutputAccess=True
 Index.1.ShutdownAccess=True

```

JSON RESPONSE

```
 HTTP/1.0 200 OK
 Content-type: application/json
 <Body>

 {
 "UserGroups": [
 {
 "Index": 1,
 "UserGroupID": "Group 1",
 "LiveChannel": [
 "0", "1", "2", "3", "4", "5", "6", "7", "8", "9", "10",
 "11", "12",
 "13", "14", "15", "16", "17", "18", "19", "20", "21", "22",
 "23",
 "24", "25", "26", "27", "28", "29", "30", "31", "32", "33",
 "34",
 "35", "36", "37", "38", "39", "40", "41", "42", "43", "44",
 "45",
 "46", "47","48", "49", "50", "51", "52", "53", "54", "55",
 "56",
 "57", "58", "59", "60", "61", "62", "63"
 ],
 "SearchChannel": [
 "0", "1", "2", "3", "4", "5", "6", "7", "8", "9", "10",
 "11", "12",

```

56 Security


```
 "13", "14", "15", "16", "17", "18", "19", "20", "21", "22",
 "23",
 "24", "25", "26", "27", "28", "29", "30", "31", "32", "33",
 "34",
 "35", "36", "37", "38", "39", "40", "41", "42", "43", "44",
 "45",
 "46", "47","48", "49", "50", "51", "52", "53", "54", "55",
 "56",
 "57", "58", "59", "60", "61", "62", "63"
 ],
 "BackupChannel": [
 "0", "1", "2", "3", "4", "5", "6", "7", "8", "9", "10",
 "11", "12",
 "13", "14", "15", "16", "17", "18", "19", "20", "21", "22",
 "23",
 "24", "25", "26", "27", "28", "29", "30", "31", "32", "33",
 "34",
 "35", "36", "37", "38", "39", "40", "41", "42", "43", "44",
 "45",
 "46", "47","48", "49", "50", "51", "52", "53", "54", "55",
 "56",
 "57", "58", "59", "60", "61", "62", "63"
 ],
 "MenuAccess": [
 "System",
 "Device",
 "Record",
 "Event",
 "Network"
 ],
 "SystemMenuAccess": [
 "DateTimeLanguage",
 "SystemManagement",
 "SystemLog",
 "BackupLog",
 "EventLog"
 ],
 "DeviceMenuAccess": [
 "CameraRegistration",
 "CameraSetup",
 "LiveSetup",

```

SUNAPI 57


```
 "ChannelSetup",
 "DeviceFormat",
 "HDDAlarm",
 "iSCSI",
 "RAID",
 "Monitor"
 ],
 "RecordMenuAccess": [
 "RecordingSchedule",
 "NvrRecordSetup",
 "NetCamRecordSetup",
 "RecordOption"
 ],
 "EventMenuAccess": [
 "NvrSensorDetection",
 "NetCamSensorDetection",
 "NvrEventDetection",
 "NetCamEventDetection",
 "VideoLossDetection",
 "AlarmSchedule"
 ],
 "NetworkMenuAccess": [
 "NetworkInterface",
 "NetworkPort",
 "DDNS",
 "IPFilter",
 "SSL",
 "802.1x",
 "LiveStreaming",
 "SMTP",
 "EventMail",
 "GroupAndRecipientEmail",
 "SNMP",
 "DHCPServer"
 ],
 "RecordStartAccess": true,
 "RecordStopAccess": true,
 "PTZAccess": true,
 "AlarmOutputAccess": true,
 "ShutdownAccess": true
 }

```

58 Security


```
 ]
 }

#### **8.4.3. Adding a user group**
```

REQUEST

```
 http://<Device IP>/stw cgi/security.cgi?msubmenu=usergroups&action=add&UserGroupID=Group3&LiveChann
 el=1,11,21&SearchChannel=2,12,22&BackupChannel=3,13,33

#### **8.4.4. Updating a user group**
```

REQUEST

```
 http://<Device IP>/stw cgi/security.cgi?msubmenu=usergroups&action=update&UserGroupID=Group3&Backup
 Channel=13,21,3

#### **8.4.5. Removing a user group**
```

A user group can be deleted with the index number or the user group ID.


REQUEST

```
 http://<Device IP>/ stw cgi/security.cgi?msubmenu=usergroups&action=remove&Index=3

```

REQUEST

```
 http://<Device IP>/stw cgi/security.cgi?msubmenu=usergroups&action=remove&UserGroupID=Group3

```

SUNAPI 59


## **Chapter 9. Authority**
### **9.1. Description**

The **authority** submenu sets the access permissions.


**NOTE** This chapter applies to NVR only.


**Access level**

|Action|NVR|
|---|---|
|view|User|
|set|Admin|


### **9.2. Syntax**

```
 http://<Device IP>/stw-cgi/security.cgi?msubmenu=
 authority &action=<value>[&<parameter>=<value>...]

### **9.3. Parameters**

```













|Action|Parameter|Request/<br>Response|Type/<br>Value|Description|
|---|---|---|---|---|
|view||||Reads the authority settings|
|set|LiveAccess|REQ, RES|<bool><br>True, False|Whether to grant permission for live<br>access|
||PTZAccess|REQ, RES|<bool><br>True, False|Whether to grant permission for PTZ<br>control|
||RemoteAlarmOutput|REQ, RES|<bool><br>True, False|Whether to grant permission for<br>remote alarm output control|
||ShutDown|REQ, RES|<bool><br>True, False|Whether to grant permission to shut<br>down|
||RecordStartAccess|REQ, RES|<bool><br>True, False|Whether to grant permission for<br>record start control|
||RecordStopAccess|REQ, RES|<bool><br>True, False|Whether to grant permission for<br>record stop control|
||SearchAccess|REQ, RES|<bool><br>True, False|Whether to grant permission for<br>search control|
||BackupAccess|REQ, RES|<bool><br>True, False|Whether to grant permission for<br>backup access|



60 Security


|Action|Parameter|Request/<br>Response|Type/<br>Value|Description|
|---|---|---|---|---|
||NetworkAccess|REQ, RES|<bool><br>True, False|Whether to grant permission for<br>network access|
||WebviewerAccess|REQ, RES|<bool><br>True, False|Whether to grant permission for Web<br>viewer access|
||AutoLogoutTime|REQ, RES|<enum><br>Off, 1m,<br>2m, 3m,<br>5m, 10m|Auto logout time|
||IDManualInput|REQ, RES|<bool><br>True, False|Whether to grant permission to<br>manually input the ID|

### **9.4. Examples**

#### **9.4.1. Getting current permission settings**

REQUEST




```
 http://<Device IP>/stw-cgi/security.cgi?msubmenu=authority&action=view

```

TEXT RESPONSE

```
 HTTP/1.0 200 OK
 Content-type: text/plain
 <Body>

 LiveAccess=True
 PTZAccess=False
 RemoteAlarmOutput=False
 ShutDown=False
 RecordStopAccess=False
 SearchAccess=False
 BackupAccess=False
 RecordStartAccess=False
 NetworkAccess=True
 WebviewerAccess=True
 IDManualInput=False
 AutoLogoutTime=OFF

```

SUNAPI 61


JSON RESPONSE

```
 HTTP/1.0 200 OK
 Content-type: application/json
 <Body>

 {
 "LiveAccess": true,
 "PTZAccess": false,
 "RemoteAlarmOutput": false,
 "ShutDown": false,
 "RecordStopAccess": false,
 "SearchAccess": false,
 "BackupAccess": false,
 "RecordStartAccess": false,
 "NetworkAccess": true,
 "WebviewerAccess": true,
 "IDManualInput": false,
 "AutoLogoutTime": "OFF"
 }

#### **9.4.2. Setting the access permission**
```

REQUEST

```
 http://<Device IP>/stw cgi/security.cgi?msubmenu=authority&action=set&LiveAccess=False&PTZAccess=Fa
 lse&RemoteAlarmOutput=False&ShutDown=False&RecordStopAccess=False&SearchAcce
 ss=False&BackupAccess=false

```

62 Security


## **Chapter 10. Additional Password**
### **10.1. Description**

The **additionalpassword** submenu sets multiple passwords for the user.


**NOTE** This chapter applies to NVR only.


**Access level**

|Action|NVR|
|---|---|
|view|User|
|add, update|Admin|
|remove|Admin|


### **10.2. Syntax**

```
 http://<Device IP>/stw-cgi/security.cgi?msubmenu=
 additionalpassword &action=<value>[&<parameter>=<value>...]

### **10.3. Parameters**

```




















|Action|Parameter|Request/<br>Response|Type/<br>Value|Description|
|---|---|---|---|---|
|view|UserID|REQ|<string>|User ID|
|add/update|UserID|REQ, RES|<string>|User ID|
||Enable|REQ, RES|<bool><br>True, False|• To enable a multi password rule|
||PasswordIndex|REQ, RES|<int>|• Index for password|
||Password|REQ, RES|<string>|• Additional password|
||IsPasswordEncrypted|REQ|<bool><br>True, False|• If set to true, Password is<br>encrypted using the public key<br>provided by the**rsa** submenu of<br>**security**.cgi, and sent as post<br>payload. Refer to the Application<br>Programmer’s Guide.|
|remove|UserID|REQ|<string>|User ID|


SUNAPI 63


|Action|Parameter|Request/<br>Response|Type/<br>Value|Description|
|---|---|---|---|---|
||PasswordIndex|REQ|<csv>|Password Index that is to be removed<br>**Note**<br>All passwords will be removed for<br>the corresponding user if<br>PasswordIndex is not provided.|

### **10.4. Examples**

#### **10.4.1. Getting additional password settings for all users**

REQUEST

```
 http://<Device IP>/stw cgi/security.cgi?msubmenu=additionalpassword&action=view

```

TEXT RESPONSE

```
 HTTP/1.0 200 OK
 Content-type: text/plain
 <Body>

 UserID.User1.GroupID=Group1
 UserID.User1.Enable=True
 UserID.User2.GroupID=Group2
 UserID.User2.Enable=False
 UserID.User3.GroupID=Group2
 UserID.User3.Enable=True

```

JSON RESPONSE

```
 HTTP/1.0 200 OK
 Content-type: application/json
 <Body>

 {
 "AdditionalPasswords": [
 {
 "UserID": "User1",

```

64 Security


```
 "GroupID": "Group1",
 "Enable": true
 },
 {
 "UserID": "User2",
 "GroupID": "Group2",
 "Enable": false
 },
 {
 "UserID": "User3",
 "GroupID": "Group2",
 "Enable": true
 }
 ]
 }

#### **10.4.2. Getting additional password settings for user "User1"**
```

REQUEST

```
 http://<Device IP>/stw cgi/security.cgi?msubmenu=additionalpassword&action=view&UserID=User1

```

TEXT RESPONSE

```
 HTTP/1.0 200 OK
 Content-type: text/plain
 <Body>

 UserID.User1.GroupID=Group1
 UserID.User1.Enable=True

```

JSON RESPONSE

```
 HTTP/1.0 200 OK
 Content-type: application/json
 <Body>

 {
 "AdditionalPasswords": [

```

SUNAPI 65


```
 {
 "UserID": "User1",
 "GroupID": "Group1",
 "Enable": true
 }
 ]
 }

#### **10.4.3. Adding a Password for a User**
```

REQUEST

```
 http://<Device IP>/stw-cgi/security.cgi?
 msubmenu=additionalpassword&action=add&UserID=User1&Password=12345678

#### **10.4.4. Updating Password**
```

REQUEST

```
 http://<Device IP/stw cgi/security.cgi?msubmenu=additionalpassword&action=update&UserID=User1&Pass
 wordindex=1&Password=q1w2e3r4t5!

#### **10.4.5. Removing all Passwords for a User**
```

REQUEST

```
 http://<Device IP>/stw cgi/security.cgi?msubmenu=additionalpassword&action=remove&UserID=User1

#### **10.4.6. Removing Password Index 1,2,3**
```

REQUEST

```
 http://<Device IP>/stw cgi/security.cgi?msubmenu=additionalpassword&action=remove&UserID=User1&Pass
 wordIndex=1,2,3

```

66 Security


## **Chapter 11. Getting public key**
### **11.1. Description**

The **rsa** submenu is used to get the public key from the device. This can be used to encrypt the password

information sent to the device.


**NOTE** This chapter applies to network cameras only.


**Access level**







|Action|Camer<br>a|NVR|AMS|
|---|---|---|---|
|view|Admin|Admin|Admin|

### **11.2. Syntax**

```
 http://<Device IP>/stw-cgi/security.cgi?msubmenu=
 rsa &action=<value>[&<parameter>=<value>...]

### **11.3. Parameters**

```










|Action|Parameter|Request/<br>Response|Type/<br>Value|Description|
|---|---|---|---|---|
|view|PublicKeyFormat|REQ|<enum><br>PKCS1,<br>X509|Optional request parameter to specify<br>the RSA public key format. If not<br>specified, the PKCS1 format is served.<br>**CAMERA ONLY**<br>|
||PublicKey|RES|<string>|RSA public key|

### **11.4. Examples**

Please refer to the application programming guide for information on how to use this
**NOTE**

public key to encrypt passwords.


REQUEST

```
 http://<Device IP>/stw-cgi/security.cgi?msubmenu=rsa&action=view

```

TEXT RESPONSE

```
 HTTP/1.0 200 OK

```

SUNAPI 67


```
 Content-type: text/plain
 <Body>

 PublicKey=-----BEGIN RSA PUBLIC KEY---- MIIBCgKCAQEAugtcj1ql+mvkzK60Hph3an0Z/rdtZ/NF84m0TAsQuiDheGnN7dYJ
 nZfRit5PcdugQO7XAkVq9DBy6kWrgrMqlzS9PwwEN7cBgFmyU/yJvpnZNrxlDLFB
 ELlXgEYVih5yTSSoa6uWy8cSnGrnY1Ywymh8JGvuk0xZFc09eBCnIogQqydQb1AP
 OnUqTx5JaCdnitYekHRWdyh1XY3wJnV6Ykb8hfnwzhrbz4P2bOCTW/ISE5hl2qvP
 WrSBk+EEH2Wfcwfu2785iyu6mDzoCT64XcyOgscLkLhkg2IAXhoel+TNDdN0zzOX
 dIpDg2Vi4s3ObPG4KSLnStXJJYIDx3CrRwIDAQAB
 -----END RSA PUBLIC KEY----
```

JSON RESPONSE

```
 HTTP/1.0 200 OK
 Content-type: application/json
 <Body>

 {
 "PublicKey": "-----BEGIN RSA PUBLIC KEY---- \nMIIBCgKCAQEAugtcj1ql+mvkzK60Hph3an0Z/rdtZ/NF84m0TAsQuiDheGnN7dYJ\nnZfRit5P
 cdugQO7XAkVq9DBy6kWrgrMqlzS9PwwEN7cBgFmyU/yJvpnZNrxlDLFB\nELlXgEYVih5yTSSoa6
 uWy8cSnGrnY1Ywymh8JGvuk0xZFc09eBCnIogQqydQb1AP\nOnUqTx5JaCdnitYekHRWdyh1XY3w
 JnV6Ykb8hfnwzhrbz4P2bOCTW/ISE5hl2qvP\nWrSBk+EEH2Wfcwfu2785iyu6mDzoCT64XcyOgs
 cLkLhkg2IAXhoel+TNDdN0zzOX\ndIpDg2Vi4s3ObPG4KSLnStXJJYIDx3CrRwIDAQAB\n---- END RSA PUBLIC KEY-----\n"
 }

```

Example of when key format is specified.


REQUEST

```
 http://<Device IP>/stw cgi/security.cgi?msubmenu=rsa&action=view&PublicKeyFormat=X509

```

TEXT RESPONSE

```
 HTTP/1.0 200 OK
 Content-type: text/plain

```

68 Security


```
 <Body>

 PublicKey=-----BEGIN PUBLIC KEY---- MIIBIjANBgkqhkiG9w0BAQEFAAOCAQ8AMIIBCgKCAQEAxp5XPQay2FVUJZXCV2K2
 7Wv7uLtZ3vIwsSiAHVJZwSmAQV7H23ElmBCNEWCk96mdjonZnHpQ0mWj3hsDkO48
 qGnELbsrqfTuUF5Ulze7+f34aX/Mg9pwbOruZE3CRbcsxc2JTTbm0sLoVnSV7pPn
 Lg/r4dzp7ll3fL4WfKere/sXmRdeZ+2ugVzrCGSovOX4madkAtwCEszOZedIWe85
 AkDN42Aw11sknn66EkDZAMVrpI5g0nfrdUYTKxh/e+LAVOfMSHdFaMht4rSTaXN7
 z+RxPh5Ro0UN5Ha9buNtiXUB4VkjV440/Be13njHt+d5HZduGh0WhggIjgyTJGsN
 7wIDAQAB
 -----END PUBLIC KEY----
```

JSON RESPONSE

```
 HTTP/1.0 200 OK
 Content-type: application/json
 <Body>

 {
 "PublicKey": "-----BEGIN PUBLIC KEY---- \nMIIBIjANBgkqhkiG9w0BAQEFAAOCAQ8AMIIBCgKCAQEAxp5XPQay2FVUJZXCV2K2\n7Wv7uLtZ
 3vIwsSiAHVJZwSmAQV7H23ElmBCNEWCk96mdjonZnHpQ0mWj3hsDkO48\nqGnELbsrqfTuUF5Ulz
 e7+f34aX/Mg9pwbOruZE3CRbcsxc2JTTbm0sLoVnSV7pPn\nLg/r4dzp7ll3fL4WfKere/sXmRde
 Z+2ugVzrCGSovOX4madkAtwCEszOZedIWe85\nAkDN42Aw11sknn66EkDZAMVrpI5g0nfrdUYTKx
 h/e+LAVOfMSHdFaMht4rSTaXN7\nz+RxPh5Ro0UN5Ha9buNtiXUB4VkjV440/Be13njHt+d5HZdu
 Gh0WhggIjgyTJGsN\n7wIDAQAB\n-----END PUBLIC KEY-----\n"
 }

```

SUNAPI 69


## **Chapter 12. Configure default camera user** **credentials in NVR**
### **12.1. Description**

The **camerausers** submenu is used to configure camera’s default set of username and password in NVR.

If NVR discovers some cameras or does connection test, it automatically tries to connect with camera with

these configured user credentials.


**NOTE** This chapter applies to NVR only.


**Access level**

|Action|NVR|
|---|---|
|view|User|
|add/update|Admin|
|remove|Admin|


### **12.2. Syntax**

```
 http://<Device IP>/stw-cgi/security.cgi?msubmenu=
 camerausers &action=<value>[&<parameter>=<value>...]

### **12.3. Parameters**

```















|Action|Parameter|Request/<br>Response|Type/<br>Value|Description|
|---|---|---|---|---|
|view|UserID|REQ|<string>||
||IsInitPasswordSet|RES|<bool><br>True, False|Initial password status whether it is<br>set or not|
|add/update|Index|REQ, RES|<int>|Index to be added|
||UserID|REQ, RES|<string>|ID to try connecting with its camera|
||Password|REQ, RES|<string>|Password to try connecting with its<br>camera|
||IsPasswordEncrypted|REQ|<bool><br>True, False|When this is set to true, password is<br>encrypted using the public key<br>obtained from the**rsa** submenu of<br>security.cgi, and sent as payload<br>content for the POST command.|



70 Security


|Action|Parameter|Request/<br>Response|Type/<br>Value|Description|
|---|---|---|---|---|
|set|InitPassword|REQ|<string>|Initializes camera with this password|
||IsPasswordEncrypted|REQ|<bool><br>True, False|When this is set to True, InitPassword<br>parameter is not sent and instead the<br>password is encrypted using the<br>public key obtained from the**rsa**<br>submenu of security.cgi, and sent as<br>payload content for the POST<br>command.|
|remove|Index|REQ|<int>|Index to be removed|

### **12.4. Examples**

#### **12.4.1. Viewing a user**

REQUEST

```
 http://<Device IP>/stw-cgi/security.cgi?msubmenu=camerausers&action=view

```

JSON RESPONSE

```
 HTTP/1.0 200 OK
 Content-type: application/json
 <Body>

 {
 "Users": [
 {
 "Index": 0,
 "UserID": "admin"
 },
 {
 "Index": 1,
 "UserID": "admin"
 },
 {
 "Index": 2,
 "UserID": "root"
 }
 ]

```

SUNAPI 71


```
 }

```

Please refer to the application programming guide for information on how to use this
**NOTE**

public key to encrypt passwords.

#### **12.4.2. Adding a user**

REQUEST

```
 http://<Device IP>/stw cgi/security.cgi?msubmenu=camerausers&action=add&UserId=admin&password=12345
 678&IsPasswordEncrypted=false

#### **12.4.3. Updating a user**
```

REQUEST

```
 http://<Device IP>/stw cgi/security.cgi?msubmenu=camerausers&action=update&Index=0&UserId=admin&pas
 sword=12345678&IsPasswordEncrypted=False

#### **12.4.4. Removing a user**
```

REQUEST

```
 http://<Device IP>/stw cgi/security.cgi?msubmenu=camerausers&action=remove&Index=1

```

72 Security


## **Chapter 13. Getting Client Mutual Authenticate** **Status**
### **13.1. Description**

The **clienthttpsstatus** submenu is used to get the client’s mutual authentication status from the device.


This chapter applies to network cameras only.



**NOTE**


**Access level**



Attribute that checks for the client certificate authentication supports:

"attributes/Security/Support/ClientCertificateAuthentication"



|Action|Camera|
|---|---|
|view|User|

### **13.2. Syntax**

```
 http://<Device IP>/stw-cgi/security.cgi?msubmenu=
 clienthttpsstatus &action=<value>[&<parameter>=<value>...]

### **13.3. Parameters**

```








|Action|Parameter|Request/<br>Response|Type/<br>Value|Description|
|---|---|---|---|---|
|view||||Read client’s mutual certificate<br>status|


SUNAPI 73


|Action|Parameter|Request/<br>Response|Type/<br>Value|Description|
|---|---|---|---|---|
||ClientHttpsStatus|RES|<enum><br>NO_HTTPS,<br>HTTPS_WITHOUT_CLIE<br>NT_CERT,<br>HTTPS_WITH_INVALID<br>_CLIENT_CERT,<br>HTTPS_WITH_VALID_C<br>LIENT_CERT|Current client’s HTTPS connection<br>status<br>• NO_HTTPS: The client uses no<br>HTTPS<br>• HTTPS_WITHOUT_CLIENT_CER<br>T: The client uses HTTPS, but<br>the device does not use<br>mutual authentication<br>• HTTPS_WITH_INVALID_CLIENT<br>_CERT: The device has mutual<br>authentication enabled, but<br>the client’s certificate is invalid<br>• HTTPS_WITH_VALID_CLIENT_C<br>ERT: The device has mutual<br>authentication enabled and<br>the client’s certificate is valid|

### **13.4. Examples**

REQUEST

```
 http://<Device IP>/stw
```



```
 cgi/security.cgi?msubmenu=clienthttpsstatus&action=view

```

TEXT RESPONSE

```
 HTTP/1.0 200 OK
 Content-type: text/plain
 <Body>

```

ClientHttpsStatus=NO_HTTPS


JSON RESPONSE

```
 HTTP/1.0 200 OK
 Content-type: application/json
 <Body>

```

{


74 Security


"ClientHttpsStatus": "NO_HTTPS"


}


SUNAPI 75


## **Chapter 14. Getting TLS Configuration**
### **14.1. Description**

The **tlsversion** submenu is used to get the TLS configuration from the device.


**NOTE** This chapter applies to network cameras only.


**Access level**

|Action|Camera|
|---|---|
|view|Admin|
|set|Admin|


### **14.2. Syntax**

```
 http://<Device IP>/stw-cgi/security.cgi?msubmenu=
 tlsversion &action=<value>[&<parameter>=<value>...]

### **14.3. Parameters**

```



















|Action|Parameter|Request/<br>Response|Type/<br>Value|Description|
|---|---|---|---|---|
|view||||Reads TLS configuration.|
||Version|REQ|<csv><br>TLSv1_0,<br>TLSv1_1,<br>TLSv1_2,<br>TLSv1_3|TLS Version<br>Getting the configuration of specific<br>TLS version|
||Version.#.SupportedCiph<br>erMode|RES|<csv><br>Compatible,<br>Secure|Supported cipher mode<br>• Compatible: Supports a<br>compatible cipher suite<br>• Secure: Supports a secure cipher<br>suite|
|set|Version.#.Enable|REQ, RES|<bool><br>True, False|Enables or disables TLS version<br>If a specific TLS version to be enabled<br>does not support Secure mode,<br>**CipherMode** will automatically<br>change to Compatible mode|



76 Security


|Action|Parameter|Request/<br>Response|Type/<br>Value|Description|
|---|---|---|---|---|
||CipherMode|REQ, RES|<enum><br>Compatible,<br>Secure|Cipher mode<br>• Compatible: Device uses a<br>compatible cipher suite<br>• Secure: Device uses a more secure<br>cipher suite<br>To use a specific mode, all versions<br>must support the mode.|

### **14.4. Examples**




#### **14.4.1. Getting all versions of the TLS configurations**

REQUEST

```
 http://<Device IP>/stw-cgi/security.cgi?msubmenu=tlsversion&action=view

```

TEXT RESPONSE

```
 HTTP/1.0 200 OK
 Content-type: text/plain
 <Body>

 Version.TLSv1_0.Enable=False
 Version.TLSv1_0.SupportedCipherModes=Compatible
 Version.TLSv1_1.Enable=False
 Version.TLSv1_1.SupportedCipherModes=Compatible
 Version.TLSv1_2.Enable=True
 Version.TLSv1_2.SupportedCipherModes=Compatible,Secure
 Version.TLSv1_3.Enable=True
 Version.TLSv1_3.SupportedCipherModes=Compatible,Secure
 CipherMode=Secure

```

JSON RESPONSE

```
 HTTP/1.0 200 OK
 Content-type: application/json
 <Body>

```

SUNAPI 77


```
 {
 "Versions": [
 {
 "Version": "TLSv1_0",
 "Enable": false,
 "SupportedCipherModes": [
 "Compatible"
 ]
 },
 {
 "Version": "TLSv1_1",
 "Enable": false,
 "SupportedCipherModes": [
 "Compatible"
 ]
 },
 {
 "Version": "TLSv1_2",
 "Enable": true,
 "SupportedCipherModes": [
 "Compatible",
 "Secure"
 ]
 },
 {
 "Version": "TLSv1_3",
 "Enable": true,
 "SupportedCipherModes": [
 "Compatible",
 "Secure"
 ]
 }
 ],
 "CipherMode": "Secure"
 }

#### **14.4.2. Getting ‘TLSv1_3’ configuration**
```

REQUEST

```
 http://<Device IP>/stw
```

78 Security


```
 cgi/security.cgi?msubmenu=tlsversion&action=view&Version=TLSv1_3

```

TEXT RESPONSE

```
 HTTP/1.0 200 OK
 Content-type: text/plain
 <Body>

 Version.TLSv1_3.Enable=True
 Version.TLSv1_3.SupportedCipherModes=Compatible,Secure
 CipherMode=Secure

```

JSON RESPONSE

```
 HTTP/1.0 200 OK
 Content-type: application/json
 <Body>

 {
 "Versions": [
 {
 "Version": "TLSv1_3",
 "Enable": true,
 "SupportedCipherModes": [
 "Compatible",
 "Secure"
 ]
 }
 ],
 "CipherMode": "Secure"
 }

#### **14.4.3. Enabling TLS v1.2 and v1.3**
```

REQUEST

```
 http://<Device IP>/stw cgi/security.cgi?msubmenu=tlsversion&action=set&Version.TLSv1_2.Enable=True&
 Version.TLSv1_3.Enable=True

```

SUNAPI 79


#### **14.4.4. Setting cipher mode to compatible mode**

REQUEST

```
 http://<Device IP>/stw cgi/security.cgi?msubmenu=tlsversion&action=set&CipherMode=Compatible

```

80 Security


## **Chapter 15. Getting Camera’s validation status** **from NVR**
### **15.1. Description**

The **cameravalidationstatus** submenu is used to get the camera’s validation status from NVR.


**NOTE** This chapter applies to NVR only.


**Access level**

|Action|NVR|
|---|---|
|view|User|


### **15.2. Syntax**

```
 http://<Device IP>/stw-cgi/security.cgi?msubmenu=
 cameravalidationstatus &action=<value>[&<parameter>=<value>...]

### **15.3. Parameters**

```












|Action|Parameter|Request/<br>Response|Type/<br>Value|Description|
|---|---|---|---|---|
|view||||Reads camera validation status|
||Channel.#.Connected|RES|<bool><br>True, False|Camera connection status|
||Channel.#.CameraVali<br>dationStatus|RES|<enum><br>UNKNOWN, HTTP,<br>OTHER_CERT,<br>CHANGED_CERT,<br>INVALID_DEVICE_CERT<br>, VALID_DEVICE_CERT|Current channels connection<br>status<br>**Note**<br>Valid status is only supported<br>for cameras connected using<br>SUNAPI in NVR|

### **15.4. Examples**

REQUEST

```
 http://<Device IP>/stw
```





```
 cgi/security.cgi?msubmenu=cameravalidationstatus&action=view

```

SUNAPI 81


TEXT RESPONSE

```
 HTTP/1.0 200 OK
 Content-type: text/plain
 <Body>

 Channel.0.Connected=True
 Channel.0.CameraValidationStatus=HTTP
 Channel.1.Connected=True
 Channel.1.CameraValidationStatus=HTTP
 Channel.2.Connected=True
 Channel.2.CameraValidationStatus=HTTP
 ....
 Channel.3.Connected=False

```

JSON RESPONSE

```
 HTTP/1.0 200 OK
 Content-type: application/json
 <Body>

 {
 "cameravalidationstatus": [
 {
 "Channel": 0,
 "Connected": true,
 "CameraValidationStatus": "HTTP"
 },
 {
 "Channel": 1,
 "Connected": true,
 "CameraValidationStatus": "HTTP"
 },
 {
 "Channel": 2,
 "Connected": true,
 "CameraValidationStatus": "HTTP"
 },
 ...
 ]

```

82 Security


```
 }

```

SUNAPI 83


## **Chapter 16. CA Certificate Settings**
### **16.1. Description**

The **cacertificate** submenu handles CA certificates.


**Access level**

|Action|Camera|
|---|---|
|view|Admin|
|install|Admin|
|remove|Admin|


### **16.2. Syntax**

```
 http://<Device IP>/stw-cgi/security.cgi?msubmenu=
 cacertificate &action=<value>[&<parameter>=<value>...]

### **16.3. Parameters**

```






























|Action|Parameter|Request/<br>Response|Type/<br>Value|Description|
|---|---|---|---|---|
|view||||Reads the SSL (HTTPS) settings|
||Certificate.#.CertificateN<br>ame|RES|<string>|Certificate name|
||Certificate.#.Type|RES|<enum><br>Unique,<br>Public,<br>SelfSigned|Type of the certificate|
||Certificate.#.Subject|RES|<string>|Subject of the certificate|
||Certificate.#.SubjectAlter<br>nativeName|RES|<string>|Subject alternative name (SAN)|
||Certificate.#.Issuer|RES|<string>|Issuer|
||Certificate.#.IssueDate|RES|<string>|Issued date|
||Certificate.#.ExpiryDate|RES|<string>|Expiry date|
||Certificate.#.Version|RES|<string>|Version|
||Certificate.#.SerialNumb<br>er|RES|<string>|Serial number|
||Certificate.#.Signature|RES|<string>|Signature|


84 Security


|Action|Parameter|Request/<br>Response|Type/<br>Value|Description|
|---|---|---|---|---|
||Certificate.#.Thumbprint|RES|<string>|Thumbprint|
||Certificate.#.IsRemovabl<br>e|RES|<bool>|Whether the certificate can be deleted|
|remove|CertificateName|REQ|<string>|Certificate name|
|install||||POST method|

### **16.4. Examples**

#### **16.4.1. Getting the CA certificates**

REQUEST

```
 http://<Device IP>/stw-cgi/security.cgi?msubmenu=cacertificate&action=view

```

TEXT RESPONSE

```
 HTTP/1.0 200 OK
 Content-type: text/plain
 <Body>

 Certificate.1.CertificateName=HTW_rootca
 Certificate.1.Type=Unique
 Certificate.1.Subject=/C=KR/O=Hanwha Vision/OU=Security Solution/CN=Hanwha
 Vision Private Root CA 2
 Certificate.1.SubjectAlternativeName= Certificate.1.Issuer=/C=KR/O=Hanwha Vision/OU=Security Solution/CN=Hanwha
 Vision Private Root CA 2
 Certificate.1.IssueDate=Feb 17 04:15:52 2020 GMT
 Certificate.1.ExpiryDate=Feb 2 04:15:52 2080 GMT
 Certificate.1.Version=V3
 Certificate.1.SerialNumber=00 85 BE B7 49 3A 83 3A E7
 Certificate.1.Signature=sha256WithRSAEncryption
 Certificate.1.Thumbprint=3676ae9bd6ebb4f3543b00c08898d17b7fa96b7e61726a4bd5f
 60c09062c4fce
 Certificate.1.IsRemovable=False
 Certificate.2.CertificateName=helloCA
 Certificate.2.Type=Public
 Certificate.2.Subject=/C=FR/ST=Radius/L=Somewhere/O=Example
 Inc./emailAddress=admin@example.org/CN=Example Certificate Authority

```

SUNAPI 85


```
 Certificate.2.SubjectAlternativeName= Certificate.2.Issuer=/C=FR/ST=Radius/L=Somewhere/O=Example
 Inc./emailAddress=admin@example.org/CN=Example Certificate Authority
 Certificate.2.IssueDate=Mar 9 01:46:25 2020 GMT
 Certificate.2.ExpiryDate=Jan 16 01:46:25 2030 GMT
 Certificate.2.Version=V3
 Certificate.2.SerialNumber=00 62 0A 2B 24 D9 7E DD 53 B2 B5 F6 71 DF 72 92
 08 F0 7F 25 9A
 Certificate.2.Signature=sha256WithRSAEncryption
 Certificate.2.Thumbprint=68b8a185ae17600815b25cd1c42ecbbd62f2b962a62787376fc
 53f9efb211391
 Certificate.2.IsRemovable=True

```

JSON RESPONSE

```
 HTTP/1.0 200 OK
 Content-type: application/json
 <Body>

 {
 "Certificates": [
 {
 "CertificateName": "HTW_rootca",
 "Type": "Unique",
 "Subject": "/C=KR/O=Hanwha Vision/OU=Security Solution/CN=Hanwha
 Vision Private Root CA 2",
 "SubjectAlternativeName": "-",
 "Issuer": "/C=KR/O=Hanwha Vision/OU=Security Solution/CN=Hanwha
 Vision Private Root CA 2",
 "IssueDate": "Feb 17 04:15:52 2020 GMT",
 "ExpiryDate": "Feb 2 04:15:52 2080 GMT",
 "Version": "V3",
 "SerialNumber": "00 85 BE B7 49 3A 83 3A E7 ",
 "Signature": "sha256WithRSAEncryption",
 "Thumbprint":
 "3676ae9bd6ebb4f3543b00c08898d17b7fa96b7e61726a4bd5f60c09062c4fce",
 "IsRemovable": false
 },
 {
 "CertificateName": "helloCA",
 "Type": "Public",

```

86 Security


```
 "Subject": "/C=FR/ST=Radius/L=Somewhere/O=Example
 Inc./emailAddress=admin@example.org/CN=Example Certificate Authority",
 "SubjectAlternativeName": "-",
 "Issuer": "/C=FR/ST=Radius/L=Somewhere/O=Example
 Inc./emailAddress=admin@example.org/CN=Example Certificate Authority",
 "IssueDate": "Mar 9 01:46:25 2020 GMT",
 "ExpiryDate": "Jan 16 01:46:25 2030 GMT",
 "Version": "V3",
 "SerialNumber": "00 62 0A 2B 24 D9 7E DD 53 B2 B5 F6 71 DF 72 92
 08 F0 7F 25 9A ",
 "Signature": "sha256WithRSAEncryption",
 "Thumbprint":
 "68b8a185ae17600815b25cd1c42ecbbd62f2b962a62787376fc53f9efb211391",
 "IsRemovable": true
 }
 ]
 }

#### **16.4.2. Installing CA certificate**
```

REQUEST

```
 http://<Device IP>/stw cgi/security.cgi?msubmenu=cacertificate&action=install

```

When requesting a certificate to be installed, data should be sent via the POST method in the following

format.


The certname value is the certificate name. The certlength value is the certificate data size. The certdata

value is the certificate data. The keylength is the key data size. The keydata value is the key data.

```
 <SetHTTPSData>
 <PublicCertName>certname</PublicCertName>
 <CertLength>certlength</CertLength>
 <CertData>certdata</CertData>
 </SetHTTPSData>

```

**CURL command**


The certificate installation can be tested with CURL as below. To learn about CURL, please refer to

[http://curl.haxx.se.](http://curl.haxx.se)


SUNAPI 87


**NOTE** To get a JSON response, add the -H "Accept: application/json" header to the request.

```
 curl -v --digest -u <userid>:<password> --data-urlencode @cert.xml
 "http://<Device IP>/stw cgi/security.cgi?msubmenu=cacertificate&action=install" -H "Expect:"

```

The above command will produce a request to the device that appears as below:

```
 POST /stw-cgi/security.cgi?msubmenu=ssl&action=install HTTP/1.1
 Content-Length: 3775
 Content-Type: application/x-www-form-urlencoded

```

TEXT RESPONSE

```
 OK

```

JSON RESPONSE

```
 {
 "Response": "Success"
 }

#### **16.4.3. Deleting a certificate**
```

To delete a certificate with the **remove** action, the **CertificateName** parameter must be set at the same

time.


REQUEST

```
 http://<Device IP>/stw cgi/security.cgi?msubmenu=cacertificate&action=remove&CertificateName=certna
 me

```

88 Security


