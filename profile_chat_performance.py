"""
Deep Performance Profiler for Chat Endpoint
============================================
Measures exactly where time is spent in the chat flow.
"""
import asyncio
import time
import json
import httpx
from datetime import datetime
from uuid import uuid4

API_BASE = "http://localhost:8000"
APP_NAME = "gavigans_agent"


class PerformanceProfiler:
    def __init__(self):
        self.timings = {}
        self.start_time = None

    def start(self, label):
        self.start_time = time.time()
        print(f"\n⏱️  {label}...")

    def end(self, label):
        elapsed = time.time() - self.start_time
        self.timings[label] = elapsed
        print(f"   ✅ {elapsed:.3f}s")
        return elapsed

    def report(self):
        print("\n" + "="*60)
        print("PERFORMANCE BREAKDOWN")
        print("="*60)

        total = sum(self.timings.values())
        for label, duration in sorted(self.timings.items(), key=lambda x: x[1], reverse=True):
            percentage = (duration / total * 100) if total > 0 else 0
            bar = "█" * int(percentage / 2)
            print(f"{label:40} {duration:6.3f}s {bar} {percentage:5.1f}%")

        print("="*60)
        print(f"{'TOTAL TIME':40} {total:6.3f}s")
        print("="*60)


async def profile_chat_flow():
    """Profile the complete chat flow with detailed timing"""
    profiler = PerformanceProfiler()
    user_id = f"profile_{uuid4().hex[:8]}"

    print(f"🔍 Profiling chat flow for user: {user_id}")
    print("="*60)

    async with httpx.AsyncClient(timeout=30.0) as client:

        # Step 1: Session Creation
        profiler.start("1. Session Creation")
        session_response = await client.post(
            f"{API_BASE}/apps/{APP_NAME}/users/{user_id}/sessions",
            json={"state": {}}
        )
        profiler.end("1. Session Creation")

        if session_response.status_code != 200:
            print(f"❌ Session creation failed: {session_response.text}")
            return

        session_data = session_response.json()
        session_id = session_data["id"]
        print(f"   Session ID: {session_id[:12]}...")

        # Step 2: Session Retrieval (to test cache/db speed)
        profiler.start("2. Session Retrieval")
        retrieve_response = await client.get(
            f"{API_BASE}/apps/{APP_NAME}/users/{user_id}/sessions/{session_id}"
        )
        profiler.end("2. Session Retrieval")

        # Step 3: SSE Chat Request - Time to First Byte
        profiler.start("3. SSE Request Setup")
        chat_payload = {
            "appName": APP_NAME,
            "userId": user_id,
            "sessionId": session_id,
            "newMessage": {
                "role": "user",
                "parts": [{"text": "hello"}]
            },
            "streaming": True
        }
        profiler.end("3. SSE Request Setup")

        # Step 4: Time to First Response Chunk
        print(f"\n⏱️  4. Sending SSE request and waiting for first chunk...")
        sse_start = time.time()
        first_chunk_time = None
        chunks_received = 0

        async with client.stream(
            "POST",
            f"{API_BASE}/run_sse",
            json=chat_payload,
            timeout=30.0
        ) as response:

            async for chunk in response.aiter_bytes():
                if first_chunk_time is None:
                    first_chunk_time = time.time() - sse_start
                    profiler.timings["4. Time to First Chunk"] = first_chunk_time
                    print(f"   ✅ First chunk received: {first_chunk_time:.3f}s")

                chunks_received += 1

                # Parse SSE events to identify stages
                if chunk.startswith(b"data: "):
                    try:
                        data_str = chunk[6:].decode().strip()
                        event = json.loads(data_str)

                        # Track different event types
                        if "modelVersion" in event and "5. First AI Response" not in profiler.timings:
                            ai_response_time = time.time() - sse_start
                            profiler.timings["5. First AI Response"] = ai_response_time
                            print(f"   ✅ First AI response: {ai_response_time:.3f}s")

                        # Check for function calls (agent routing)
                        if "content" in event and "parts" in event.get("content", {}):
                            for part in event["content"]["parts"]:
                                if "functionCall" in part:
                                    if part["functionCall"].get("name") == "transfer_to_agent":
                                        transfer_time = time.time() - sse_start
                                        if "6. Agent Transfer" not in profiler.timings:
                                            profiler.timings["6. Agent Transfer"] = transfer_time
                                            print(f"   ✅ Transfer to sub-agent: {transfer_time:.3f}s")

                                if "text" in part and part["text"].strip():
                                    text_time = time.time() - sse_start
                                    if "7. First Text Response" not in profiler.timings:
                                        profiler.timings["7. First Text Response"] = text_time
                                        print(f"   ✅ First text response: {text_time:.3f}s")
                    except:
                        pass

                # Stop after getting enough data
                if chunks_received > 20:
                    break

        total_stream_time = time.time() - sse_start
        profiler.timings["8. Total Stream Time"] = total_stream_time
        print(f"   ✅ Total streaming: {total_stream_time:.3f}s ({chunks_received} chunks)")

    # Generate report
    profiler.report()

    # Analysis
    print("\n📊 ANALYSIS:")
    print("-" * 60)

    if "4. Time to First Chunk" in profiler.timings:
        ttfb = profiler.timings["4. Time to First Chunk"]
        if ttfb > 5:
            print(f"⚠️  SLOW: Time to first byte is {ttfb:.1f}s (should be <2s)")
            print("   Likely causes:")
            print("   - Database session lookup/creation blocking")
            print("   - Cold start / connection pool warming")
            print("   - Network latency to database")
        elif ttfb > 2:
            print(f"⚠️  MODERATE: Time to first byte is {ttfb:.1f}s")
            print("   Room for optimization in session handling")
        else:
            print(f"✅ GOOD: Time to first byte is {ttfb:.1f}s")

    if "5. First AI Response" in profiler.timings and "4. Time to First Chunk" in profiler.timings:
        ai_overhead = profiler.timings["5. First AI Response"] - profiler.timings["4. Time to First Chunk"]
        print(f"\n🤖 AI Response Latency: {ai_overhead:.3f}s")
        if ai_overhead > 1.5:
            print("   ⚠️  AI API is slower than expected")

    if "6. Agent Transfer" in profiler.timings:
        print(f"\n🔀 Multi-Agent Overhead:")
        print(f"   Root agent routing: {profiler.timings['6. Agent Transfer']:.3f}s")
        if "7. First Text Response" in profiler.timings:
            sub_agent_time = profiler.timings["7. First Text Response"] - profiler.timings["6. Agent Transfer"]
            print(f"   Sub-agent response: {sub_agent_time:.3f}s")
            print(f"   💡 Total multi-agent overhead: ~{profiler.timings['6. Agent Transfer']:.1f}s")
            print("      (Could save this by using single agent)")


if __name__ == "__main__":
    print("🚀 Starting Deep Performance Profile...")
    print("=" * 60)
    asyncio.run(profile_chat_flow())
