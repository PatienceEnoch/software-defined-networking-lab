# SDN field notes

October–November 2026 · GNS3, OpenDaylight, Open vSwitch

I built this lab to see what happens between asking a controller to install a rule and watching a packet hit that rule. These notes follow the checks I used when the controller connection, the API request, and the forwarding result each needed their own explanation.

## Follow the controller connection first

In Lab 2, the switch briefly pointed at `192.168.42.183:6653` and the connection was refused. The working OpenDaylight address was `192.168.56.102:6653` on the host-only network. Restoring that target brought the OpenFlow session back. During host-only troubleshooting, I also used `tcpdump` to verify ARP replies.

I now check the management path in order. First I confirm the controller address and look for traffic on the management interface. Then I check whether OVS reports an active connection and whether the switch appears in OpenDaylight's operational inventory. Each check answers a different question. An ARP reply shows local address resolution, and an active OpenFlow session shows the switch reached the controller service.

## Read the API path as part of the configuration

OpenDaylight returned HTTP 409 while I was working on the firewall rule. I corrected the flow resource path under the switch node to use `flow-node-inventory:table=0/flow=100`. Once the request was accepted, I checked the operational flow and then inspected table 0 on OVS.

Rebuilding the topology also gave me a different switch datapath ID. Lab 1 appeared as `openflow:187176127603778`, while Lab 2 appeared as `openflow:125423032627785`. The hosts kept the same IPs. Checking inventory before submitting a write tells me which switch the script will actually address. See the [topology reader](../odl_topology.py) and the [Lab 2 firewall script](../sdn_firewall_lab2.py).

## Explain the failed ping with switch evidence

Before installing the rule, PC2 received all five ping replies from PC1. The two priority-100 entries in table 0 forwarded traffic between the host ports. I added flow 100 at priority 200 to match IPv4 ICMP from PC2 to PC1 and drop it.

| Check | Recorded observation |
| --- | --- |
| PC2 ping before the policy | 5 of 5 replies |
| PC2 ping with the policy | 0 of 5 replies |
| OVS counter for the drop entry | 5 packets, 490 bytes |
| PC2 ping after removal | 5 of 5 replies |

I used `ofproto/trace` to inspect which rule a matching packet would select. The flow counter showed that real test packets hit the drop entry. Testing again after removal showed that the original forwarding path was usable. See the [recorded firewall test](../security/README.md) and the [policy JSON](../security/block-icmp.json).

## Checks I would run again

| Where | What I look for |
| --- | --- |
| Switch management interface | The expected controller address and an active OpenFlow connection |
| OpenDaylight operational inventory | The expected datapath ID and table 0 entries |
| Open vSwitch flow table | The matching fields, priority, action, and packet counter |
| VPCS console | Traffic behavior before the change, with the rule installed, and after rollback |

My usual switch-side checks are `ovs-vsctl --columns=target,is_connected list Controller` and `ovs-ofctl -O OpenFlow13 dump-flows br0`. The [main lab README](../README.md) has the full demo sequence. The recorded restart check covered OVS. Controller VM restart and full-lab recovery still need their own tests.
