# Attributes


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

1.1. attributes.cgi. . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . 3

2. Attributes . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . 4

2.1. Overview . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . 4

2.2. Attribute request . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . 4

2.3. Group and category . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . 4

2.4. Example data . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . 4

2.5. Attributes . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . 6

2.5.1. System Group . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . 6

2.5.2. Network Group . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . 8

2.5.3. Transfer Group . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . 9

2.5.4. Security Group . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . 9

2.5.5. Media Group . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . 10

2.5.6. Image Group . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . 12

2.5.7. PTZSupport Group . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . 17

2.5.8. Recording Group . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . 20

2.5.9. EventSource Group . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . 22

2.5.10. IO Group . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . 28

3. CGI . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . 29

3.1. Overview . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . 29

3.2. Examples . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . 29


2 Attributes


## **Chapter 1. Overview**
### **1.1. attributes.cgi**

The attributes and capabilities of Hanwha Vision video surveillance devices are requested by using

**attributes.cgi** .


The following CGI command returns device attributes and CGI information including parameters and

allowed value ranges in XML format.

```
 http://<Device IP>/stw-cgi/attributes.cgi

```

The XML contains two sections.


 - attributes


 - cgi


Each section can be requested separately. It will be explained in detail in Chapter 2 and Chapter 3.


SUNAPI 3


## **Chapter 2. Attributes**
### **2.1. Overview**

The attributes section of the XML contains a few high-level attributes of the features that the device

supports.

### **2.2. Attribute request**

The following command returns only the attributes data.

```
 http://<Device IP>/stw-cgi/attributes.cgi/attributes

### **2.3. Group and category**
```

Attributes are grouped based on the relevant feature and the CGI that is used. The groups are organized

by features and have names such as **System**, **Network**, **Transfer**, etc. Each group is further divided into

the following categories:


 - **Property** : Whether or not the attribute is supported by the device.


 - **Support** : Whether or not the feature is supported.


 - **Limit** : The limits of the device regarding the feature e.g. the number of video channels the device has

or the maximum number of users it allows.

### **2.4. Example data**

Below is the **attributes** part of the XML file.


The **attributes** part consists of groups such as System, Network, IO, etc. The System group has 3

categories: Property, Support, and Limit. It provides information such as the NIC count and the maximum

number of channels (shown in the Limit category) as well as whether or not system configurations or

firmware updates are supported (shown in the Support category).


4 Attributes


SUNAPI 5


### **2.5. Attributes**

The following is an attribute table.

#### **2.5.1. System Group**

|Category|Attribute|Type|Access Level|Col5|Col6|Col7|
|---|---|---|---|---|---|---|
||||**Camera**|**NVR**|**Decoder**|**Encoder**|
|Property|MicomVersion|bool||User|User||
||ISPVersion|bool|Guest|||Guest|
||PTZBoardVersion|bool|Guest|||Guest|
||InterfaceBoardVersion|bool|Guest|||Guest|
||TrackingVersion|bool|Guest|||Guest|
||BootLoaderVersion|bool|Guest|||Guest|
||ModelName|string|Guest|User|User|Guest|
||ONVIFVersion|string|Guest|User|User|Guest|
||SUNAPIVersion|string|Guest|User|User|Guest|



6 Attributes


|Category|Attribute|Type|Access Level|Col5|Col6|Col7|
|---|---|---|---|---|---|---|
||FirmwareVersion|string|Guest|User|User|Guest|
||ModelType|enum|Guest||||
||WisenetPlatformVersion|bool|Guest||||
|Support|GlobalConfiguration|bool||User|User||
||RS422|bool|User|||Admin|
||ConfigRestore|bool|Admin|Admin|Admin|Admin|
||ConfigRestore.ExcludeGroups|enum|Admin|Admin|Admin|Admin|
||ConfigRestore.ExcludeGroups.Net<br>work.Selectable|bool|Admin|Admin|Admin|Admin|
||ConfigRestore.ExcludeGroups.Ca<br>mera.Selectable|bool||Admin|Admin||
||ConfigRestore.ExcludeGroups.Aut<br>hority.Selectable|bool||Admin|Admin||
||ConfigBackup|bool|Admin|Admin|Admin|Admin|
||FWUpdate|bool|Admin|User|User|Admin|
||Shutdown|bool||User|User||
||Restart|bool|Admin|||Admin|
||GPS|bool||User|||
||AutoBackup|bool||User|||
||DigitalSignage|bool||User|||
||OpenSDK|bool|Admin|||Admin|
||FreeStyleSplitMode|bool|||User||
||DisplayMerge|csv|||User||
||SDCardEncryption|bool|Suser||||
||FullDuplex|bool||User|||
||OneOpenAppPerChannel|bool|Suser||||
||SupportChannelExpansionFeature|bool|Guest||||
||LogServer|bool|Admin|User||Admin|
||AIFeatures|bool||User|||
||AIEngine|bool||User|||
||Stratocast|bool|Admin||||
||HybridThermal|bool|Guest||||
||ManufacturerChange|bool|Admin||||


SUNAPI 7


