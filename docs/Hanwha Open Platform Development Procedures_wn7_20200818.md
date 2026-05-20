# **[Hanwha Open Platform Development Procedures]**

This document indicates procedures in developing and finalizing your
application using Hanwha Open Platform.


**1)** **NDA**


You can download the SDK for Hanwha Open Platform App
development by registering on the STEP portal, a membership
program for partners who use Hanwha Techwin products.


When developing an App using SDK and needing support for
materials and functions other than SDK materials, an NDA signing
is required.


**2)** **Open Platform SDK**


The following components are included.


A. SDK package: cross compiler, library files, example code…


$ /opt/opensdk/opensdk-x.00


B. Documentations : Program guide, API, Web page guide


C. Eclipse Plug-in : Camera Project, Build, Installation


**3)** **Development**


You can start development by yourself with 2)Open Platform SDK.


A. API usage can be checked by referring to the sample code.


B. Questions about using API are supported through ‘Help Desk’ –

‘Q&A’ on the STEP site.


**4)** **Conformance Test**


To verify your application’s performance, you should conduct the


conformance test. The purpose of this test is to ensure that the
basic performance of the camera is maintained while your
application is running.


The result of conformance test is uploaded to the STEP site after
filling out the check item of the Conformance Template.


**5)** **Application Registration on STEP site**


The next step in developing an open platform app is the process of
registering the developed app on the STEP site.


[https://step.hanwha-security.com/kor_EN/OpenPlatform/OpenPlatform.aspx](https://step.hanwha-security.com/kor_EN/OpenPlatform/OpenPlatform.aspx)


If you are not a member of the STEP site, please join as an
application partner first.


A. Go to [Open Platform] -> [Hanwha Open Platform] page, click

on Register New Applications button.


B. Enter all of the information require.


   - Conformance test results are written and signed in the Check
List and uploaded to the Test Report field.


   - “Company logo image” requires 163x142 pixels.


   - “Application Link Address” is your web page link address
which includes the introduction of your Open Platform
application and the way to purchase.


C. Description is an introduction comment about the App. When

registration is complete, it will be posted to all users. The
posted content cannot be edited by administrators other than
the author.


D. The staff in charge of Hanwha Open Platform confirms the

conformance test result and uploaded data and approves it to
be posted to all users.


E. After approval, your application will be listed on both a main

page and an Open Platform page.


F. After listing-up, you can request to revise the comments.

Approval process should be needed.


**6)** **App signing certificate release**


App signature verification is introduced from Camera products with
Hanwha Techwin SoC WN7. App signature verification process
ensures that only trusted apps are installed on the camera.


A. you can download the test key and test certificate from STEP

site in the app development step.


B. When registering developed application with conformance test

result on the STEP, you should request a signing key and
certificate for your application.


C. Hanwha sends you the signing key and certificate encrypted by

e-mail.


D. Save the signing key and certificate file in the following

directory of the development computer.
“/opt/opensdk/signature”


Building the app in the Eclipse IDE or running
opensdk_packager creates an electronically signed package file.


E. The camera verify app signature and certificate chain when

installing application on camera.


*** Products that do not use WN7 are the same as the current
development process.












