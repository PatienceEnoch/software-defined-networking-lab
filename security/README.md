# SDN Firewall Lab

## Objective
Implement centralized ICMP filtering using OpenDaylight,
Open vSwitch, OpenFlow, and RESTCONF.

## Network
- PC1: 192.168.10.1/24
- PC2: 192.168.10.2/24
- Controller: OpenDaylight
- Switch: openflow:187176127603778

## Firewall Policy
- Flow ID: 100
- Priority: 200
- Source: PC2 (192.168.10.2)
- Destination: PC1 (192.168.10.1)
- Protocol: ICMP
- Action: DROP

The firewall rule overrides the existing priority-100
forwarding rules for matching traffic.

## Configuration
The tested OpenFlow policy is stored in block-icmp.json.

## Test Results
- Before firewall: 5/5 pings successful.
- After firewall: 0/5 pings successful.
- Drop rule: 5 packets, 490 bytes.
- After rollback: 5/5 pings successful.

## Deployment
Install the rule using OpenDaylight RESTCONF with
an HTTP PUT request to table 0, flow 100.

## Rollback
Delete flow 100 using an HTTP DELETE request.

## Conclusion
Successfully demonstrated centralized security enforcement,
OpenFlow packet filtering, traffic monitoring, and rollback
in an isolated GNS3 environment.
