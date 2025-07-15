#!/usr/bin/env python3
"""
Real-world example: OpenAI API integration with TameSDK

This example shows how to wrap OpenAI API calls with policy enforcement,
providing control over model usage, cost management, and content filtering.
"""

import asyncio
import os
from typing import Dict, Any, List, Optional
from dataclasses import dataclass

try:
    from openai import OpenAI, AsyncOpenAI
except ImportError:
    print("Please install openai: pip install openai")
    exit(1)

import tamesdk


# Configure TameSDK
tamesdk.configure(
    api_url=os.getenv("TAME_API_URL", "http://localhost:8000"),
    api_key=os.getenv("TAME_API_KEY"),
    agent_id="openai-agent",
    user_id=os.getenv("USER", "demo-user")
)


@dataclass
class CompletionRequest:
    """Structured request for OpenAI completions."""
    prompt: str
    model: str = "gpt-3.5-turbo"
    max_tokens: Optional[int] = None
    temperature: float = 0.7
    user_id: Optional[str] = None


class TameOpenAIClient:
    """OpenAI client with TameSDK policy enforcement."""
    
    def __init__(self, api_key: Optional[str] = None):
        self.openai_client = OpenAI(api_key=api_key)
        self.async_client = AsyncOpenAI(api_key=api_key)
        self.tame_client = tamesdk.Client()
    
    @tamesdk.enforce_policy(
        tool_name="openai_completion",
        metadata={"api_provider": "openai", "cost_tracking": True}
    )
    def create_completion(
        self,
        prompt: str,
        model: str = "gpt-3.5-turbo",
        max_tokens: Optional[int] = None,
        temperature: float = 0.7,
        **kwargs
    ) -> str:
        """
        Create a text completion with policy enforcement.
        
        Policies can control:
        - Which models are allowed
        - Token limits per user/session
        - Content filtering
        - Cost controls
        - Rate limiting
        """
        
        # Estimate cost for policy decisions
        estimated_cost = self._estimate_cost(model, max_tokens or 1000)
        
        response = self.openai_client.chat.completions.create(
            model=model,
            messages=[{"role": "user", "content": prompt}],
            max_tokens=max_tokens,
            temperature=temperature,
            **kwargs
        )
        
        result = response.choices[0].message.content
        
        # Log actual usage and cost
        actual_tokens = response.usage.total_tokens
        actual_cost = self._estimate_cost(model, actual_tokens)
        
        # This metadata will be logged automatically by the decorator
        return result
    
    @tamesdk.with_approval(
        approval_message="High-cost model usage requires approval"
    )
    def create_expensive_completion(
        self,
        prompt: str,
        model: str = "gpt-4",
        **kwargs
    ) -> str:
        """Create completion with expensive model (requires approval)."""
        return self.create_completion(prompt, model, **kwargs)
    
    @tamesdk.enforce_policy(tool_name="openai_embedding")
    def create_embedding(
        self,
        text: str,
        model: str = "text-embedding-ada-002"
    ) -> List[float]:
        """Create text embedding with policy enforcement."""
        response = self.openai_client.embeddings.create(
            model=model,
            input=text
        )
        return response.data[0].embedding
    
    @tamesdk.log_action(level="INFO", metadata={"sensitive": True})
    def moderate_content(self, text: str) -> Dict[str, Any]:
        """Moderate content (logged but not policy-enforced)."""
        response = self.openai_client.moderations.create(input=text)
        return {
            "flagged": response.results[0].flagged,
            "categories": dict(response.results[0].categories),
            "category_scores": dict(response.results[0].category_scores)
        }
    
    async def async_create_completion(
        self,
        prompt: str,
        model: str = "gpt-3.5-turbo",
        **kwargs
    ) -> str:
        """Async version with policy enforcement."""
        
        # Use async client for policy enforcement
        async with tamesdk.AsyncClient() as client:
            decision = await client.enforce(
                "openai_completion",
                {
                    "prompt": prompt,
                    "model": model,
                    "max_tokens": kwargs.get("max_tokens"),
                    "temperature": kwargs.get("temperature", 0.7)
                },
                metadata={"api_provider": "openai", "async": True}
            )
            
            if decision.is_allowed:
                response = await self.async_client.chat.completions.create(
                    model=model,
                    messages=[{"role": "user", "content": prompt}],
                    **kwargs
                )
                
                result = response.choices[0].message.content
                
                # Log the result
                await client.update_result(
                    decision.session_id,
                    decision.log_id,
                    {
                        "status": "success",
                        "tokens_used": response.usage.total_tokens,
                        "cost": self._estimate_cost(model, response.usage.total_tokens),
                        "result_length": len(result)
                    }
                )
                
                return result
            else:
                raise tamesdk.PolicyViolationException(decision)
    
    def _estimate_cost(self, model: str, tokens: int) -> float:
        """Estimate API cost based on model and token count."""
        # Simplified cost estimation (update with real pricing)
        cost_per_1k_tokens = {
            "gpt-3.5-turbo": 0.002,
            "gpt-4": 0.03,
            "gpt-4-turbo": 0.01,
            "text-embedding-ada-002": 0.0001
        }
        
        rate = cost_per_1k_tokens.get(model, 0.002)
        return (tokens / 1000) * rate
    
    def __enter__(self):
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        self.tame_client.close()