|Category|Attribute|Type|Access Level|Col5|Col6|Col7|
|---|---|---|---|---|---|---|
||SSDStorage|bool|Admin||||
||LocalVMS|bool|Admin||||
||VirtualCropChannel|bool|Guest||||
||MultiLanguageEventSchema|bool|Admin||||
||LiveEventDisplay|bool||User|||
||PowerMode|bool|Guest||||
||SubmonitorMaxResolution|enum||User|||
|Limit|MaxHDMIOut|int|Guest|||Guest|
||NICCount|int|Guest|User|User|Guest|
||MaxChannel|int|Guest|User|User|Guest|
||MaxPOS|int||User|||
||MaxVGAOut|int|||User||
||MaxHDMIOut|int|ADMIN|User|User|ADMIN|
||MaxHDMIIn|int|||User||
||MaxLiveSession|int||User|||
||MaxSearchSession|int||User|||
||MaxBackupSession|int||User|||
||OpenSDK.MaxApps|int|Admin|||Admin|
||MaxSSDStorage|int|Admin||||
||MaxPartitionPerSSD|int|Admin||||
||MaxAnalog|int||User|||
||MaxVGASpotCount|int||User|||
||MaxAnalogSpotCount|int||User|||
||ChannelExpansionLimit|int|Guest||||
||MaxAudioSubDevices<br>**AMS ONLY**<br>|int|Guest||||
||MaxSpeakerGroups<br>**AMS ONLY**<br>|int|Guest||||

#### **2.5.2. Network Group**





|Category|Attribute|Type|Access Level|Col5|Col6|Col7|
|---|---|---|---|---|---|---|
||||**Camera**|**NVR**|**Decoder**|**Encoder**|
|Limit|MaxIPv4Filter|int|Guest|User|User|Guest|


8 Attributes


|Category|Attribute|Type|Access Level|Col5|Col6|Col7|
|---|---|---|---|---|---|---|
||MaxIPv6Filter|int|Guest|User|User|Guest|
||MaxIPv4QoS|int|Guest|User|User|Guest|
||MaxIPv6QoS|int|Guest|User|User|Guest|
||MaxNetCam|int||User|||
||MaxSIPAccountCount|int|Guest||||
||MaxRecipientCount|int|Guest||||
||MaxRecipientInGroup|int|Guest||||
|Support|BandwidthControl|bool||User|User||
||POE|bool||User|User||
||WiFi|bool|Admin|User|User|Admin|
||TUTK|bool||User|User||
||POEExtender|bool|Admin||||
||MTUSize|bool|Guest||||
||SIP|bool|Admin||||
||DDNSP2P|bool||User|||
||MQTT|bool|Admin||||
||NetworkAudioIn<br>**AMS ONLY**<br>|bool|User||||

#### **2.5.3. Transfer Group**





|Category|Attribute|Type|Access Level|Col5|Col6|Col7|
|---|---|---|---|---|---|---|
||||**Camera**|**NVR**|**Decoder**|**Encoder**|
|Support|SMTP|bool|Admin|User||Admin|
||HTTP|bool|Admin|User||Admin|
||FTP|bool|Admin|User||Admin|
||DataServer|bool|Guest||||
|Limit|SMTP.MaxRecipients||Admin|||Admin|

#### **2.5.4. Security Group**

|Category|Attribute|Type|Access Level|Col5|Col6|Col7|
|---|---|---|---|---|---|---|
||||**Camera**|**NVR**|**Decoder**|**Encoder**|
|Limit|MaxAdditionalPasswords|int||User|User||
||MaxUser|int|Guest|User|User|Guest|



SUNAPI 9


|Category|Attribute|Type|Access Level|Col5|Col6|Col7|
|---|---|---|---|---|---|---|
||MaxGroup|int||Admin|Admin||
||MaxUserPerGroup|int||Admin|Admin||
||MaxSMTPGroup|int||User|User||
||MaxSMTPUser|int||User|User||
||MaxSMTPUserPerGroup|int||User|User||
|Support|AdminIDChangeable|bool|Admin|User|User||
||ClientCertificateAuthentication|bool|Admin||||
||AdminAccess|bool|Admin||||
||MaxSelfSignedCertificates|int|Guest||||
||NewPasswordPolicy|bool|Guest||||
||CurrentPasswordVerification|enum|User||||

#### **2.5.5. Media Group**










|Categor<br>y|Channel|Attribute|Type|Access Level|Col6|Col7|Col8|
|---|---|---|---|---|---|---|---|
|||||**Camera**|**NVR**|**Decoder**|**Encoder**|
|Limit|Channel.<br>#|MaxAudioInput|int|Guest|User|User|Guest|
|||MaxAudioOutput|int|Guest|User|User|Guest|
|||MaxProfile|int|Guest|User|User|Guest|
|||MaxResolution|enum|Guest|||Guest|
||Streamin<br>gMetada<br>ta||csv||User|||
||Streamin<br>gProfiles||csv||User|||
||MaxVide<br>oOutput||int|Guest||||
||MaxAudi<br>oInput||int|Guest||||
|Support|Channel.<br>#|WiseStream|bool|Guest|||Guest|
|||DynamicGOV|bool|Guest|||Guest|
|||DynamicFPS|bool|Guest||||
|||Protocol.SUNAPI|bool||User|User||



10 Attributes


