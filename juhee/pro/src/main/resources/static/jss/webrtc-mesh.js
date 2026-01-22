document.addEventListener('DOMContentLoaded', () => {
    const host = window.location.host;
    const socket = new WebSocket(`ws://${host}/signal`);

    let localStream;
    let peerConnection;
    let dataChannel;

    const rtcConfig = {
        iceServers: [{ urls: 'stun:stun.l.google.com:19302' }]
    };

    // [통합 기능] 도움 요청 버튼 (USER 전용)
    const startBtn = document.getElementById('startBtn');
    if (startBtn && MY_ROLE === "USER") {
        startBtn.onclick = async () => {
            try {
                // 1. 화면 공유 팝업 띄우기 (현재 탭 선택 유도)
                localStream = await navigator.mediaDevices.getDisplayMedia({
                    video: { cursor: "always" },
                    audio: true,
                    selfBrowserSurface: "include"
                });

                console.log("1. 화면 스트림 획득 성공");

                // 2. PeerConnection 생성 및 호출 시작
                const pc = createPeerConnection();
                const offer = await pc.createOffer();
                await pc.setLocalDescription(offer);

                // 3. 시그널링 전송
                socket.send(JSON.stringify({ type: 'offer', sdp: offer }));

                startBtn.innerText = "보호자 연결 중...";
                startBtn.style.backgroundColor = "#ff9900";

            } catch (e) {
                console.error("연결 에러:", e);
                alert("화면 공유가 필요합니다.");
            }
        };
    }

    function createPeerConnection() {
        if (peerConnection) return peerConnection;

        peerConnection = new RTCPeerConnection(rtcConfig);

        // GUARDIAN일 때만 데이터 채널 생성
        if (MY_ROLE === "GUARDIAN") {
            dataChannel = peerConnection.createDataChannel("remoteControl");
            setupDataChannel(dataChannel);
        }

        // USER는 GUARDIAN이 만든 채널을 수신
        peerConnection.ondatachannel = (event) => {
            dataChannel = event.channel;
            setupDataChannel(dataChannel);
        };

        // USER의 스트림을 연결에 추가
        if (MY_ROLE === "USER" && localStream) {
            localStream.getTracks().forEach(track => peerConnection.addTrack(track, localStream));
        }

        // GUARDIAN이 스트림을 받아 비디오 태그에 연결
        peerConnection.ontrack = (event) => {
            const remoteVideosDiv = document.getElementById('remoteVideos');
            let remoteVideo = document.getElementById('remoteVideoTag');

            if (!remoteVideo && remoteVideosDiv) {
                remoteVideo = document.createElement('video');
                remoteVideo.id = 'remoteVideoTag';
                remoteVideo.autoplay = true;
                remoteVideo.playsinline = true;
                remoteVideo.style.width = "100%";
                if (MY_ROLE === "GUARDIAN") remoteVideo.onclick = sendClickCommand;
                remoteVideosDiv.appendChild(remoteVideo);
            }
            if (remoteVideo) remoteVideo.srcObject = event.streams[0];
        };

        peerConnection.onicecandidate = (event) => {
            if (event.candidate) {
                socket.send(JSON.stringify({ type: 'ice', candidate: event.candidate }));
            }
        };

        return peerConnection;
    }

    function setupDataChannel(channel) {
        channel.onopen = () => {
            console.log("데이터 채널 오픈됨");
            if (startBtn) startBtn.innerText = "보호자 연결 완료!";
        };
        channel.onmessage = (e) => {
            const data = JSON.parse(e.data);
            if (MY_ROLE === "USER" && data.type === 'click') {
                executeRemoteClick(data.x, data.y);
            }
        };
    }

    // 원격 클릭 실행 (USER)
    function executeRemoteClick(relX, relY) {
        const x = relX * window.innerWidth;
        const y = relY * window.innerHeight;
        const targetEl = document.elementFromPoint(x, y);
        if (targetEl) {
            targetEl.dispatchEvent(new MouseEvent('click', { view: window, bubbles: true, clientX: x, clientY: y }));
            showClickDot(x, y);
        }
    }

    function showClickDot(x, y) {
        const dot = document.createElement('div');
        dot.style.cssText = `position:fixed; left:${x-5}px; top:${y-5}px; width:10px; height:10px; background:red; border-radius:50%; z-index:9999; pointer-events:none;`;
        document.body.appendChild(dot);
        setTimeout(() => dot.remove(), 500);
    }

    // 클릭 좌표 전송 (GUARDIAN)
    function sendClickCommand(event) {
        if (dataChannel && dataChannel.readyState === "open") {
            const rect = event.target.getBoundingClientRect();
            const x = (event.clientX - rect.left) / rect.width;
            const y = (event.clientY - rect.top) / rect.height;
            dataChannel.send(JSON.stringify({ type: 'click', x: x, y: y }));
        }
    }

    // 시그널링 수신 처리
    socket.onmessage = async (event) => {
        const data = JSON.parse(event.data);
        if (data.type === 'offer' && MY_ROLE === "GUARDIAN") {
            const pc = createPeerConnection();
            await pc.setRemoteDescription(new RTCSessionDescription(data.sdp));
            const answer = await pc.createAnswer();
            await pc.setLocalDescription(answer);
            socket.send(JSON.stringify({ type: 'answer', sdp: answer }));
        } else if (data.type === 'answer' && peerConnection) {
            await peerConnection.setRemoteDescription(new RTCSessionDescription(data.sdp));
        } else if (data.type === 'ice' && peerConnection) {
            await peerConnection.addIceCandidate(new RTCIceCandidate(data.candidate));
        }
    };
});