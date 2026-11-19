/*
 * backup-tool - a SUID root helper deployed by ops to run nightly backups.
 * It simply calls into libbackup.so, which is resolved through the run-time
 * search path (/opt/backup/lib). That directory is writable by the ops group.
 */
#include <stdio.h>
#include <stdlib.h>
#include <unistd.h>

int backup_run(void);

int main(int argc, char **argv)
{
    (void)argc;
    (void)argv;
    printf("[backup-tool] starting backup as uid=%d euid=%d\n", getuid(), geteuid());
    printf("[backup-tool] result: %d\n", backup_run());
    return 0;
}
