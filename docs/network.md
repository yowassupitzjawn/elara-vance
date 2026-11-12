# Network

VLANs, the switch, and what lives where. Specs only.

## VLANs

| VLAN | Network | What lives here |
|---|---|---|
| VLAN00 | Primary LAN | WiFi / Eero APs and wireless devices |
| VLAN20 | Servers | Office, desktops, and servers |
| VLAN30 | Cameras | Cameras only — no gateway, airgapped |

Everything unlabeled on the switch is VLAN00.

## Switch port map

24-port Gb PoE smart switch, fw 2019. All GE ports are Access mode.

| Ports | Status |
|---|---|
| GE1–GE18 | Down (empty) |
| GE19, GE20, GE21 | Up (unlabeled, VLAN00) |
| GE22, GE23 | Up — Eero WiFi APs |
| GE24 | Up — Office02 |
| XG1 | Up — trunk to pfSense (10G) |
| XG2 | Up — Office01 (10G) |
| XG3, XG4 | Down (10G fiber, empty) |

8 of 28 ports in use.

## Emergency access

One pfSense port (OPT1) is kept as an emergency local access port:
plug a laptop in directly when there is no KVM.

## Cameras

No cameras are mounted or online yet. One camera is on a bench
test. VLAN30 is ready and waiting.
