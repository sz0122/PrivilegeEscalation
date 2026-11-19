/* libbackup.so - the shared library resolved from the writable RPATH dir */
#include <stdio.h>

int backup_run(void)
{
    printf("[libbackup] performing nightly backup\n");
    return 0;
}
