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

void GPIO_One(int Gpio) {
    FILE *bright;
    bright = fopen("/sys/class/leds/m1_high/brightness", "w");
    fseek(bright, 0, SEEK_SET);
    fprintf(bright, "%d", 1 * Gpio);
    fclose(bright);
}

void setupPWM(int enable) {
    FILE *pwm;
    pwm = fopen("/dev/beagle/pwm/P9_16/enable", "w");
    fseek(pwm, 0, SEEK_SET);
    fprintf(pwm, "%d", 1 * enable);
    fclose(pwm);
}

void setupPeriod(int period_one) {
    FILE *period;
    period = fopen("/dev/beagle/pwm/P9_16/period", "w");
    fseek(period, 0, SEEK_SET);
    fprintf(period, "%d", 10 * period_one);
    fclose(period);
}

void pwm_duty(int the_duty_multiplier) {
    FILE *duty;
    duty = fopen("/dev/beagle/pwm/P9_16/duty_cycle", "w");
    fseek(duty, 0, SEEK_SET);
    fprintf(duty, "%d", 100 * the_duty_multiplier);
    fclose(duty);
}

int testInteger = 0;

int main() {
    printf("Setting up\n");
    setupPWM(0);

    while(1) {
        printf("Enter an integer, Please: ");
        scanf("%d", &testInteger);
        if (testInteger >= 10) {
            setupPWM(1);
            setupPeriod(140);
            pwm_duty(10);
            GPIO_One(1);
        }
        usleep(2500);

        if (testInteger < 2) {
            setupPWM(1);
            setupPeriod(250);
            pwm_duty(0);
            GPIO_One(1);
        }

        usleep(2500);
    }
    pwm_duty(0);
    return 0;
}
