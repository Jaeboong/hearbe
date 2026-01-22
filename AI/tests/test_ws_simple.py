"""
WebSocket ASR Simple Test (No Microphone)

Usage:
    pip install websockets numpy
    python tests/test_ws_simple.py [--host localhost] [--port 8000]

Sends generated test audio to verify WebSocket connection and ASR pipeline.
"""

import asyncio
import argparse
import json
import base64
import sys

try:
    import websockets
except ImportError:
    print("Error: websockets not installed. Run: pip install websockets")
    sys.exit(1)

try:
    import numpy as np
except ImportError:
    print("Error: numpy not installed. Run: pip install numpy")
    sys.exit(1)


SAMPLE_RATE = 16000


def generate_test_audio(duration_sec: float = 1.0, tone_hz: float = 440.0) -> bytes:
    """Generate a simple sine wave tone as test audio."""
    samples = int(SAMPLE_RATE * duration_sec)
    t = np.linspace(0, duration_sec, samples, dtype=np.float32)

    # Generate sine wave
    audio_float = np.sin(2 * np.pi * tone_hz * t) * 0.3

    # Convert to 16-bit PCM
    audio_int16 = (audio_float * 32767).astype(np.int16)

    return audio_int16.tobytes()


def generate_silence(duration_sec: float = 1.0) -> bytes:
    """Generate silence as test audio."""
    samples = int(SAMPLE_RATE * duration_sec)
    audio_int16 = np.zeros(samples, dtype=np.int16)
    return audio_int16.tobytes()


async def test_connection(host: str, port: int):
    """Test basic WebSocket connection."""
    uri = f"ws://{host}:{port}/ws"

    print(f"1. Connecting to {uri}...")

    try:
        async with websockets.connect(uri) as ws:
            # Wait for connection message
            response = await asyncio.wait_for(ws.recv(), timeout=5.0)
            msg = json.loads(response)
            print(f"   Received: {msg['type']} - {msg.get('data', {}).get('message', '')}")

            if msg.get("type") == "status" and msg.get("data", {}).get("status") == "connected":
                print("   Connection successful!")
                return True
            else:
                print("   Unexpected response")
                return False

    except websockets.ConnectionRefused:
        print(f"   Error: Cannot connect to {uri}")
        print("   Make sure the server is running (docker-compose up)")
        return False
    except asyncio.TimeoutError:
        print("   Error: Timeout waiting for server response")
        return False
    except Exception as e:
        print(f"   Error: {e}")
        return False


async def test_audio_chunk(host: str, port: int):
    """Test sending audio chunk and receiving ASR result."""
    uri = f"ws://{host}:{port}/ws"

    print(f"\n2. Testing audio streaming to {uri}...")

    try:
        async with websockets.connect(uri) as ws:
            # Wait for connection
            response = await ws.recv()
            msg = json.loads(response)
            print(f"   Connected: {msg.get('data', {}).get('message', '')}")

            # Generate 1.5 seconds of silence (enough to trigger transcription)
            print("   Generating test audio (1.5s silence)...")
            audio_data = generate_silence(1.5)
            print(f"   Audio size: {len(audio_data)} bytes")

            # Send as single chunk with is_final=True
            message = {
                "type": "audio_chunk",
                "data": {
                    "audio": base64.b64encode(audio_data).decode("ascii"),
                    "seq": 1,
                    "is_final": True
                }
            }

            print("   Sending audio chunk (is_final=True)...")
            await ws.send(json.dumps(message))

            # Wait for ASR result
            print("   Waiting for ASR result...")

            try:
                while True:
                    response = await asyncio.wait_for(ws.recv(), timeout=30.0)
                    msg = json.loads(response)
                    msg_type = msg.get("type")
                    data = msg.get("data", {})

                    if msg_type == "asr_result":
                        print(f"\n   ASR Result received!")
                        print(f"   - Text: '{data.get('text', '')}'")
                        print(f"   - Confidence: {data.get('confidence', 0):.3f}")
                        print(f"   - Language: {data.get('language', '')}")
                        print(f"   - Duration: {data.get('duration', 0):.2f}s")
                        print(f"   - Is Final: {data.get('is_final', False)}")
                        print(f"   - Segment ID: {data.get('segment_id', '')}")
                        return True

                    elif msg_type == "error":
                        print(f"   Error: {data.get('error', '')}")
                        return False

                    else:
                        print(f"   Received: {msg_type}")

            except asyncio.TimeoutError:
                print("   Timeout waiting for ASR result")
                print("   This may indicate ASR service is not ready or model is loading")
                return False

    except Exception as e:
        print(f"   Error: {e}")
        return False


