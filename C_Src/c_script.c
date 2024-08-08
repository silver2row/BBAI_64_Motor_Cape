#include <stdio.h>
#include <stdlib.h>
#include <unistd.h>
// #include <gpiod.h>

#define PWM_PERIOD 20000
#define DUTY_MIN   10000
#define DUTY_MAX   20000

void writeToFile(const char* path, int value) {
    FILE* file = fopen(path, "rw");
    if(file == NULL) {
        perror("Cannot open file...");
        printf("My integer is: %d\n", value);
        printf(path);
        exit(1);
    }
    fprintf(file, "%d", value);
    fclose(file);
}

int main() {
    writeToFile("/dev/beagle/pwm/P9_16/enable", 1);
    writeToFile("/dev/beagle/pwm/P9_16/period", PWM_PERIOD);
    writeToFile("/sys/class/leds/m1_high/brightness", 1);

    while(1) {
        writeToFile("/dev/beagle/pwm/P9_16/period", DUTY_MIN);
        writeToFile("/sys/class/leds/m1_high/brightness", 1);
        usleep(25000);

        writeToFile("/dev/beagle/pwm/P9_16/period", DUTY_MAX);
        writeToFile("/sys/class/leds/m1_high/brightness", 1);
        usleep(25000);

        writeToFile("/dev/beagle/pwm/P9_16/period", (DUTY_MIN + DUTY_MAX) / 2);
        writeToFile("/sys/class/leds/m1_high/brightness", 1);
        usleep(25000);
    }
    writeToFile("/dev/beagle/pwm/P9_16/enable", 0);
    writeToFile("/sys/class/leds/m1_high/brightness", 0);

    return 0;
}