def demonstrate_policy_enforcement():
    """Demonstrate various policy enforcement scenarios."""
    
    with TameOpenAIClient() as client:
        print("🚀 TameSDK + OpenAI Integration Demo")
        print("=" * 50)
        
        # Example 1: Normal completion (should be allowed)
        print("\n📝 Example 1: Normal completion")
        try:
            result = client.create_completion(
                prompt="Explain quantum computing in simple terms",
                model="gpt-3.5-turbo",
                max_tokens=100
            )
            print(f"✅ Success: {result[:100]}...")
        except Exception as e:
            print(f"❌ Error: {e}")
        
        # Example 2: Expensive model (might require approval)
        print("\n💰 Example 2: Expensive model usage")
        try:
            result = client.create_expensive_completion(
                prompt="Write a detailed analysis of market trends",
                model="gpt-4",
                max_tokens=500
            )
            print(f"✅ Success: {result[:100]}...")
        except tamesdk.ApprovalRequiredException as e:
            print(f"⏳ Approval required: {e.decision.reason}")
        except Exception as e:
            print(f"❌ Error: {e}")
        
        # Example 3: Content moderation (always logged)
        print("\n🛡️ Example 3: Content moderation")
        test_content = "This is a normal message about technology"
        moderation = client.moderate_content(test_content)
        print(f"📊 Moderation result: {moderation}")
        
        # Example 4: Embedding creation
        print("\n🔢 Example 4: Text embedding")
        try:
            embedding = client.create_embedding(
                text="Machine learning is transforming industries",
                model="text-embedding-ada-002"
            )
            print(f"✅ Embedding created: {len(embedding)} dimensions")
        except Exception as e:
            print(f"❌ Error: {e}")


async def demonstrate_async_usage():
    """Demonstrate async usage patterns."""
    
    print("\n🔄 Async Usage Demo")
    print("=" * 30)
    
    client = TameOpenAIClient()
    
    tasks = [
        client.async_create_completion(
            f"Write a haiku about {topic}",
            model="gpt-3.5-turbo",
            max_tokens=50
        )
        for topic in ["nature", "technology", "friendship"]
    ]
    
    try:
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        for i, result in enumerate(results, 1):
            if isinstance(result, Exception):
                print(f"❌ Task {i} failed: {result}")
            else:
                print(f"✅ Task {i} success: {result}")
                
    except Exception as e:
        print(f"❌ Async error: {e}")


