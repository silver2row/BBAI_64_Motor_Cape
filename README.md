# BBAI_64_Motor_Cape

A Build for the Motor Cape and BBAI-64 from beagleboard.org

This machine, the BBAI-64, has a TDA4VM dual-core processor with other parts as coprocessors from TI.

There is ongoing development for this board still going on, e.g. circa `8/2024`.

I am building this method of ideas to help others get started with the BBAI-64, GPIO, PWM, and the Motor Cape.

```
1. First, install the image
2. The image is located here: There is also a newer image that one can find on beagleboard.org for the BBAI-64 (6.12.x)! 
   https://www.beagleboard.org/distros/bbai64-debian-12-6-2024-07-04-xfce
3. Use Balena Etcher or another flashing tool to put it on the micro SD Card, attach
   the micro SD Card to the cage on the BBAI-64,
   and then apply power
4. Boot and type in ssh debian@192.168.7.2
5. A USB C to USB C cable would be preferable in this instance
   for ssh communication and power 
6. On your development desktop, ssh into the board with passcode tmppwd
7. Clone this repo and look around or change things (my source is an ongoing affair)
8. sudo apt update && sudo apt upgrade
9. sudo apt-get dist-upgrade -yq
10. cd /opt/source/dtb-6.1-Beagle/ && git pull
11. ./build_n_install.sh
12. fdtoverlays /overlays/k3-j721e-beagleboneai64-BBORG_MOTOR.dtbo
    goes in /boot/firmware/extlinux/extlinux.conf

13. Use sudo to install the .dtbo file in /boot/firmware/extlinux/extlinux.conf
14. Use the shell script provided in the forums and/or this repo under scripts
15. This will ensure that the PWM outputs are available
16. sudo shutdown -h now
17. Attach the Motor Cape and attach PWR, GND, and a single phase motor
    to Motor1 on the headers of the Motor Cape
18. Apply power to your board and apply power to the Motor Cape
19. I use a variable Bench Supply PSU for testing
20. Also, during each boot, one will need to apply the shell script and/or 
    make a .service file for running on boot
21. Please view the photos of the Headers for accessing what pins
    do what to what connectors on the Motor Cape
22. Or, one can look in the source to understand what pins do what in
    b_script.c
23. Now, apply the sh set_up_pwm.sh command to instantiate the 
    pinmuxing of the PWM peripherals/outputs
24. gcc b_script -o b_script

25. That should compile or use your own source to fully captivate audiences
26. Then, ./b_script to run the binary that gcc has just produced
27. There should be a Red LED lit and the motor or locking solenoid, in my case, should move
28. If there is an issue or if you are not receiving movement, review the source
29. Change at will
```

All the steps can be found here: https://forum.beagleboard.org/t/how-can-i-use-the-motor-cape-in-bb-ai-64/38967/12

I think I have gone over what I read, and what I have learned, plus other ideas from researching ideas for the build.

Seth

P.S. Enjoy...and always, one can go to beagleboard.org to look over their builds, images, and boards. Also, I noticed
a forum and docs.beagleboard.org bunch of ideas for assistance in building around particular boards.

Here is also a page online where Capes are available: https://www.mouser.com/new/beagleboardorg/beaglebonecapes/

```
# Also
```

* WIP

```
a. Build a better bot!
b. Make the bot do something fascinating!
c. Repeat a. and b. until infinity!
```
