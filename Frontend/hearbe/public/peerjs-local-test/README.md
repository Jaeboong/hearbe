# PeerJS Local Test (LAN)

This folder contains a simple static page to test 1:1 video calls with PeerJS on your LAN.

## 1) Start PeerJS signaling server on the host (192.168.0.28)

```bash
docker pull peerjs/peerjs-server

docker run -d \
  --name dadab-peer \
  -p 9000:9000 \
  --restart always \
  peerjs/peerjs-server \
  --port 9000 --path /dadab-peer
```

## 2) Serve this folder as a static site

From this folder:

```bash
python -m http.server 3000
```

Then open:
- Host PC: http://localhost:3000
- Other PC: http://192.168.0.28:3000

## 3) How to use the page

1. Click `Start Camera/Mic` on both PCs.
2. Set `Room` and `Role`, then click `Apply room+role`.
3. Click `Init Peer` on both PCs.
4. On the guest PC, click `Call`.

## Notes

- If camera/mic is blocked on the non-localhost URL, Chrome may require a secure origin.
  Use the flag `chrome://flags/#unsafely-treat-insecure-origin-as-secure` and add
  `http://192.168.0.28:3000`, or serve via HTTPS.
- Screen share usually requires a secure origin (HTTPS or localhost).
- PeerJS server settings are hardcoded to `192.168.0.28:9000` with path `/dadab-peer` in `app.js`.