|Categor<br>y|Channel|Attribute|Type|Access Level|Col6|Col7|Col8|
|---|---|---|---|---|---|---|---|
|||ChannelAudioOutput|bool||User|User||
|||DeviceAudioOutput|bool|Suser|||Suser|
|||MultiAudioOutput|Bool|Admin|||Admin|
|||AudioIn|bool|Suser|User|User|Suser|
|||VideoOut|bool|Suser||||
|||ATC|bool|Guest|||Guest|
|||Crop|bool|Guest|||Guest|
|||VideoEncodingType|enum|Guest|User|User|Guest|
|||AudioEncodingType|enum|Guest|User|User|Guest|
|||VideoSetting|bool|User|||Admin|
|||ExactTimeStamp|bool|Guest|||Guest|
|||Live|bool|Guest|User||Guest|
|||FixedProfileCodecChange|bool|Guest|||Guest|
|||ShowNonVideoProfile|bool|Guest|||Guest|
|||ProfileAddByIndex|bool|User|||Admin|
|||Stream.UDP|bool|Guest|User||Guest|
|||Stream.TCP|bool|Guest|User||Guest|
|||Stream.Multicast|bool|Guest|User||Guest|
|||Stream.MulticastIPV6|bool|Guest||||
|||Stream.RTPOverRTSPOverTCP|bool|Guest|User||Guest|
|||Stream.RTSPOverHTTP|bool|Guest|User||Guest|
|||Stream.RTSPOverHTTPS|bool|Guest|User||Guest|
|||Stream.MultiProfiles|bool||User|||
|||Stream.Metadata|bool||User|||
|||Stream.SRTP.UDP|bool|Guest||||
|||Stream.SRTP.TCP|bool|Guest||||
|||Stream.SRTP.Multicast|bool|Guest||||
|||Stream.SRTP.RTSPOverRTSPO<br>verTCP|bool|Guest||||
|||Stream.SRTP.RTSPOverHTTP|bool|Guest||||
|||Stream.SRTP.RTSPOverHTTPS|bool|Guest||||
|||Stream.RTSPBlocksize|bool|Guest||||


SUNAPI 11


|Categor<br>y|Channel|Attribute|Type|Access Level|Col6|Col7|Col8|
|---|---|---|---|---|---|---|---|
|||Stream.BackchannelOverPost|bool||admin|||
|||Metadata.ImageType|csv|Guest||||
|||Metadata.ImageTransfer|bool|Guest||||
|||Metadata.ClassTypes|bool|Guest||||
|||Metadata.ClassTypeDetails|bool|Guest||||
|||SensorCaptureMode|bool|Guest||||
|||DynamicPrivacyMask|bool|Guest||||
||GlobalSe<br>nsorMod<br>e||bool|Guest||||
||Metadat<br>aShare||bool|Guest||||
||Dynamic<br>PrivacyM<br>ask||bool|Guest||||

#### **2.5.6. Image Group**

















|Categor<br>y|Channel|Attribute|Type|Access Level|Col6|Col7|Col8|
|---|---|---|---|---|---|---|---|
|||||**Camera**|**NVR**|**Decoder**|**Encoder**|
|Limit|Channel.<br>#|MaxSmartCodecArea|int|Guest|||Guest|
|||MaxPrivacyMask|int|Guest|||Guest|
|||MaxPrivacyMask.Rectangle|int|Guest|||Guest|
|||MaxPrivacyMask.Polygon|int|Guest|||Guest|
|||MaxOSDTitles|int|Guest|||Guest|
|||MaxOSDDates|int|Guest|||Guest|
|||ViewModes|int|Guest|||Guest|
|||ViewModes.MaxActive|int|Guest|||Guest|
|||MaxIRZoneCountInCeilingMo<br>de|int|Guest||||
|||MaxIRZoneCountInWallMode|int|Guest||||
|||MaxFocusPreset|int|Guest||||
|||MaxIRZoneCount|int|Guest||||


12 Attributes


|Categor<br>y|Channel|Attribute|Type|Access Level|Col6|Col7|Col8|
|---|---|---|---|---|---|---|---|
|||MaxAutoFocusZoneCount|int|Guest||||
|Support|Channel.<br>#|Defog|bool|User|User||Admin|
|||ProfileBasedDewarpedView|bool|Guest|User||Guest|
|||MultiImager|bool|Guest|User||Guest|
|||OSDLanguages|csv|Guest|||Guest|
|||Gamma|bool|User|||Admin|
|||Saturation|bool|User|||Admin|
|||Sharpness|bool|User|||Admin|
|||Brightness|bool|User|||Admin|
|||ResetFocus|bool||User|||
|||SimpleFocus|bool||User|||
|||SimpleFocus.FocusArea|bool|User|||Admin|
|||PrivacyMask.ZoomThreshold|bool|Suser|||Admin|
|||Privacy.MaskColor.Global|bool|Suser|||Admin|
|||FocusAdjust|bool|Suser||||
|||ZoomAdjust|bool|Suser||||
|||IRLED|bool|Suser||||
|||ZoneBasedIRLED|bool|Guest||||
|||DIS|bool|Suser||||
|||P-Iris|bool|Suser||||
|||DayNight|bool|Suser||||
|||FisheyeLens|bool|Guest|User|||
|||DewarpedView|bool|Guest|User|||
|||ThermalFeatures|bool|Guest||||
|||PTRZ|bool|Suser||||
|||ViewModes.360Panorama|bool|Guest||||
|||ViewModes.360Panorama.Sub<br>Views|int|Guest||||
|||ViewModes.360Panorama.PTZ|bool|Guest||||
|||ViewModes.360Panorama.PTZ<br>.Features|csv|Guest||||



