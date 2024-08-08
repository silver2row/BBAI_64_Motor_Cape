// Differences from Sean J. Miller on element14
// Since its conception, the links have changed and have since been lost!

#include <stdio.h>
#include <unistd.h>
// #include <gpiod.h>
#include <stdlib.h>
#include <fcntl.h>
#include <sys/types.h>
#include <sys/stat.h>
#include <errno.h>

#define BRIGHT 1
#define ENABLE 1
#define DUTY   (2 / 20) * 100
#define PERIOD 1000

int bright = 0;
int enable = 0;
int duty   = 0;
int period = 0;

void setup_GPIO_One() {
    fd bright = open("/sys/class/leds/m1_high/brightness", O_WRONLY);
    if (fd == -1) {
        perror("Unable to open");
        exit(1);
    }
}

void setupPWM() {
    enable = open("/dev/beagle/pwm/P9_16/enable", O_WRONLY);
    if (enable == -1) {
        perror("Unable to open");
        exit(1);
    }
}

void setupPWM_Period() {
    period = open("/dev/beagle/pwm/P9_16/period", O_WRONLY);
    if (period == -1) {
        perror("Unable to open");
        exit(1);
    }
}

void pwm_duty() {
    duty = open("/dev/beagle/pwm/P9_16/duty_cycle", O_WRONLY);
    if (duty == -1) {
        perror("Um...cannot open?");
        exit(1);
    }
}

int main() {
    printf("Setting up\n");
    setupPWM();
    setup_GPIO_One();
    setupPWM_Period();
    pwm_duty();

    for (int i = 0; i < 20; i++) {
        if (write(bright, "1", 1) != 1) {
            PERIOD;
            DUTY;
            ENABLE;
            perror("Error");
            exit(1);
        }

        usleep(500000);

        if (write(bright, "0", 1) != 1) {
            PERIOD;
            DUTY;
            ENABLE;
            perror("Error");
            exit(1);
        }

        usleep(500000);
    }
    close(bright);
    pwm_duty(0);
    return 0;
}
