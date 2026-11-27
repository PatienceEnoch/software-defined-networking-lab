# SDN field notes

October–November 2026 · GNS3, OpenDaylight, Open vSwitch

I wanted to see what happened after I sent a flow rule to OpenDaylight. The firewall test gave me a way to follow that change all the way to the switch and see what it did to a ping.

## The switch was calling the wrong address

In Lab 2, OVS was trying to reach `192.168.42.183:6653` and getting a connection refusal. I pointed it back at `192.168.56.102:6653`, the OpenDaylight address on the host-only network, and the OpenFlow session came back.

While troubleshooting the host-only network, I used `tcpdump` to look for ARP replies. Seeing a reply told me address resolution was working. To see whether the switch had actually connected to OpenDaylight, I checked `ovs-vsctl --columns=target,is_connected list Controller` and looked for the switch in OpenDaylight's inventory.

## The RESTCONF request came back with a 409

I was trying to install the firewall rule when OpenDaylight returned HTTP 409. The fix was in the URL. I changed the path under the switch node to `flow-node-inventory:table=0/flow=100`. Once the request went through, I looked for the flow in OpenDaylight's operational inventory and then checked table 0 on OVS.

The two labs used the same PC addresses, but the switch had a different ID in each one. Lab 1 used `openflow:187176127603778` and Lab 2 used `openflow:125423032627785`. That’s why I check the node ID before running a firewall script. The [topology reader](../odl_topology.py) lists the discovered nodes, and the [Lab 2 script](../sdn_firewall_lab2.py) shows where the ID goes in the request.

## The ping timed out. The counter told me why.

PC2 could ping PC1 before I made the change. Two priority-100 rules in table 0 forwarded traffic between the host ports. I added flow 100 at priority 200 so it would match and drop IPv4 ICMP traveling from PC2 to PC1 before the forwarding rule could apply.

| Lab 1 check | What I saw |
| --- | --- |
| Ping before installing the rule | 5 of 5 replies |
| Ping with the rule installed | 0 of 5 replies |
| OVS drop counter | 5 packets, 490 bytes |
| Ping after removing the rule | 5 of 5 replies |

I used `ofproto/trace` to see which rule a matching packet would take. Then I checked `ovs-ofctl -O OpenFlow13 dump-flows br0` and saw five packets on the drop entry. When I removed the rule and ran the same ping again, all five replies came back. The [firewall test](../security/README.md) and [policy JSON](../security/block-icmp.json) are in the repo.

## Where I’d pick up next time

I’d start with the controller connection, confirm the switch ID in OpenDaylight, and look at the installed flow and its counter on OVS. Then I’d run the same ping before the change, with the rule in place, and after removing it. The [lab README](../README.md) has the commands in order.

I tested an OVS restart during the lab. Restarting the controller VM and recovering from a full lab shutdown are still open checks.
