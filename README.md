# Software Defined Networking lab

This is my software defined networking lab, built on 21 October 2026 with GNS3, Open vSwitch, OpenDaylight, OpenFlow 1.3, and RESTCONF. The setup is small: two VPCS hosts, one virtual switch, and a controller on a separate Ubuntu VM. I built it to get hands-on with controller-managed forwarding and see what it takes to keep the setup working after a restart.

Two PCs talking to each other sounds simple until you put yourself in charge of the packets.

## The setup

The checked in GNS3 project is `SDN-OpenFlow-Lab`. Its topology contains:

```text
PC1 (192.168.10.1/24) ─┐
                       ├─ OpenvSwitchmanagement-1 (br0 data plane)
PC2 (192.168.10.2/24) ─┘
                       └─ Cloud2/eth0 (host-side management attachment)
```

The project notes record the following management/control addresses:

| Component | Address / port |
| --- | --- |
| OpenDaylight controller VM | `192.168.56.102` |
| OVS management interface | `192.168.56.250` |
| OpenFlow controller connection | TCP `6653` |
| PC1 | `192.168.10.1/24` |
| PC2 | `192.168.10.2/24` |

The project file records GNS3 format `2.2.61` and the Docker image `gns3/openvswitch:latest`. The OpenDaylight VM and its controller data are external to this GNS3 project export.

## What works so far

My lab notes record a working controller to switch connection, bidirectional forwarding rules pushed with HTTP PUT requests and JSON, and successful traffic tests between the two hosts. They also record persistent OVS management networking, controller reconnection and flow restoration after an OVS restart, and a separate JSON backup of the rules.

These are results from the original lab session; I have not rerun the live checks for this README update. The original flow backup is not present in this checkout, so `examples/flow-rules.example.json` is a documentation template, not a claim that these exact flow IDs or port numbers were installed.

## RESTCONF and OpenFlow 1.3 workflow

Use the RESTCONF base path, port, credentials, and YANG path that match the OpenDaylight release installed in the controller VM. Older labs commonly use `/restconf/config/...` or `/rests/data/...` on port 8181; newer Netty deployments may use `/restconf/data/...` on port 8182. Do not mix these forms without checking the running controller.

Before declaring a rule active:

1. Confirm the controller's configured flow in the config datastore.
2. Confirm the switch and table in operational inventory.
3. Inspect the actual OpenFlow 1.3 port mapping with `ovs-ofctl -O OpenFlow13 show br0` or `ovs-vsctl --columns=name,ofport list Interface`.
4. Inspect installed entries with `ovs-ofctl -O OpenFlow13 dump-flows br0`.
5. Test both directions from the VPCS consoles (`ping 192.168.10.2` from PC1 and the reverse).

The example JSON uses the OpenFlow plugin's `flow-node-inventory:flow` wrapper and shows the shape of a bidirectional IPv4 rule. Replace the node ID, flow ID, priorities, match fields, and output ports with values read from the running lab.

## Save, persist, and recover

- In each VPCS console, run `save`; this writes the guest configuration to its `startup.vpc` file.
- Save the GNS3 project and stop all nodes before creating a project snapshot.
- Keep the GNS3 project directory, the external OpenDaylight VM, its controller configuration/persistence data, and the separate flow JSON backup together as one recovery set.
- OVSDB preserves bridge, port, and controller settings; it is separate from the OpenFlow flow table. After a daemon or VM restart, verify controller reconciliation and dump the flows again. `ovs-ctl restart` has its own flow save/restore behavior, so do not assume every restart has the same effect.
- A GNS3 project export may omit images and snapshots, and external VMware/VirtualBox nodes have portability limits. A VirtualBox snapshot is not a substitute for copying the VM and controller data.
- For recovery, start the controller using the method used by the original installation, verify its RESTCONF endpoint, reconnect the OVS controller, confirm inventory and installed flows, then repeat the two ping tests.

## Repository contents

The `gns3/` directory contains the project definition and VPCS startup files. No credentials, controller database, VM disk, or unverified flow dump is included.

## How to use this repo

Start with the topology file and the project notes if you want to inspect the saved lab. Read the validation notes before starting anything in GNS3. The controller VM, Docker image, credentials, and working flow backup are deliberately kept outside this repository, so opening the project file by itself will not recreate the whole lab.

## Next up

- Check what survives a controller restart and a full lab shutdown.
- Try a narrowly scoped traffic-blocking rule and verify both blocked and allowed traffic.
- Build Python automation for RESTCONF, starting with read-only requests.

## References

- [OpenDaylight OpenFlow operations](https://docs.opendaylight.org/projects/openflowplugin/en/latest/users/operation.html)
- [OpenDaylight flow examples](https://docs.opendaylight.org/projects/openflowplugin/en/latest/users/flow-examples.html)
- [Open vSwitch OpenFlow FAQ](https://docs.openvswitch.org/en/latest/faq/openflow/)
- [GNS3 VPCS documentation](https://docs.gns3.com/docs/emulators/vpcs)
- [GNS3 GUI and snapshots](https://docs.gns3.com/docs/using-gns3/beginners/the-gns3-gui)