async def test_streaming(host: str, port: int):
    """Test streaming multiple chunks."""
    uri = f"ws://{host}:{port}/ws"

    print(f"\n3. Testing streaming mode to {uri}...")

    try:
        async with websockets.connect(uri) as ws:
            # Wait for connection
            response = await ws.recv()
            print("   Connected")

            # Generate 3 seconds of audio, send in 20ms chunks
            print("   Streaming 3 seconds of test audio in 20ms chunks...")

            chunk_samples = 320  # 20ms @ 16kHz
            chunk_bytes = chunk_samples * 2
            total_samples = SAMPLE_RATE * 3  # 3 seconds
            total_chunks = total_samples // chunk_samples

            audio_data = generate_silence(3.0)

            results = []

            # Background task to receive messages
            async def receiver():
                try:
                    while True:
                        response = await ws.recv()
                        msg = json.loads(response)
                        if msg.get("type") == "asr_result":
                            results.append(msg.get("data", {}))
                except asyncio.CancelledError:
                    pass

            recv_task = asyncio.create_task(receiver())

            # Send chunks
            for i in range(total_chunks):
                start = i * chunk_bytes
                end = start + chunk_bytes
                chunk = audio_data[start:end]

                is_final = (i == total_chunks - 1)

                message = {
                    "type": "audio_chunk",
                    "data": {
                        "audio": base64.b64encode(chunk).decode("ascii"),
                        "seq": i + 1,
                        "is_final": is_final
                    }
                }

                await ws.send(json.dumps(message))
                await asyncio.sleep(0.02)  # 20ms

                # Progress
                if (i + 1) % 50 == 0:
                    print(f"   Sent {i + 1}/{total_chunks} chunks...")

            print(f"   Sent all {total_chunks} chunks")

            # Wait for final result
            await asyncio.sleep(3.0)

            recv_task.cancel()
            try:
                await recv_task
            except asyncio.CancelledError:
                pass

            print(f"\n   Received {len(results)} ASR results:")
            for r in results:
                is_final = r.get("is_final", False)
                text = r.get("text", "")
                segment = r.get("segment_id", "")
                prefix = "[FINAL]" if is_final else "[PARTIAL]"
                print(f"   {prefix} {segment}: '{text}'")

            return True

    except Exception as e:
        print(f"   Error: {e}")
        import traceback
        traceback.print_exc()
        return False


async def main():
    parser = argparse.ArgumentParser(description="WebSocket ASR Simple Test")
    parser.add_argument("--host", default="localhost", help="Server host (default: localhost)")
    parser.add_argument("--port", type=int, default=8000, help="Server port (default: 8000)")
    parser.add_argument("--test", choices=["connection", "audio", "streaming", "all"],
                        default="all", help="Test to run")
    args = parser.parse_args()

    print("=" * 60)
    print("WebSocket ASR Test Suite")
    print("=" * 60)
    print()

    results = {}

    if args.test in ["connection", "all"]:
        results["connection"] = await test_connection(args.host, args.port)

    if args.test in ["audio", "all"] and results.get("connection", True):
        results["audio"] = await test_audio_chunk(args.host, args.port)

    if args.test in ["streaming", "all"] and results.get("audio", True):
        results["streaming"] = await test_streaming(args.host, args.port)

    # Summary
    print("\n" + "=" * 60)
    print("Test Summary")
    print("=" * 60)
    for test_name, passed in results.items():
        status = "PASS" if passed else "FAIL"
        print(f"  {test_name}: {status}")


if __name__ == "__main__":
    asyncio.run(main())