SUNAPI 13


|Categor<br>y|Channel|Attribute|Type|Access Level|Col6|Col7|Col8|
|---|---|---|---|---|---|---|---|
|||ViewModes.OneOverviewAndT<br>ripleView|bool|Guest||||
|||ViewModes.OneOverviewAndT<br>ripleView.SubViews|int|Guest||||
|||ViewModes.OneOverviewAndT<br>ripleView.PTZ|bool|Guest||||
|||ViewModes.OneOverviewAndT<br>ripleView.PTZ.Features|csv|Guest||||
|||ViewModes.OneOverviewAnd<br>OctaView|bool|Guest||||
|||ViewModes.OneOverviewAnd<br>OctaView.SubViews|int|Guest||||
|||ViewModes.OneOverviewAnd<br>OctaView.PTZ|bool|Guest||||
|||ViewModes.OneOverviewAnd<br>OctaView.PTZ.Features|csv|Guest||||
|||ViewModes.Overview|bool|Guest||||
|||ViewModes.Overview.SubView<br>s|int|Guest||||
|||ViewModes.Overview.PTZ|bool|Guest||||
|||ViewModes.Overview.PTZ.Feat<br>ures|csv|Guest||||
|||ViewModes.LeftHalfView|bool|Guest||||
|||ViewModes.LeftHalfView.SubV<br>iews|int|Guest||||
|||ViewModes.LeftHalfView.PTZ|bool|Guest||||
|||ViewModes.LeftHalfView.PTZ.F<br>eatures|csv|Guest||||
|||ViewModes.RightHalfView|bool|Guest||||
|||ViewModes.RightHalfView.Sub<br>Views|int|Guest||||
|||ViewModes.RightHalfView.PTZ|bool|Guest||||
|||ViewModes.RightHalfView.PTZ<br>.Features|csv|Guest||||
|||ViewModes.SingleView|bool|Guest||||


14 Attributes


|Categor<br>y|Channel|Attribute|Type|Access Level|Col6|Col7|Col8|
|---|---|---|---|---|---|---|---|
|||ViewModes.SingleView.SubVie<br>ws|int|Guest||||
|||ViewModes.SingleView.PTZ|bool|Guest||||
|||ViewModes.SingleView.PTZ.Fe<br>atures|csv|Guest||||
|||ViewModes.QuadView|bool|Guest||||
|||ViewModes.QuadView.SubVie<br>ws|int|Guest||||
|||ViewModes.QuadView.PTZ|bool|Guest||||
|||ViewModes.QuadView.PTZ.Fea<br>tures|csv|Guest||||
|||ViewModes.QuadView.#|bool|Guest||||
|||ViewModes.QuadView..#.SubV<br>iews|int|Guest||||
|||ViewModes.QuadView..#.PTZ|bool|Guest||||
|||ViewModes.QuadView..#.PTZ.F<br>eatures|csv|Guest||||
|||ViewModes.Panorama|bool|Guest||||
|||ViewModes.Panorama.SubVie<br>ws|int|Guest||||
|||ViewModes.Panorama.PTZ|bool|Guest||||
|||ViewModes.Panorama.PTZ.Fe<br>atures|csv|Guest||||
|||ViewModes.DoublePanorama|bool|Guest||||
|||ViewModes.DoublePanorama.<br>SubViews|int|Guest||||
|||ViewModes.DoublePanorama.<br>PTZ|bool|Guest||||
|||ViewModes.DoublePanorama.<br>PTZ.Features|csv|Guest||||
|||ViewModes.CropView|bool|Guest||||
|||ViewModes.CropView.SubView<br>s|int|Guest||||
|||ViewModes.CropView.PTZ|bool|Guest||||


SUNAPI 15


|Categor<br>y|Channel|Attribute|Type|Access Level|Col6|Col7|Col8|
|---|---|---|---|---|---|---|---|
|||ViewModes.CropView.PTZ.Feat<br>ures|csv|Guest||||
|||NormalizedOSDRange|bool|Guest|||Guest|
|||AutoImageAlignmentSupport|bool|Guest||||
|||ImageSettings|bool|User||||
|||Iris|bool|User||||
|||Iris-Fno|bool|User||||
|||LDC|bool|User||||
|||Crop|bool|Admin||||
|||DynamicArea|bool|Guest||||
|||AutoFocus|bool|User||||
|||DirectionIndicator|bool|Suser||||
|||OSDArrow|bool|Suser||||
|||Contrast|bool|User||||
|||WhiteBalance|bool|User||||
|||BackLight|bool|User||||
|||DayNightSwitchThresholdAdju<br>st|bool|User||||
|||XCE|bool|User||||
|||FocusContinuousAdjust|bool|User||||
|||ZoomContinuousAdjust|bool|User||||
|||AntiFlicker|bool|Guest||||
|||AGC|bool|Guest||||
|||ShutterControl|bool|Guest||||
|||ThermalVariationSensitivity|bool|Guest||||
|||FocusPreset|bool|Guest||||
|||HorizontalFlip|bool|Guest||||
|||VerticalFlip|bool|Guest||||
|||Rotate|enum|Guest||||
|||UnifiedFlip|bool|Guest||||
|||RotateAndLDCIncompatible|bool|Admin||||
|||RotateAndVideoOutIncompati<br>ble|bool|Admin||||



16 Attributes


