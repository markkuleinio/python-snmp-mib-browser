# python-snmp-mib-browser
Small program to show MIB file OIDs in a list

Example:

```
$ cat /var/lib/snmp/mibs/ietf/SNMPv2-SMI /var/lib/snmp/mibs/ietf/IPV6-MIB | python3 mib-browser.py
.1 = (unknown MIB)::iso
.1.3 = (unknown MIB)::org
.1.3.6 = (unknown MIB)::dod
.1.3.6.1 = (unknown MIB)::internet
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
your actual MIB file you are interested in. Also note that the parsing is not done in any structural
way but just by trial and error.
