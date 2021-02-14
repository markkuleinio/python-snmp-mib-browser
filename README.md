# python-snmp-mib-browser
Small program to show MIB file OIDs in a list.

Example:

```
$ python3 mib-browser.py IPV6-MIB
.1 = (root)::iso
.1.3 = SNMPv2-SMI::org
.1.3.6 = SNMPv2-SMI::dod
.1.3.6.1 = SNMPv2-SMI::internet
.1.3.6.1.1 = SNMPv2-SMI::directory
.1.3.6.1.2 = SNMPv2-SMI::mgmt
.1.3.6.1.2.1 = SNMPv2-SMI::mib-2
.1.3.6.1.2.1.10 = SNMPv2-SMI::transmission
.1.3.6.1.2.1.55 = IPV6-MIB::ipv6MIB
.1.3.6.1.2.1.55.1 = IPV6-MIB::ipv6MIBObjects
.1.3.6.1.2.1.55.1.1 = IPV6-MIB::ipv6Forwarding
.1.3.6.1.2.1.55.1.2 = IPV6-MIB::ipv6DefaultHopLimit
.1.3.6.1.2.1.55.1.3 = IPV6-MIB::ipv6Interfaces
.1.3.6.1.2.1.55.1.4 = IPV6-MIB::ipv6IfTableLastChange
.1.3.6.1.2.1.55.1.5 = IPV6-MIB::ipv6IfTable
...
```

It tries to load all the necessary MIBs (based on the `IMPORTS` statements
in the MIBs) to show the full tree to the MIB requested in the command line.

By default the MIB files are read from `/var/lib/snmp/mibs` (and its subdirectories). You
can use the `-a` (`--add`) argument to add comma-separated list of other directories
(and their subdirectories!) to the search path, and use `-n` argument to skip the
default path altogether.

Note that the file parser actually reads **all** the files in the given (sub)directories
to find the MIB files, so don't try it with a root directory or something else
with many unnecessary or large files.

Example where the vendor-specific MIBs are found in a separate directory:

```
$ ls /home/markku/mibs
CISCO-BGP4-MIB.my  CISCO-SMI.my

$ python3 mib-browser.py CISCO-BGP4-MIB
MIB 'CISCO-BGP4-MIB' not found
.1 = (root)::iso

$ python3 mib-browser.py CISCO-BGP4-MIB -a /home/markku/mibs
.1 = (root)::iso
.1.3 = SNMPv2-SMI::org
.1.3.6 = SNMPv2-SMI::dod
.1.3.6.1 = SNMPv2-SMI::internet
...
.1.3.6.1.4.1.9.9.187 = CISCO-BGP4-MIB::ciscoBgp4MIB
.1.3.6.1.4.1.9.9.187.0 = CISCO-BGP4-MIB::ciscoBgp4NotifyPrefix
.1.3.6.1.4.1.9.9.187.0.1 = CISCO-BGP4-MIB::cbgpFsmStateChange
.1.3.6.1.4.1.9.9.187.0.2 = CISCO-BGP4-MIB::cbgpBackwardTransition
.1.3.6.1.4.1.9.9.187.0.3 = CISCO-BGP4-MIB::cbgpPrefixThresholdExceeded
.1.3.6.1.4.1.9.9.187.0.4 = CISCO-BGP4-MIB::cbgpPrefixThresholdClear
...
```

Errors will be output if all the necessary MIBs cannot be loaded, for example
(the default search path is here disabled with `-n`):

```
$ python3 mib-browser.py CISCO-BGP4-MIB -n -a /home/markku/mibs
MIB 'SNMPv2-SMI' not found
MIB 'SNMPv2-CONF' not found
MIB 'SNMPv2-TC' not found
MIB 'INET-ADDRESS-MIB' not found
MIB 'SNMP-FRAMEWORK-MIB' not found
MIB 'BGP4-MIB' not found
Missing input: MIB file for SNMPv2-SMI is needed for resolving "cisco = { enterprises 9 }" (and others in the same tree)
.1 = (root)::iso
```

Note that the MIB file parsing is not done in any structural way but just by trial and error,
so unexpected file syntax will cause problems in parsing.
