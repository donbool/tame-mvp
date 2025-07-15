#!/usr/bin/env python3
"""
Minimal test to diagnose MCP GitHub server connection issues.
"""

import asyncio
import os
import sys
import json
from dotenv import load_dotenv

load_dotenv()

async def test_mcp_github_server():
    """Test basic MCP GitHub server connection step by step."""
    
    print("🧪 Testing MCP GitHub Server Connection")
    print("=" * 50)
    
    # Check environment
    github_token = os.getenv("GITHUB_TOKEN")
    if not github_token:
        print("❌ GITHUB_TOKEN not found")
        return False
    
    print(f"✅ GitHub token found: {github_token[:10]}...")
    
    try:
        from mcp.client.stdio import stdio_client, StdioServerParameters
        from mcp import ClientSession
        print("✅ MCP imports successful")
    except ImportError as e:
        print(f"❌ MCP import failed: {e}")
        return False
    
    try:
        # Test server parameters
        print("🔧 Creating server parameters...")
        server_params = StdioServerParameters(
            command="npx",
            args=["-y", "@modelcontextprotocol/server-github"],
            env={
                "GITHUB_PERSONAL_ACCESS_TOKEN": github_token
            }
        )
        print("✅ Server parameters created")
        
        # Test stdio client creation
        print("📡 Creating stdio client...")
        client = stdio_client(server_params)
        print("✅ Stdio client created")
        
        # Test connection
        print("🔌 Attempting connection...")
        try:
            async with client as (read_stream, write_stream):
                print("✅ Streams connected")
                
                # Test session creation
                print("📋 Creating MCP session...")
                session = ClientSession(read_stream, write_stream)
                print("✅ Session created")
                
                # Test initialization
                print("🔄 Initializing session...")
                init_result = await asyncio.wait_for(session.initialize(), timeout=10.0)
                print(f"✅ Session initialized: {init_result}")
                
                # Test tool listing
                print("🛠️  Listing tools...")
                tools_result = await asyncio.wait_for(session.list_tools(), timeout=5.0)
                tools = tools_result.tools if hasattr(tools_result, 'tools') else []
                print(f"✅ Tools listed: {len(tools)} available")
                
                for tool in tools[:3]:  # Show first 3 tools
                    print(f"   📌 {tool.name}: {tool.description}")
                
                # Test a simple tool call
                if tools:
                    print("🧪 Testing a simple tool call...")
                    try:
                        # Try to call a basic tool
                        test_tool = tools[0]
                        print(f"🔍 Testing tool: {test_tool.name}")
                        
                        # Use minimal arguments
                        test_args = {"owner": "octocat", "repo": "Hello-World"}
                        
                        result = await asyncio.wait_for(
                            session.call_tool(test_tool.name, test_args),
                            timeout=10.0
                        )
                        print(f"✅ Tool call successful: {test_tool.name}")
                        
                    except Exception as tool_error:
                        print(f"⚠️  Tool call failed (but connection works): {tool_error}")
                
                print("🎉 MCP GitHub server connection SUCCESSFUL!")
                return True
                
        except asyncio.TimeoutError:
            print("⏰ Connection timeout")
            return False
            
    except Exception as e:
        print(f"💥 Connection failed: {e}")
        print(f"Error type: {type(e).__name__}")
        import traceback
        traceback.print_exc()
        return False

async def test_with_tamesdk():
    """Test MCP with TameSDK integration."""
    
    print("\n🛡️  Testing MCP + TameSDK Integration")
    print("=" * 50)
    
    try:
        import tamesdk
        
        # Create TameSDK client
        tame_client = tamesdk.Client(
            api_url=os.getenv("TAME_API_URL", "http://localhost:8000"),
            session_id=f"mcp-test-{asyncio.get_event_loop().time()}",
            agent_id="mcp-diagnostic-agent",
            user_id="developer"
        )
        print("✅ TameSDK client created")
        
        # Test policy enforcement
        print("🛡️  Testing policy enforcement...")
        try:
            decision = tame_client.enforce(
                tool_name="get_repository",
                tool_args={"owner": "test", "repo": "test"}
            )
            print("✅ Policy enforcement working - operation allowed")
            
        except tamesdk.PolicyViolationException as e:
            print(f"🛡️  Policy enforcement working - operation blocked: {e}")
            
        except Exception as e:
            print(f"❌ TameSDK error: {e}")
            return False
        
        tame_client.close()
        print("✅ TameSDK integration test complete")
        return True
        
    except Exception as e:
        print(f"💥 TameSDK integration failed: {e}")
        return False

async def main():
    """Run all diagnostic tests."""
    
    print("🔬 MCP GitHub Server Diagnostic Test")
    print("=" * 60)
    
    # Test basic MCP connection
    mcp_success = await test_mcp_github_server()
    
    # Test TameSDK integration
    tamesdk_success = await test_with_tamesdk()
    
    print("\n📊 Test Results Summary")
    print("=" * 30)
    print(f"MCP Connection: {'✅ PASS' if mcp_success else '❌ FAIL'}")
    print(f"TameSDK Integration: {'✅ PASS' if tamesdk_success else '❌ FAIL'}")
    
    if mcp_success and tamesdk_success:
        print("\n🎉 All tests passed! Ready for real MCP agent.")
    else:
        print("\n🔧 Issues found. Fix required before proceeding.")
        
    return mcp_success and tamesdk_success

if __name__ == "__main__":
    result = asyncio.run(main())
    sys.exit(0 if result else 1)