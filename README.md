# python-snmp-mib-browser
Small program to show MIB file OIDs in a list

Example:

```
$ cat /var/lib/snmp/mibs/ietf/SNMPv2-SMI /var/lib/snmp/mibs/ietf/IPV6-MIB | python3 mib-browser.py
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
.1.3.6.1.2.1.55.1.5.1 = IPV6-MIB::ipv6IfEntry
.1.3.6.1.2.1.55.1.5.1.1 = IPV6-MIB::ipv6IfIndex
.1.3.6.1.2.1.55.1.5.1.2 = IPV6-MIB::ipv6IfDescr
.1.3.6.1.2.1.55.1.5.1.3 = IPV6-MIB::ipv6IfLowerLayer
.1.3.6.1.2.1.55.1.5.1.4 = IPV6-MIB::ipv6IfEffectiveMtu
.1.3.6.1.2.1.55.1.5.1.5 = IPV6-MIB::ipv6IfReasmMaxSize
.1.3.6.1.2.1.55.1.5.1.6 = IPV6-MIB::ipv6IfIdentifier
...
```

Depending on the MIB file contents/dependencies you may need to find several files to read before
your actual MIB file you are interested in (check the `IMPORTS ... FROM <mibname>` statements
in the beginning of the MIB files). `SNMPv2-SMI` is always needed as it contains the first
levels from the root (iso.org.dod.internet) as well as other commonly needed items.

Also note that parsing is not done in any structural way but just by trial and error.
