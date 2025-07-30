import asyncio
import websockets
import base64
import json
from vad_utils import is_human_voice
from twilio.rest import Client
import os

ACCOUNT_SID = os.getenv("TWILIO_ACCOUNT_SID")
AUTH_TOKEN = os.getenv("TWILIO_AUTH_TOKEN")
SIP_ADDRESS = os.getenv("TWILIO_SIP_ADDRESS")

client = Client(ACCOUNT_SID, AUTH_TOKEN)

async def handler(websocket):
    stream_sid = None
    async for message in websocket:
        try:
            data = json.loads(message)

            if "start" in data:
                stream_sid = data["start"]["streamSid"]
                print(f"🟢 Stream started: {stream_sid}")

            elif "media" in data:
                payload = data["media"]["payload"]
                audio_bytes = base64.b64decode(payload)
                if is_human_voice(audio_bytes):
                    print("✅ Human voice detected!")
                    await redirect_call(stream_sid)

            elif "stop" in data:
                print(f"🔴 Stream ended: {stream_sid}")

        except Exception as e:
            print(f"❌ Error: {e}")

async def redirect_call(stream_sid):
    for call in client.calls.list(status="in-progress"):
        if stream_sid in call.sid:
            client.calls(call.sid).update(
                twiml=f'''
                <Response>
                    <Say>One moment. Connecting you to our assistant.</Say>
                    <Dial>
                        <Sip>{SIP_ADDRESS}</Sip>
                    </Dial>
                </Response>
                '''
            )
            print("📞 Redirected to SIP.")
            break

async def main():
    print("🚀 WebSocket server running on port 10000")
    async with websockets.serve(handler, "0.0.0.0", 10000):
        await asyncio.Future()

if __name__ == "__main__":
    asyncio.run(main())
