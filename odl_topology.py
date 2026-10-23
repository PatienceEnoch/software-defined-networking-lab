import getpass
import requests

# OpenDaylight RESTCONF API
url = "http://localhost:8182/restconf/data/network-topology:network-topology?content=nonconfig"

# Ask for the password securely
password = getpass.getpass("OpenDaylight password: ")

# Send an HTTP GET request
response = requests.get(
    url,
    auth=("admin", password),
    headers={"Accept": "application/yang-data+json"},
    timeout=10
)

# Check for HTTP errors
response.raise_for_status()

# Convert the JSON response into Python data
data = response.json()

# Find the switches and their ports
topologies = data["network-topology:network-topology"]["topology"]

for topology in topologies:
    for node in topology.get("node", []):
        print("Switch:", node["node-id"])
        print("Ports:", len(node.get("termination-point", [])))

# Retrieve OpenFlow table 0
flow_url = (
    "http://localhost:8182/restconf/data/opendaylight-inventory:nodes/"
    "node=openflow%3A187176127603778/"
    "flow-node-inventory:table=0?content=nonconfig"
)

flow_response = requests.get(
    flow_url,
    auth=("admin", password),
    headers={"Accept": "application/yang-data+json"},
    timeout=10
)

flow_response.raise_for_status()
tables = flow_response.json().get("flow-node-inventory:table", [])

print("\nOpenFlow Rules:")
for table in tables:
    for flow in table.get("flow", []):
        print("Flow ID:", flow["id"])
        print("Priority:", flow["priority"])
        print("Incoming port:", flow.get("match", {}).get("in-port"))

        instructions = flow.get("instructions", {}).get("instruction", [])
        for instruction in instructions:
            actions = instruction.get("apply-actions", {}).get("action", [])
            for action in actions:
                output = action.get("output-action", {}).get("output-node-connector")
                if output:
                    print("Output port:", output)

        print("---")

# Display traffic statistics for each flow
print("\nFlow Traffic Statistics:")

for table in tables:
    for flow in table.get("flow", []):
        stats = flow.get(
            "opendaylight-flow-statistics:flow-statistics", {}
        )

        print(f"Flow ID: {flow['id']}")
        print(f"Packets: {stats.get('packet-count', 'N/A')}")
        print(f"Bytes: {stats.get('byte-count', 'N/A')}")
        print("---")