|Categor<br>y|Channel|Attribute|Type|Access Level|Col6|Col7|Col8|
|---|---|---|---|---|---|---|---|
|||PrivacyIndexReorder|bool|Guest||||
|||ImageAlignment|csv|Guest||||
|||SSNR2DLevel|bool|Suser||||
|||SSNR3DLevel|bool|Suser||||
|||ThermalNUC|bool|Guest||||
|||PrivacyAndDISIncompatible|bool|User||||
|||AutoFocusZone|bool|Suser||||
|||WiseAutoFocus|bool|Suser||||
|||WhiteLED|bool|Admin||||
||GlobalRo<br>tateView||bool|Guest||||
||GlobalLD<br>CMode||bool|Guest||||
||GlobalM<br>askPatte<br>rn||bool|Guest||||
||GlobalM<br>ultiImag<br>eOSD||bool|Guest||||

#### **2.5.7. PTZSupport Group**












|Categor<br>y|Channel|Attribute|Type|Access Level|Col6|Col7|Col8|
|---|---|---|---|---|---|---|---|
|||||**Camera**|**NVR**|**Decoder**|**Encoder**|
|Support|Channel.<br>#|Preset|Bool|Suser|User|User|Suser|
|||Swing|Bool|Suser|User|User|Suser|
|||Group|Bool|Suser|User|User|Suser|
|||DigitalZoom|Bool|Suser|||Suser|
|||Trace|bool|Suser|User|User|Suser|
|||AutoRun|bool|Suser|User|User|Suser|
|||Home|bool|Suser|User|User|Suser|
|||Tour|bool|Suser|User|User|Suser|
|||PresetRename|bool|Admin|User|User|Admin|



SUNAPI 17


|Categor<br>y|Channel|Attribute|Type|Access Level|Col6|Col7|Col8|
|---|---|---|---|---|---|---|---|
|||PTZLimit|bool|User|User|User|Admin|
|||AreaZoom|bool|Suser|User|User|Suser|
|||Query.Pan|bool|Suser|User|User|Suser|
|||Query.Tilt|bool|Suser|User|User|Suser|
|||Query.Zoom|bool|Suser|User|User|Suser|
|||Query.Focus|bool|Suser|User|User|Suser|
|||Query.Iris|bool|Suser|User|User|Suser|
|||OSDMenu.On|bool|User|User|User|Admin|
|||OSDMenu.Off|bool|User|User|User|Admin|
|||OSDMenu.Up|bool|User|User|User|Admin|
|||OSDMenu.Down|bool|User|User|User|Admin|
|||OSDMenu.Right|bool|User|User|User|Admin|
|||OSDMenu.Left|bool|User|User|User|Admin|
|||OSDMenu.Select|bool|User|User|User|Admin|
|||OSDMenu.Return|bool|User|User|User|Admin|
|||Absolute.Pan|bool|Suser|User|User|Suser|
|||Absolute.Tilt|bool|Suser|User|User|Suser|
|||Absolute.Zoom|bool|Suser|User|User|Suser|
|||Absolute.Focus|bool|Suser|User|User|Suser|
|||Absolute.Iris|bool|Suser|User|User|Suser|
|||Absolute.PanSpeed|bool|Suser|User|User|Suser|
|||Absolute.TiltSpeed|bool|Suser|User|User|Suser|
|||Absolute.ZoomSpeed|bool|Suser|User|User|Suser|
|||Continuous.Pan|bool|Suser|User|User|Suser|
|||Continuous.Tilt|bool|Suser|User|User|Suser|
|||Continuous.Zoom|bool|Suser|User|User|Suser|
|||Continuous.Focus|bool|Suser|User|User|Suser|
|||Continuous.Iris|bool|Suser|User|User|Suser|
|||Continuous.PanSpeed|bool|Suser|User|User|Suser|
|||Continuous.TiltSpeed|bool|Suser|User|User|Suser|
|||Continuous.ZoomSpeed|bool|Suser|User|User|Suser|
|||Relative.Pan|bool|Suser|User|User|Suser|



18 Attributes


|Categor<br>y|Channel|Attribute|Type|Access Level|Col6|Col7|Col8|
|---|---|---|---|---|---|---|---|
|||Relative.Tilt|bool|Suser|User|User|Suser|
|||Relative.Zoom|bool|Suser|User|User|Suser|
|||Relative.Focus|bool|Suser|User|User|Suser|
|||Relative.Iris|bool|Suser|User|User|Suser|
|||3AxisPTZ|bool|Suser|User|User|Suser|
|||Azimuth|bool|Suser|||Suser|
|||ProfileBasedDigitalPTZ|bool|Suser||||
|||DigitalAutoTracking|bool|Suser|User|User|Suser|
|||DigitalPTZ|bool|Suser|User|User|Suser|
|||ExternalPTZ|bool|Suser|||Suser|
|||RealPTZ|bool|Suser|||Suser|
|||ZoomOnly|bool|Suser|||Suser|
|||AuxCommands|csv|Suser|User|User||
|||PanTiltOnly|bool|Suser||||
|||PanZeroPosition|bool|Suser||||
|||SmartZoom|bool|Suser||||
|||PTCorrection|bool|Suser||||
|||AIAutoTracking|bool|Suser||||
|||PresetImageConfig|bool|Suser||||
|||PresetImageConfig.XCE|bool|Suser||||
|||PresetVideoAnalysis|bool|Suser||||
|||MountPosition|bool|Suser||||
|||PresetObjectDetection|bool|Suser||||
|||QuickZoom|bool|Suser||||
||GlobalPT<br>ZMode||bool|Suser||||
||DigitalRT<br>ZOnlyInD<br>efaultSet<br>tings||bool|Suser||||
|Limit|Channel.<br>#|MaxPreset|int|Guest|User|User|Guest|
|||MaxGroupCount|int|Guest|User|User|Guest|



