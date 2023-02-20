# ARID

Instant access to IDs or information from a code. 
- We redefined personal identification by combining AR. 
- No need to worry about losing ID Card
- No need to worry about security
- We got you covered. 

##### https://devpost.com/software/ar-info

## Inspiration
Having used OpenCV for several projects, ranging mostly from machine learning detections, one of the things we have never done was anything AR related. We thought this was one possible use case of utilizing AR codes; showing ID's so that doctors, officers, and users would have a quick and easy access to their information. We also added a verification step for privacy protection in the form of twilio.

## What it does
A user uploads their ID into the backend via a frontend user prompt. The image is stored alongside their names. An ARUCO code is generated to pair with the image. The user can point the code towards the screen where they will be sent a verification text. If not verified, the program will not screen the ARUCO code. If verified, the camera takes the ARUCO code and transposes the ID/image via homography transformation. There is no limit to how many it can display or what orientation or size.

Note; future expansion can include video and even 3D representation of data -- the possibilites are limitless.

## How we built it
Our first task was to tackle the hard thing first: the backend and the actual AR processing. We played around in python with opencv to create an app that takes still frame images and checks for any matching ARUCO codes. Once that was done, we decided to implement it into a web framework so it is accessible by any device. We implemented a model for ID's in Django alongside a camera module and a user upload module. Certain things were needed to be changed as OpenCV did not function ideally in Django so we had to come up with a work-around in our detection function. Lastly, after it was implemented, we decided to host on AWS/Heroku for a demo.

## Challenges we ran into
#### AIORTC and Browser Camera
So far when we hosted the project on AWS, the camera does not work; it only does so locally. We come to found out that we need to implement aiortc in order to gain access to browser camera so we can relay it to the backend.
#### Matching
One of the main challenges we ran into was delegating ID's to their respective ARUCO generated ones. A possible solution we came up with was renaming the user uploaded files to match their ARUCO generated ones. Additionally, this helped deal with duplicates as we implemented a check for those.
#### Out of bounds
The way the detection matches the ARUCO with the ID is via a list. One of the earlier problems were due to ARUCO codes being misinterpreted for different ones, causing it to go out of bounds because it was accessing an ID/Image that didn't exist. We can solve this by changing the list implementation into a hash/dict, or add metadata/tupled info into the image. For now, we made a simple logical check by checking if in bounds and if not just to display the base ID/default.
#### Standalone to Django
Implementing OpenCV into Django was quite the task. It required implementing multithreading and constant updates to video stream unlike a standalone py app. Thus it also results in a lower framerate. We are unsure of what fixes we could add, but this is one of our bigger challenges so far. Additionally, modifying camera data would result in nothing happening or completely breaking the server with no error messages.

## Accomplishments that we're proud of
We're proud that it manages to work; the user upload, verification, and camera to a varying degree. It is still somewhat buggy and not up to standard; there's a lot of room for improvements and modifications to increase speed, user accessibility, security, and overall design. However, this is a good start we're proud of.

## What we learned
We learned how to utilize OpenCV and web frameworks to create an ARUCO detector and image transposer. Additionally, we learned how to implement it into web services rather than a standalone python application with things like multithreadding. We also learned how host our code on a Heroku/AWS Lightsail. 

## What's next for AR Info
- Better Security Implementation of Twilio
- UI/UX Design
- Modifications to Camera for better framerate
- Multiple image/object transpose on ARUCO
- Calibration
- Implement AIORTC
- Autoangle adjustment on image

## Members
- Robin Lee Simpson | @TeachMeTW | Backend/OpenCV
- Yuheon Joh (John J Doe) | @leyuheon | FrontEnd/User
