from crewai import Agent
from langchain_groq import ChatGroq

# Check what the Agent expects
print("Agent model_fields:")
for field_name, field_info in Agent.model_fields.items():
    if 'llm' in field_name.lower():
        print(f"  {field_name}: {field_info.annotation}")

print("\n" + "="*60)

# Try to understand what ChatGroq is
print("\nChatGroq parent classes:")
print(f"  {ChatGroq.__mro__}")

# Try with model string instead
print("\n" + "="*60)
print("\nTrying with model string instead of object...")

try:
    agent = Agent(
        role="Test",
        goal="Test",
        backstory="Test",
        llm="gpt-4o",  # Use model string instead
    )
    print("✓ Agent created successfully with model string")
except Exception as e:
    print(f"✗ Error: {e}")
