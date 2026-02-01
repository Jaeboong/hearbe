const SERVER = {
  host: "192.168.0.28",
  port: 9000,
  path: "/hearbe/share",
  secure: false,
  config: {
    iceServers: [{ urls: "stun:stun.l.google.com:19302" }]
  }
};

const ui = {
  myIdInput: document.getElementById("myIdInput"),
  roomInput: document.getElementById("roomInput"),
  roleSelect: document.getElementById("roleSelect"),
  applyIdBtn: document.getElementById("applyIdBtn"),
  initPeerBtn: document.getElementById("initPeerBtn"),
  startMediaBtn: document.getElementById("startMediaBtn"),
  peerIdInput: document.getElementById("peerIdInput"),
  callBtn: document.getElementById("callBtn"),
  hangupBtn: document.getElementById("hangupBtn"),
  screenShareBtn: document.getElementById("screenShareBtn"),
  myIdLabel: document.getElementById("myIdLabel"),
  connLabel: document.getElementById("connLabel"),
  myVideo: document.getElementById("myVideo"),
  remoteVideo: document.getElementById("remoteVideo"),
  logBox: document.getElementById("logBox")
};

let peer = null;
let myStream = null;
let screenStream = null;
let currentCall = null;

function log(message) {
  const ts = new Date().toLocaleTimeString();
  ui.logBox.textContent = `[${ts}] ${message}\n` + ui.logBox.textContent;
}

function setConnLabel(value) {
  ui.connLabel.textContent = value;
}

function getOutgoingStream() {
  return screenStream || myStream;
}

async function startMedia() {
  if (myStream) {
    return myStream;
  }
  try {
    myStream = await navigator.mediaDevices.getUserMedia({
      video: true,
      audio: true
    });
    ui.myVideo.srcObject = myStream;
    log("Local media started");
    return myStream;
  } catch (err) {
    log(`Media error: ${err.message || err}`);
    throw err;
  }
}

function attachCallHandlers(call) {
  currentCall = call;
  setConnLabel(`in-call (${call.peer})`);

  call.on("stream", (remoteStream) => {
    ui.remoteVideo.srcObject = remoteStream;
    log("Remote stream received");
  });

  call.on("close", () => {
    log("Call closed");
    setConnLabel("idle");
    ui.remoteVideo.srcObject = null;
    currentCall = null;
  });

  call.on("error", (err) => {
    log(`Call error: ${err.message || err}`);
  });
}

async function answerCall(call) {
  if (!myStream && !screenStream) {
    await startMedia();
  }
  attachCallHandlers(call);
  call.answer(getOutgoingStream());
  log(`Answered call from ${call.peer}`);
}

function initPeer() {
  const customId = ui.myIdInput.value.trim();
  if (peer) {
    peer.destroy();
    peer = null;
  }

  peer = new Peer(customId || undefined, SERVER);

  peer.on("open", (id) => {
    ui.myIdLabel.textContent = id;
    setConnLabel("open");
    log(`Peer open: ${id}`);
  });

  peer.on("call", (call) => {
    log(`Incoming call from ${call.peer}`);
    answerCall(call);
  });

  peer.on("disconnected", () => {
    setConnLabel("disconnected");
    log("Peer disconnected");
  });

  peer.on("close", () => {
    setConnLabel("closed");
    log("Peer closed");
  });

  peer.on("error", (err) => {
    log(`Peer error: ${err.message || err}`);
  });
}

async function callUser() {
  if (!peer) {
    log("Init peer first");
    return;
  }
  const peerId = ui.peerIdInput.value.trim();
  if (!peerId) {
    log("Enter peer ID to call");
    return;
  }
  if (!myStream && !screenStream) {
    await startMedia();
  }
  const call = peer.call(peerId, getOutgoingStream());
  attachCallHandlers(call);
  log(`Calling ${peerId}...`);
}

function hangup() {
  if (currentCall) {
    currentCall.close();
  }
}

async function replaceVideoTrack(newTrack) {
  if (!currentCall) {
    return;
  }
  const pc = currentCall.peerConnection || currentCall._pc;
  if (!pc) {
    log("PeerConnection not available for track replace");
    return;
  }
  const sender = pc.getSenders().find((s) => s.track && s.track.kind === "video");
  if (!sender) {
    log("No video sender found");
    return;
  }
  try {
    await sender.replaceTrack(newTrack);
    log("Video track replaced");
  } catch (err) {
    log(`replaceTrack error: ${err.message || err}`);
  }
}

async function startScreenShare() {
  if (screenStream) {
    stopScreenShare();
    return;
  }
  try {
    const stream = await navigator.mediaDevices.getDisplayMedia({
      video: { cursor: "always" },
      audio: false
    });
    screenStream = stream;
    ui.myVideo.srcObject = stream;
    ui.screenShareBtn.textContent = "Stop Screen Share";

    const track = stream.getVideoTracks()[0];
    track.onended = () => stopScreenShare();
    await replaceVideoTrack(track);

    log("Screen share started");
  } catch (err) {
    log(`Screen share error: ${err.message || err}`);
  }
}

function stopScreenShare() {
  if (!screenStream) {
    return;
  }
  screenStream.getTracks().forEach((t) => t.stop());
  screenStream = null;
  ui.screenShareBtn.textContent = "Start Screen Share";
  if (myStream) {
    ui.myVideo.srcObject = myStream;
    const track = myStream.getVideoTracks()[0];
    if (track) {
      replaceVideoTrack(track);
    }
  }
  log("Screen share stopped");
}

function applyRoomRole() {
  const room = ui.roomInput.value.trim();
  const role = ui.roleSelect.value;
  if (!room) {
    log("Enter room number");
    return;
  }
  const myId = `room-${room}-${role}`;
  ui.myIdInput.value = myId;

  const peerRole = role === "host" ? "guest" : "host";
  ui.peerIdInput.value = `room-${room}-${peerRole}`;

  log(`IDs set: me=${myId}, peer=${ui.peerIdInput.value}`);
}

ui.applyIdBtn.addEventListener("click", applyRoomRole);
ui.initPeerBtn.addEventListener("click", initPeer);
ui.startMediaBtn.addEventListener("click", startMedia);
ui.callBtn.addEventListener("click", callUser);
ui.hangupBtn.addEventListener("click", hangup);
ui.screenShareBtn.addEventListener("click", startScreenShare);

window.addEventListener("beforeunload", () => {
  if (peer) {
    peer.destroy();
  }
  if (myStream) {
    myStream.getTracks().forEach((t) => t.stop());
  }
  if (screenStream) {
    screenStream.getTracks().forEach((t) => t.stop());
  }
});

log(`Server: ${SERVER.host}:${SERVER.port}${SERVER.path}`);
