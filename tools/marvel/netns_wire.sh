#!/usr/bin/env bash
# Wire a network namespace for the home-line second egress (multi-IP crawl).
#
# A macvlan on wlp8s0 gives the namespace its own L2 identity on the home
# LAN: traffic from inside exits via the home gateway (192.168.1.1) -> home
# ISP public IP, completely separate from the NORDLYNX (CA) egress that the
# main namespace uses. Unprivileged processes in the main ns stay marked by
# NORDLYNX; this ns is not, so its crawler sees a different egress IP.
#
# Usage: sudo bash tools/marvel/netns_wire.sh [ns_name] [ns_ip] [gateway] [dev]
set -euo pipefail

NS="${1:-se_shard2}"
NS_IP="${2:-192.168.1.203}"
GATEWAY="${3:-192.168.1.1}"
DEV="${4:-mv2}"
PARENT="wlp8s0"

if ip netns list | grep -q "^${NS}[[:space:]]"; then
  echo "removing existing netns $NS"
  ip netns del "$NS"
fi
ip link del "$DEV" 2>/dev/null || true

ip netns add "$NS"
ip link add "$DEV" link "$PARENT" type macvlan mode bridge
ip link set "$DEV" netns "$NS"
ip netns exec "$NS" ip link set lo up
ip netns exec "$NS" ip addr add "$NS_IP"/24 dev "$DEV"
ip netns exec "$NS" ip link set "$DEV" up
ip netns exec "$NS" ip route add default via "$GATEWAY"

echo "netns '$NS' wired: $DEV (macvlan on $PARENT) ip=$NS_IP default via $GATEWAY"
echo "verify: sudo ip netns exec $NS curl -s --max-time 15 https://api.ipify.org"