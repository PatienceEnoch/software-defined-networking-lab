import getpass
import requests

# OpenDaylight controller
BASE_URL = "http://localhost:8182/restconf/data"
SWITCH_ID = "openflow%3A125423032627785"
FLOW_ID = "100"

FLOW_URL = (
    f"{BASE_URL}/opendaylight-inventory:nodes/"
    f"node={SWITCH_ID}/"
    f"flow-node-inventory:table=0/flow={FLOW_ID}"
)

import sys

# Validate command before contacting OpenDaylight
if len(sys.argv) != 2 or sys.argv[1] not in ("check", "install", "remove"):
    print("Usage: python3 sdn_firewall.py {check|install|remove}")
    sys.exit(1)

password = getpass.getpass("OpenDaylight password: ")

def check_firewall():
    """Check the firewall rule in OpenDaylight."""
    response = requests.get(
        FLOW_URL + "?content=nonconfig",
        auth=("admin", password),
        headers={"Accept": "application/yang-data+json"},
        timeout=10
    )

    if response.status_code == 200:
        print("Firewall rule exists in operational data.")
        print(response.json())
    elif response.status_code in (404, 409):
        try:
            errors = response.json().get("errors", {}).get("error", [])
        except ValueError:
            errors = []

        if response.status_code == 404 or any(
            error.get("error-tag") == "data-missing"
            for error in errors
        ):
            print("Firewall rule is not present in operational data.")
        else:
            print(f"OpenDaylight returned HTTP {response.status_code}")
            print(response.text)
    else:
        print(f"OpenDaylight returned HTTP {response.status_code}")
        print(response.text)

def install_firewall():
    """Install the ICMP blocking policy through RESTCONF."""

    # Check whether flow 100 already exists
    check = requests.get(
        FLOW_URL,
        auth=("admin", password),
        headers={"Accept": "application/yang-data+json"},
        timeout=10
    )

    if check.status_code == 200:
        print("Flow 100 already exists. Installation cancelled.")
        return

    if check.status_code != 404:
        try:
            errors = check.json().get("errors", {}).get("error", [])
        except ValueError:
            errors = []

        if not any(e.get("error-tag") == "data-missing" for e in errors):
            check.raise_for_status()
            raise RuntimeError("Unable to verify that flow 100 is absent.")

    # Load our previously tested firewall configuration
    with open("security/block-icmp.json") as file:
        policy = file.read()

    # Send the policy to OpenDaylight
    response = requests.put(
        FLOW_URL,
        data=policy,
        auth=("admin", password),
        headers={
            "Content-Type": "application/yang-data+json",
            "Accept": "application/yang-data+json"
        },
        timeout=10
    )

    response.raise_for_status()
    print("Firewall installation request accepted by OpenDaylight.")

def remove_firewall():
    """Remove firewall rule 100 through RESTCONF."""

    response = requests.delete(
        FLOW_URL,
        auth=("admin", password),
        headers={"Accept": "application/yang-data+json"},
        timeout=10
    )

    if response.status_code in (200, 204):
        print("Firewall removal request accepted.")
    else:
        response.raise_for_status()
        print(f"Unexpected response: HTTP {response.status_code}")

if __name__ == "__main__":
    import sys

    if len(sys.argv) != 2:
        print("Usage: python3 sdn_firewall.py install")
        sys.exit(1)

    command = sys.argv[1]

    if command == "check":
        check_firewall()
    elif command == "install":
        install_firewall()
    elif command == "remove":
        remove_firewall()
    else:
        print(f"Unknown command: {command}")
        sys.exit(1)

