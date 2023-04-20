## Off-TD Debug

### Prepare for Debug Info

You can install `debuginfo` from the yum repository that provides the guest kernel debug info

```
sudo dnf install intel-mvp-tdx-kernel-debuginfo
```

or install the RPMs directly

```
cd <path to guest-kernel packages>
sudo dnf install intel-mvp-tdx-kernel-debuginfo-common-x86_64-<guest-kernel-version>.el8.x86_64.rpm \
intel-mvp-tdx-kernel-debuginfo-<guest-kernel-version>.el8.x86_64.rpm
```

After debug info installed, you can find debuggable modules in `/usr/lib/debug/usr/lib/modules/` and sources in `/usr/src/debug/`

### Start a Debuggable TD guest

Please use the qemu command to Launch TD guest via qemu-kvm and add below parameters.

- Append `debug=on` to `tdx-guest` to turn on debugging, like

```
-object tdx-guest,id=tdx,debug=on
```

- Add `-s -S` parameter to qemu-kvm to sets GDB stub server on localhost port 1234 and wait for connection from GDB to Qemu

- Append `nokaslr` to TD kernel command line to disable kernel address randomization

After that, the qemu process starts and waits for GDB connection.

```
/usr/libexec/qemu-kvm -s -S -accel kvm -monitor telnet:127.0.0.1:9001,server,nowait -object tdx-guest,id=tdx,debug=on -append "nokaslr ..." ...
char device redirected to /dev/pts/5 (label compat_monitor0)
```

### Connect to Qemu GDB Stub

On another console, set MOD_DIR in below script and run the script to start GDB

```bash
#!/usr/bin/env bash

GDB=gdb
MOD_DIR=/usr/lib/debug/usr/lib/modules/<guest kernel>/

$GDB \
-ex "add-auto-load-safe-path $MOD_DIR" \
-ex "file $MOD_DIR/vmlinux" \
-ex "set arch i386:x86-64:intel" \
-ex "set remotetimeout 360" \
-ex "target remote 127.0.0.1:1234"
```

Then the connection is established and GDB waits for you operation:

```
GNU gdb (GDB) Red Hat Enterprise Linux 8.2-18.el8
Copyright (C) 2018 Free Software Foundation, Inc.
License GPLv3+: GNU GPL version 3 or later <http://gnu.org/licenses/gpl.html>
This is free software: you are free to change and redistribute it.
There is NO WARRANTY, to the extent permitted by law.
Type "show copying" and "show warranty" for details.
This GDB was configured as "x86_64-redhat-linux-gnu".
Type "show configuration" for configuration details.
For bug reporting instructions, please see:
<http://www.gnu.org/software/gdb/bugs/>.
Find the GDB manual and other documentation resources online at:
    <http://www.gnu.org/software/gdb/documentation/>.

For help, type "help".
Type "apropos word" to search for commands related to "word".
Reading symbols from /usr/lib/debug/lib/modules/5.19.0-tdx.v1.9.mvp9.el8.x86_64/vmlinux...done.
The target architecture is assumed to be i386:x86-64:intel
Remote debugging using 127.0.0.1:1234
0x0000000000000000 in fixed_percpu_data ()
(gdb) hb start_kernel
Hardware assisted breakpoint 1 at 0xffffffff83d32d88: file init/main.c, line 929.
(gdb) hb rest_init
Hardware assisted breakpoint 2 at 0xffffffff8209d4b0: file init/main.c, line 681.
(gdb) continue
Continuing.

Breakpoint 1, start_kernel () at init/main.c:929
929     {
(gdb)
Continuing.

Breakpoint 2, rest_init () at init/main.c:681
681     {
(gdb) quit
A debugging session is active.

        Inferior 1 [process 1] will be detached.

Quit anyway? (y or n) y
Detaching from program: /usr/lib/debug/usr/lib/modules/5.19.0-tdx.v1.9.mvp9.el8.x86_64/vmlinux, process 1
Ending remote debugging.
[Inferior 1 (process 1) detached]

```

Please use `hb` command in GDB to set the first breakpoint, e.g. `hb start_kernel`.
Please note the software breakpoint is available after the kernel is loaded into GPA space by Qemu.

```
(gdb) hb start_kernel
Hardware assisted breakpoint 1 at 0xffffffff83d32d88: file init/main.c, line 929.
(gdb) hb rest_init
Hardware assisted breakpoint 2 at 0xffffffff8209d4b0: file init/main.c, line 681.
(gdb) continue
Continuing.

Breakpoint 1, start_kernel () at init/main.c:929
929     {
(gdb)
Continuing.

Breakpoint 2, rest_init () at init/main.c:681
681     {
(gdb)
```