def test_policy_scenarios():
    """Test various policy scenarios without making actual API calls."""
    
    print("\n🧪 Policy Testing (No API Calls)")
    print("=" * 40)
    
    with tamesdk.Client() as client:
        
        test_cases = [
            # Normal usage
            ("openai_completion", {
                "prompt": "Hello world",
                "model": "gpt-3.5-turbo",
                "max_tokens": 100
            }),
            
            # Expensive model
            ("openai_completion", {
                "prompt": "Complex analysis",
                "model": "gpt-4",
                "max_tokens": 2000
            }),
            
            # High token usage
            ("openai_completion", {
                "prompt": "Generate long content",
                "model": "gpt-3.5-turbo", 
                "max_tokens": 4000
            }),
            
            # Embedding
            ("openai_embedding", {
                "text": "Sample text for embedding",
                "model": "text-embedding-ada-002"
            })
        ]
        
        for tool_name, args in test_cases:
            try:
                result = client.test_policy(tool_name, args)
                decision = result.get("decision", "unknown")
                reason = result.get("reason", "No reason provided")
                
                emoji = {"allow": "✅", "deny": "❌", "approve": "⏳"}.get(decision, "❓")
                print(f"{emoji} {tool_name}: {decision} - {reason}")
                
            except Exception as e:
                print(f"❌ Test error: {e}")


class ConversationAgent:
    """Example of a conversational agent with TameSDK integration."""
    
    def __init__(self):
        self.client = TameOpenAIClient()
        self.conversation_history = []
    
    @tamesdk.enforce_policy(
        tool_name="conversation_turn",
        metadata={"agent_type": "conversational", "multi_turn": True}
    )
    def chat(self, user_message: str, system_prompt: Optional[str] = None) -> str:
        """Process a conversation turn with policy enforcement."""
        
        messages = []
        if system_prompt:
            messages.append({"role": "system", "content": system_prompt})
        
        # Add conversation history
        messages.extend(self.conversation_history)
        messages.append({"role": "user", "content": user_message})
        
        # Use the underlying OpenAI client (already policy-enforced)
        response = self.client.openai_client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=messages,
            max_tokens=500,
            temperature=0.8
        )
        
        assistant_response = response.choices[0].message.content
        
        # Update conversation history
        self.conversation_history.append({"role": "user", "content": user_message})
        self.conversation_history.append({"role": "assistant", "content": assistant_response})
        
        # Keep only last 10 messages to avoid token limits
        if len(self.conversation_history) > 10:
            self.conversation_history = self.conversation_history[-10:]
        
        return assistant_response
    
    def __enter__(self):
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        self.client.__exit__(exc_type, exc_val, exc_tb)


def demonstrate_conversation_agent():
    """Demonstrate a multi-turn conversation with policy enforcement."""
    
    print("\n💬 Conversation Agent Demo")
    print("=" * 35)
    
    with ConversationAgent() as agent:
        
        conversation_turns = [
            "Hello! Can you help me understand machine learning?",
            "What are the main types of ML algorithms?",
            "Can you give me an example of supervised learning?"
        ]
        
        for i, user_msg in enumerate(conversation_turns, 1):
            try:
                print(f"\n👤 User: {user_msg}")
                response = agent.chat(
                    user_msg,
                    system_prompt="You are a helpful AI assistant specializing in technology education."
                )
                print(f"🤖 Assistant: {response}")
                
            except tamesdk.PolicyViolationException as e:
                print(f"❌ Conversation blocked: {e.decision.reason}")
            except Exception as e:
                print(f"❌ Error in turn {i}: {e}")


if __name__ == "__main__":
    print("🎯 TameSDK OpenAI Integration Examples")
    print("=" * 50)
    
    # Check if we have required environment variables
    if not os.getenv("OPENAI_API_KEY"):
        print("⚠️  Warning: OPENAI_API_KEY not set. Some examples may fail.")
    
    try:
        # Run synchronous examples
        demonstrate_policy_enforcement()
        
        # Test policies without API calls
        test_policy_scenarios()
        
        # Conversation agent demo
        demonstrate_conversation_agent()
        
        # Run async examples
        asyncio.run(demonstrate_async_usage())
        
        print("\n✅ All examples completed!")
        
    except KeyboardInterrupt:
        print("\n👋 Demo interrupted by user")
    except Exception as e:
        print(f"\n❌ Demo failed: {e}")
        import traceback
        traceback.print_exc()