import sys
import os
from pathlib import Path

# Add src to path
sys.path.append(str(Path(__file__).parent / "src"))

from openjarvis.core import DatabaseManager, ToolRegistry, AgentRegistry
from openjarvis.tools.memory_manage import MemoryManageTool
from openjarvis.tools.user_profile_manage import UserProfileManageTool
from openjarvis.agents.intake import IntakeAgent
from openjarvis.agents.planner import PlannerAgent
from openjarvis.agents.reflector import ReflectorAgent
from openjarvis.agents.synthesizer import SynthesizerAgent

def test_database():
    print("Testing DatabaseManager...")
    db = DatabaseManager(":memory:")
    db.store_preference("theme", "dark")
    assert db.get_preference("theme") == "dark"
    
    db.add_memory("test_key", "test_value", category="short_term")
    mem = db.get_memory("test_key")
    assert len(mem) == 1
    assert mem[0]["value"] == '"test_value"'
    print("DatabaseManager OK.")

def test_tools():
    print("Testing Tools...")
    db = DatabaseManager(":memory:")
    
    # Test MemoryManageTool
    tool = MemoryManageTool(db)
    tool.execute(action="add", entry="Remember this", category="long_term")
    res = tool.execute(action="read", category="long_term")
    assert "Remember this" in res.content
    print("MemoryManageTool OK.")
    
    # Test UserProfileManageTool
    u_tool = UserProfileManageTool(db)
    u_tool.execute(action="add", entry="User likes coffee")
    res = u_tool.execute(action="read")
    assert "User likes coffee" in res.content
    print("UserProfileManageTool OK.")

def test_agents():
    print("Testing Agents...")
    assert "intake" in AgentRegistry.keys()
    assert "planner" in AgentRegistry.keys()
    assert "reflector" in AgentRegistry.keys()
    assert "synthesizer" in AgentRegistry.keys()
    print("Agent Registration OK.")

if __name__ == "__main__":
    try:
        test_database()
        test_tools()
        test_agents()
        print("\nALL CHECKS PASSED!")
    except Exception as e:
        print(f"\nCHECK FAILED: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