SUNAPI 19


|Categor<br>y|Channel|Attribute|Type|Access Level|Col6|Col7|Col8|
|---|---|---|---|---|---|---|---|
|||MaxTourCount|int|Guest|User|User|Guest|
|||MaxTraceCount|int|Guest|User|User|Guest|
|||MaxPresetCountPerGroup|int|Guest|User|User|Guest|
|||MaxGroupCountPerTour|int|Guest|User|User|Guest|


#### **2.5.8. Recording Group**



















|Categor<br>y|Channel or<br>Attribute|Attribute|Type|Access Level|Col6|Col7|Col8|
|---|---|---|---|---|---|---|---|
|||||**Camera**|**NVR**|**Decoder**|**Encoder**|
|Support|Channel.#|QueueManagemen<br>t|bool|User||||
|||SearchVideoSumm<br>ary|bool||User|||
|||Backup|bool|User|User|||
|||SearchCalendar|bool|User|User|||
|||SearchTimeline|bool|User|User|||
|||SearchEvent|bool|User|User|||
|||SearchMotionGrid|bool||User|||
|||PeopleCountSearch|bool|Admin||||
|||SmartSearch|bool||User|||
|||SearchHeatMap|bool||User|||
|||AISearchTypes|csv||User|||
|||SearchBookmark|bool||User|||
||SearchMetadata||bool||User|||
||ContinuousPlayNVR||bool||User|||
||RecordStreamLimit<br>ation||bool|Guest||||
||RAID||bool||User|||
||FailOverRecording||bool||User|||
||SearchPOS||bool||User|||
||SearchPeriod||bool||User|||
||Recording||bool|User|User|||


20 Attributes


|Categor<br>y|Channel or<br>Attribute|Attribute|Type|Access Level|Col6|Col7|Col8|
|---|---|---|---|---|---|---|---|
||ManualRecordingSt<br>art||bool||User|||
||ManualRecordingSt<br>op||bool||User|||
||RecordingStatus||bool|User|User|||
||Overlapped||bool|User|User|||
||PlaybackType||enum|User|User|||
||PlaybackSpeed||enum|User|User|||
||NAS||bool|User||||
||iSCSI||bool|User|User|||
||SearchByUTCTime||bool|User|User|||
||HeatMapGridArea||string||User|||
||RecordPriorityOrde<br>r||csv||User|||
||DualTrackRecordin<br>g||bool||Guest|||
||DiskUtility||csv||User|||
||DistributedRecordi<br>ng||bool||User|||
||GlobalRecordFileTy<br>pe||bool|Guest||||
||SimplePlaybackPag<br>e||bool|Suser||||
|Limit|MaxPlaybackChann<br>els||int||User|||
||MaxSmartSearchDa<br>ys||int||User|||
||MaxMetadataSearc<br>hDays||int||User|||
||MaxSmartSearchIn<br>cludeAreas||int||User|||
||MaxSmartSearchEx<br>cludeAreas||int||User|||
||MaxSmartSearchLin<br>es||int||User|||



SUNAPI 21


|Categor<br>y|Channel or<br>Attribute|Attribute|Type|Access Level|Col6|Col7|Col8|
|---|---|---|---|---|---|---|---|
||NumberOfStorage<br>Devices||int|User|User|||
||PreferRecordingCo<br>dec||enum|User||||
||RecordingGOVLeng<br>thMultiplierFactor||float|User||||


#### **2.5.9. EventSource Group**
































|Categor<br>y|Channel or<br>Attribute|Attribute|Type|Access Level|Col6|Col7|Col8|
|---|---|---|---|---|---|---|---|
|||||**Camera**|**NVR**|**Decoder**|**Encoder**|
|Limit|Channel.#|MaxROI.Include|int|Guest|||Guest|
|||MaxROI.Exclude|int|Guest|||Guest|
|||MaxIVRule.Area.Incl<br>ude|int|Guest|||Guest|
|||MaxIVRule.Area.Exc<br>lude|int|Guest|||Guest|
|||MaxIVRule.Line|int|Guest|||Guest|
|||MaxFaceDetection.<br>Area.Include|int|Guest|||Guest|
|||MaxFaceDetection.<br>Area.Exclude|int|Guest|||Guest|
|||MaxParkingArea|int|Guest||||
|||MaxExcludeParking<br>Area|int|Guest||||
|||MaxPeopleCountRu<br>le|int|Guest||||
|||MaxVehicleCountRu<br>le|int|Guest||||
||MaxQueues||int|Guest|||Guest|
||MaxPeopleCountRu<br>le||int|Guest||||
||MaxVehicleCountRu<br>le||int|Guest||||
||MaxHeatMap.Area.<br>Exclude||int|Guest||||



22 Attributes


