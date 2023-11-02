# Security System

This is a system based on machine vision that can detect faces, QR codes, and car plates. It includes two apps for registering and detecting users. The app can be connected to a microcontroller.

## Components
* Registration App
* Detection App
* HTTP Server
* Socket Server
* *(Microcontroller Implementation Example)

## Types of users
* Admins (can regist other users)
* Operators (control the detection points)
* Users (can use detection points)

You can use the command `flet pack main.py --name Register --add-data "assets;assets" --icon assets\favicon.png` or `flet pack main.py --name Detector --add-data "assets;assets" --icon assets\favicon.png` to create new distributions of the apps. These commands should be run in the `clients/Register` or `clients/Detector` directories, respectively.