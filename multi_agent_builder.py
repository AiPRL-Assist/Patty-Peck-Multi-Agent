"""
Build multi-agent root from DB for Gavigans.
All webchat users share the same agent set (no per-user auth).
"""
import os
import logging
from google.adk.agents import Agent
from app.chat.tools import build_tools_from_config
from app.db import db

# Force logging to stdout for Railway visibility
logging.basicConfig(level=logging.INFO, format='%(levelname)s: %(message)s')
logger = logging.getLogger(__name__)

FALLBACK_INSTRUCTION = """You are a helpful AI assistant for Gavigans.
Answer questions about the company, products, and support. Be friendly and concise."""


async def build_root_agent(before_callback=None, after_callback=None) -> Agent:
    """
    Build root agent with sub-agents from DB.
    Uses first user's agents (seed puts them under admin). No auth - all Gavigans.
    """
    print(f"🔌 Connecting to Prisma DB...")
    print(f"   DATABASE_URL prefix: {os.environ.get('DATABASE_URL', 'NOT SET')[:50]}...")
    
    await db.connect()
    print("✅ Prisma connected")

    user = await db.user.find_first()
    print(f"👤 User lookup: {user.email if user else 'NOT FOUND'}")
    
    if not user:
        print("⚠️ No user in DB - running seed...")
        try:
            from seed import seed
            await seed()
            print("✅ Seed completed")
            # seed disconnects, so reconnect
            await db.connect()
            user = await db.user.find_first()
            print(f"👤 After seed - user: {user.email if user else 'STILL NOT FOUND'}")
        except Exception as e:
            import traceback
            traceback.print_exc()
            print(f"❌ Seed failed: {e}")
            user = None
            
    if not user:
        print("⚠️ No user found - returning fallback single agent")
        return Agent(
            name="gavigans_agent",
            model="gemini-2.0-flash",
            description="Gavigans assistant",
            instruction=FALLBACK_INSTRUCTION,
            tools=[],
            before_agent_callback=before_callback,
            after_agent_callback=after_callback,
        )

    db_agents = await db.agent.find_many(where={"userId": user.id})
    print(f"🤖 Found {len(db_agents)} agents in DB for user {user.email}")
    
    if not db_agents:
        print("⚠️ No agents in DB - running seed to create them...")
        try:
            from seed import seed
            await seed()
            print("✅ Seed completed")
            await db.connect()
            db_agents = await db.agent.find_many(where={"userId": user.id})
            print(f"🤖 After seed - found {len(db_agents)} agents")
        except Exception as e:
            import traceback
            traceback.print_exc()
            print(f"❌ Seed for agents failed: {e}")
            
    if not db_agents:
        print("⚠️ Still no agents - returning fallback single agent")
        return Agent(
            name="gavigans_agent",
            model="gemini-2.0-flash",
            description="Gavigans assistant",
            instruction=FALLBACK_INSTRUCTION,
            tools=[],
            before_agent_callback=before_callback,
            after_agent_callback=after_callback,
        )

    sub_agents = []
    for db_agent in db_agents:
        tool_configs = db_agent.tools if isinstance(db_agent.tools, list) else []
        agent_tools = build_tools_from_config(tool_configs)
        agent_name = db_agent.name.lower().replace(" ", "_")
        print(f"   → Building sub-agent: {agent_name} (tools: {len(agent_tools)})")
        agent_kwargs = {
            "name": agent_name,
            "model": db_agent.model,
            "description": db_agent.description,
            "instruction": db_agent.instruction,
        }
        if agent_tools:
            agent_kwargs["tools"] = agent_tools
        sub_agents.append(Agent(**agent_kwargs))

    agent_list = "\n".join(
        f"- {a.name}: {db_agents[i].description}" for i, a in enumerate(sub_agents)
    )

    root_instruction = (
        "You are the main routing agent for Gavigans. Your job is to understand "
        "the user's question and delegate it to the most appropriate specialist agent.\n\n"
        f"Available agents:\n{agent_list}\n\n"
        "Analyze the user's message and transfer to the most appropriate agent. "
        "If no agent is a good fit, respond directly with a helpful message."
    )

    root = Agent(
        name="gavigans_agent",
        model="gemini-2.0-flash",
        description="Gavigans multi-agent orchestrator",
        instruction=root_instruction,
        sub_agents=sub_agents,
        before_agent_callback=before_callback,
        after_agent_callback=after_callback,
    )
    print(f"✅ Multi-agent root built with {len(sub_agents)} sub-agents:")
    for sa in sub_agents:
        print(f"   • {sa.name}")
    return root