|Categor<br>y|Channel or<br>Attribute|Attribute|Type|Access Level|Col6|Col7|Col8|
|---|---|---|---|---|---|---|---|
||MaxROI||int|Guest|||Guest|
||MaxFaceDetectionA<br>rea||int|Guest|||Guest|
||MaxTamperingDete<br>ctionArea||int|Guest|||Guest|
||MaxTrackingArea||int|Guest|||Guest|
||MaxAlarmInput||int|Guest|User|User|Guest|
||MaxNetworkAlarmI<br>nput||int||User|User||
||MaxIVRule||int|Guest|||Guest|
||MaxIVRule.Line||int|Guest|||Guest|
||MaxIVRule.Area||int|Guest|||Guest|
||ROICoordinate.Min<br>X||int|Guest|||Guest|
||ROICoordinate.Min<br>Y||int|Guest|||Guest|
||ROICoordinate.Max<br>X||int|Guest|||Guest|
||ROICoordinate.Max<br>Y||int|Guest|||Guest|
||MaxIVRule.Area.Incl<br>ude||int|Guest|||Guest|
||MaxIVRule.Area.Exc<br>lude||int|Guest|||Guest|
||MaxROI.Include||int|Guest|||Guest|
||MaxROI.Exclude||int|Guest|||Guest|
||MaxCoordinate.Defi<br>nedArea.AppearDis<br>appear||int|Guest|||Guest|
||MaxCoordinate.Defi<br>nedArea.Entering||int|Guest|||Guest|
||MaxCoordinate.Defi<br>nedArea.Exiting||int|Guest|||Guest|
||MaxHeatMapLevel||int|Guest|||Guest|
||MaxBoxTemperatur<br>eDetectionArea||int|Guest||||



SUNAPI 23


|Categor<br>y|Channel or<br>Attribute|Attribute|Type|Access Level|Col6|Col7|Col8|
|---|---|---|---|---|---|---|---|
||MaxBodyTemperat<br>ureDetectionArea||int|Guest||||
||MaxDTMFCodeCou<br>nt||int|Guest||||
||MaxDynamicRule||int|Admin||||
||MaxDynamicRule.E<br>ventSource||int|Admin||||
||MaxScheduleCount||int|Admin||||
||MaxMQTTMessage<br>Count||int|Admin||||
||MaxMQTTSubscript<br>ionCount||int|Admin||||
||MaxAudioFiles<br>**AMS ONLY**<br>||int|Guest||||
||MaxTTSFiles<br>**AMS ONLY**<br>||int|Guest||||
|Support|Channel.#|VideoAnalytics|csv|Guest|User|User|Guest|
|||AudioAnalytics|csv|Guest|User|User|Guest|
|||ThermalGridArea|string|Admin|||Admin|
|||IVRule|bool|Admin|||Admin|
|||GetIVRule|bool|Admin|||Admin|
|||OverlayIVRule|bool|Guest|||Guest|
|||AdjustMDIVRuleOn<br>FlipMirror|bool|Guest|||Guest|
|||ObjectDetection|bool|Guest|Admin|||
|||ObjectTypes|csv||Admin|||
|||ObjectDetection.Ev<br>entActions|csv|Guest||||
|||FaceDetection|bool|Guest|||Guest|
|||HeadDetection|bool|Guest||||
|||FaceDetection.Even<br>tActions|csv|Guest|||Guest|
|||Tracking|bool|Guest|||Guest|
|||Tracking.EventActio<br>ns|csv|Guest|||Guest|



24 Attributes


|Categor<br>y|Channel or<br>Attribute|Attribute|Type|Access Level|Col6|Col7|Col8|
|---|---|---|---|---|---|---|---|
|||Metadata|bool|Admin|User|User|Admin|
|||AdvancedMotionDe<br>tection|bool||User|User||
|||BodyTemperatureD<br>etection|bool|Guest||||
|||BodyTemperatureD<br>etection.EventActio<br>ns|csv|Guest||||
|||BoxTemperatureDe<br>tection|bool|Guest||||
|||TamperingDetectio<br>n.DarknessDetectio<br>n|bool|Guest||||
|||MaskDetection|bool|Guest||||
|||MaskDetection.Eve<br>ntActions|csv|Guest||||
|||ParkingDetection|bool|Guest||||
|||ParkingDetection.E<br>ventActions|csv|Guest||||
|||LEDIndicator|bool|Guest||||
|||LEDIndicator.Sourc<br>eChannel|csv|Guest||||
|||CallRequest|bool|Guest||||
|||CallRequest.EventA<br>ctions|csv|Guest||||
|||TamperingSwitch|bool|Guest||||
|||TamperingSwitch.E<br>ventActions|csv|Guest||||
|||DTMF|bool|Guest||||
|||DTMF.EventActions|csv|Guest||||
|||ProximitySensor|bool|Guest||||
|||ProximitySensor.Ev<br>entActions|csv|Guest||||
|||SocialDistancingViol<br>ation|bool|Guest||||



SUNAPI 25


