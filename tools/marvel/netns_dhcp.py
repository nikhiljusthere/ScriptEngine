#!/usr/bin/env python3
"""Minimal DHCP client for a network namespace (no dhclient/udhcpc on this box).

Run as root inside the namespace:
    sudo ip netns exec se_shard2 python3 tools/marvel/netns_dhcp.py mv2

Does DISCOVER -> REQUEST -> ACK on the given interface, prints the lease as
JSON on stdout, and (when run as root) applies it: replaces the interface
address with the lease and sets the default route via the router. A successful
lease means the interface now has a router-NAT-able source IP.
"""

import json
import random
import socket
import struct
import subprocess
import sys
import time

CLIENT_PORT = 68
SERVER_PORT = 67
BROADCAST = "255.255.255.255"
ZERO4 = b"\x00\x00\x00\x00"


def mac_of(iface: str) -> bytes:
    with open(f"/sys/class/net/{iface}/address", encoding="utf-8") as fh:
        return bytes.fromhex(fh.read().strip().replace(":", ""))


def dhcp_header(op: int, xid: int, secs: int, flags: int,
                ciaddr: bytes, chaddr: bytes) -> bytes:
    """Fixed 236-byte DHCP packet prefix: header + sname + file + magic."""
    head = struct.pack(
        "!BBBBIHH4s4s4s16s",
        op, 1, 6, 0, xid, secs, flags, ciaddr, ZERO4, ZERO4, chaddr.ljust(16, b"\x00"),
    )
    return head + b"\x00" * 128 + b"\x63\x82\x53\x63"


def options_bytes(opts: list[tuple[int, bytes]]) -> bytes:
    out = b""
    for code, payload in opts:
        out += bytes([code, len(payload)]) + payload
    return out + b"\xff"


def parse_options(data: bytes) -> dict:
    """Parse DHCP options starting at offset 236 of a full reply packet."""
    opts = data[236:]
    info: dict = {}
    i = 0
    while i < len(opts) and opts[i] != 255:
        code, length = opts[i], opts[i + 1]
        payload = opts[i + 2 : i + 2 + length]
        if code == 1:
            info["mask"] = socket.inet_ntoa(payload)
        elif code == 3:
            info["router"] = socket.inet_ntoa(payload[:4])
        elif code == 6:
            info["dns"] = socket.inet_ntoa(payload[4:8])
        elif code == 51:
            info["lease"] = struct.unpack("!I", payload)[0]
        elif code == 54:
            info["server_id"] = socket.inet_ntoa(payload[:4])
        i += 2 + length
    return info


def main() -> None:
    iface = sys.argv[1] if len(sys.argv) > 1 else "mv2"
    unicast_gw = None
    if len(sys.argv) > 2:
        unicast_gw = sys.argv[2]  # e.g. 192.168.1.1: skip the (broken-on-wifi)
                                  # broadcast and talk to the router directly
    xid = random.randint(1, 0x7FFFFFFF)
    chaddr = mac_of(iface)
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM, socket.IPPROTO_UDP)
    sock.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
    sock.bind(("0.0.0.0", CLIENT_PORT))
    sock.settimeout(4.0)

    def send(payload: bytes, dest: str) -> None:
        sock.sendto(payload, (dest, SERVER_PORT))

    def wait_reply(expect_op: int, seconds: float) -> dict | None:
        deadline = time.time() + seconds
        while time.time() < deadline:
            try:
                data, _ = sock.recvfrom(4096)
            except socket.timeout:
                break
            if len(data) < 240:
                continue
            reply_xid = struct.unpack("!I", data[4:8])[0]
            if reply_xid != xid or data[0] != expect_op:
                continue
            info = parse_options(data)
            info["ip"] = socket.inet_ntoa(data[16:20])
            return info
        return None

    flags = 0 if unicast_gw else 0x8000
    if unicast_gw:
        out = subprocess.run(f"ip -4 -o addr show dev {iface}", shell=True,
                             capture_output=True, text=True, check=True).stdout
        ciaddr = socket.inet_aton(out.split()[3].split("/")[0])
    else:
        ciaddr = ZERO4

    # --- DISCOVER ---
    packet = dhcp_header(1, xid, 0, flags, ciaddr, chaddr) + options_bytes([
        (53, b"\x01"),                    # DHCPDISCOVER
        (51, struct.pack("!I", 3600)),    # requested lease time
        (57, struct.pack("!H", 1500)),    # MTU
        (58, struct.pack("!H", 600)),     # T1
        (59, struct.pack("!H", 2400)),    # T2
        (12, b"se-shard2"),               # hostname
    ])
    send(packet, unicast_gw or BROADCAST)
    print(f"[dhcp] DISCOVER on {iface} -> {unicast_gw or 'broadcast'} (xid={xid:#x})", file=sys.stderr)
    offer = wait_reply(2, 12.0)
    if offer is None or offer["ip"] == "0.0.0.0":
        print(json.dumps({"error": "no DHCP offer received"}))
        sys.exit(1)
    print(f"[dhcp] OFFER ip={offer['ip']} server={offer.get('server_id')}", file=sys.stderr)

    # --- REQUEST (unicast to the server when known; reply comes as broadcast) ---
    req_opts: list[tuple[int, bytes]] = [
        (53, b"\x03"),                    # DHCPREQUEST
        (50, socket.inet_aton(offer["ip"])),
    ]
    if offer.get("server_id"):
        req_opts.append((54, socket.inet_aton(offer["server_id"])))
    packet = (
        dhcp_header(3, xid, 0, flags, ciaddr, chaddr)
        + options_bytes(req_opts)
    )
    send(packet, offer.get("server_id") or unicast_gw or BROADCAST)
    ack = wait_reply(5, 12.0)
    if ack is None:
        print(json.dumps({"error": f"no DHCP ACK (offer was {offer['ip']})"}))
        sys.exit(1)
    print(f"[dhcp] ACK ip={ack['ip']} via {ack.get('router')} dns={ack.get('dns')}", file=sys.stderr)

    lease = {
        "interface": iface,
        "ip": ack["ip"],
        "router": ack.get("router"),
        "dns": ack.get("dns"),
        "mask": ack.get("mask"),
        "lease_seconds": ack.get("lease", 3600),
    }

    # Apply the lease (root, inside the namespace).
    prefix = 24
    if lease.get("mask"):
        prefix = sum(bin(int(o)).count("1") for o in lease["mask"].split("."))
    subprocess.run(f"ip addr replace {lease['ip']}/{prefix} dev {iface}",
                   shell=True, check=True)
    if lease.get("router"):
        subprocess.run(f"ip route replace default via {lease['router']} dev {iface}",
                       shell=True, check=True)
    print(json.dumps(lease))


if __name__ == "__main__":
    main()