|Categor<br>y|Channel or<br>Attribute|Attribute|Type|Access Level|Col6|Col7|Col8|
|---|---|---|---|---|---|---|---|
|||SocialDistancingViol<br>ation.EventActions|csv|Guest||||
||ROIType||enum|Admin|||Admin|
||TamperingDetectio<br>n||bool|Guest|||Guest|
||NetworkAlarmInput||bool||User|User||
||AlarmInput||bool|Guest|User|User|Guest|
||AlarmOutput||bool|Guest|User|User|Guest|
||AudioDetection||bool|Guest|User|User|Guest|
||UserInput||bool|Guest|||Guest|
||UserInput.EventActi<br>ons||csv|Guest|||Guest|
||NetworkDisconnect||bool|Guest|User|User|Guest|
||VideoLoss||bool||User|User||
||VA.Passing||bool|Guest|||Guest|
||VA.Enter||bool|Guest|||Guest|
||VA.Exit||bool|Guest|||Guest|
||VA.Appear||bool|Guest|||Guest|
||VA.Disappear||bool|Guest|||Guest|
||VA.MotionDetection||bool|Guest|||Guest|
||VA.MotionDetection<br>.Overlay||bool|Guest|||Guest|
||VA.MotionDetection<br>.ObjectSize||bool|Guest|||Guest|
||VA.AppearDisappea<br>rType||enum|Admin|||Admin|
||VA.Intrusion||bool|Guest|||Guest|
||VA.Loitering||bool|Guest|||Guest|
||TamperingDetectio<br>n.EventActions||csv|Guest|User|User|Guest|
||AlarmInput.EventAc<br>tions||csv|Guest|User|User|Guest|
||AudioDetection.Eve<br>ntActions||csv|Guest|User|User|Guest|



26 Attributes


|Categor<br>y|Channel or<br>Attribute|Attribute|Type|Access Level|Col6|Col7|Col8|
|---|---|---|---|---|---|---|---|
||NetworkDisconnect<br>.EventActions||csv|Guest|User|User|Guest|
||VideoLoss.EventActi<br>ons||csv|Guest|User|User|Guest|
||VA.MotionDetection<br>.EventActions||csv|Guest|User|User|Guest|
||Timer||bool|Guest|||Guest|
||Timer.EventActions||csv|Guest|||Guest|
||DefocusDetection||bool|Guest|||Guest|
||DefocusDetection.E<br>ventActions||csv|Guest|User|User|Guest|
||OpenSDK||bool|Guest|||Guest|
||OpenSDK.EventActi<br>ons||csv|Guest|||Guest|
||FogDetection||bool|Guest|||Guest|
||FogDetection.Event<br>Actions||csv|Guest|User|User|Guest|
||TemperatureChang<br>eDetection||bool|Guest|||Guest|
||TemperatureChang<br>eDetection.EventAc<br>tions||csv|Guest|||Guest|
||ShockDetection||bool|Guest|||Guest|
||ShockDetection.Eve<br>ntActions||csv|Guest|||Guest|
||AudioAnalysis||bool|Guest|||Guest|
||WaterLevelWarning||bool|Guest||||
||HousingTampering||bool|Guest||||
||BoxTemperatureDe<br>tection.EventAction<br>s||csv|Guest||||
||BodyTemperatureD<br>etection||bool|Guest||||
||BodyTemperatureD<br>etection.EventActio<br>ns||csv|Guest||||



SUNAPI 27


|Categor<br>y|Channel or<br>Attribute|Attribute|Type|Access Level|Col6|Col7|Col8|
|---|---|---|---|---|---|---|---|
||TamperingDetectio<br>n.DarknessDetectio<br>n||bool|Guest||||
||ChannelBasedROIC<br>oordinate||bool|Guest||||
||GlobalAudioDetecti<br>on||bool|Guest||||
||GlobalAudioAnalysi<br>s||bool|Guest||||
||CallRequest||bool|Guest||||
||CallRequest.EventA<br>ctions||csv|Guest||||
||TamperingSwitch||bool|Guest||||
||TamperingSwitch.E<br>ventActions||csv|Guest||||
||DTMF||bool|Guest||||
||DTMF.EventActions||csv|Guest||||
||ProximitySensor||bool|Guest||||
||ProximitySensor.Ev<br>entActions||csv|Guest||||
||DynamicRule||bool|Admin||||

#### **2.5.10. IO Group**

|Category|Attribute|Type|Access Level|Col5|Col6|Col7|
|---|---|---|---|---|---|---|
||||**Camera**|**NVR**|**Decoder**|**Encoder**|
|Limit|MaxAlarmOutput|int|Guest|User|User|Guest|
||MaxAux|int|Guest|User|User|Guest|
||MaxConfigurableIO|bool|Guest||||
|Support|AlarmOutput|bool|Suser|User|User|Suser|
||Aux|bool|Suser|User|User|Suser|
||RS485|bool|Suser|User||Suser|
||AlarmReset|bool|Admin|User||Admin|
||PowerRelayIndices|int|Suser||||
||ConfigurableIO|bool|Suser||||



28 Attributes


## **Chapter 3. CGI**
### **3.1. Overview**

Each CGI part of the XML represents the submenus, actions and parameters available in the

corresponding CGI. The XML data contains the parameter data type, allowed ranges/values and type of

parameter (request/response).


The following command returns only the cgi part of the XML.

```
 http://<Device IP>/stw-cgi/attributes.cgi/<cgi name>

### **3.2. Examples**
```

The following example shows a request for only the system-related submenus and parameters of the

device.


REQUEST

```
 http://<Device IP>/stw-cgi/attributes.cgi/system

```

RESPONSE

```
 HTTP Code: 200 OK
 Content-Type: text/xml
 <Body>

```

SUNAPI 29


30 Attributes


SUNAPI 31


