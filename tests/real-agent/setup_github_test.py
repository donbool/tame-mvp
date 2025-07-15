#!/usr/bin/env python3
"""
Setup script for GitHub agent testing.
Creates a test repository and configures the environment.
"""

import os
import sys
import subprocess
from pathlib import Path

# Try to load environment variables from .env file
try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    print("💡 Install python-dotenv for .env file support: pip install python-dotenv")

def check_requirements():
    """Check if all required environment variables and tools are available."""
    required_env = {
        "OPENAI_API_KEY": "OpenAI API key for GPT-4 access",
        "GITHUB_TOKEN": "GitHub Personal Access Token with repo permissions",
    }
    
    missing = []
    for env_var, description in required_env.items():
        if not os.getenv(env_var):
            missing.append(f"  {env_var}: {description}")
    
    if missing:
        print("❌ Missing required environment variables:")
        print("\n".join(missing))
        print("\nSet them with:")
        print("export OPENAI_API_KEY='your-openai-key'")
        print("export GITHUB_TOKEN='your-github-token'")
        return False
    
    # Check if GitHub CLI is available
    try:
        subprocess.run(["gh", "--version"], capture_output=True, check=True)
        print("✅ GitHub CLI is available")
    except (subprocess.CalledProcessError, FileNotFoundError):
        print("⚠️  GitHub CLI not found. Install with: brew install gh")
        print("   (Optional - only needed for easy repo creation)")
    
    # Check if Node.js is available (for MCP GitHub server)
    try:
        subprocess.run(["node", "--version"], capture_output=True, check=True)
        subprocess.run(["npx", "--version"], capture_output=True, check=True)
        print("✅ Node.js and npx are available")
    except (subprocess.CalledProcessError, FileNotFoundError):
        print("❌ Node.js/npx not found. Install with: brew install node")
        return False
    
    return True

def install_dependencies():
    """Install Python dependencies."""
    print("📦 Installing Python dependencies...")
    try:
        subprocess.run([
            sys.executable, "-m", "pip", "install", "-r", "requirements.txt"
        ], check=True)
        print("✅ Dependencies installed successfully")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ Failed to install dependencies: {e}")
        return False

def create_test_repository():
    """Create a test repository for agent testing."""
    repo_name = input("Enter test repository name (or press Enter for 'tame-agent-test'): ").strip()
    if not repo_name:
        repo_name = "tame-agent-test"
    
    try:
        # Check if gh CLI is available
        subprocess.run(["gh", "--version"], capture_output=True, check=True)
        
        # Create repository
        result = subprocess.run([
            "gh", "repo", "create", repo_name, 
            "--public", "--clone", "--description", "Test repository for TameSDK GitHub agent"
        ], capture_output=True, text=True)
        
        if result.returncode == 0:
            print(f"✅ Created and cloned repository: {repo_name}")
            
            # Create some test files
            repo_path = Path(repo_name)
            if repo_path.exists():
                # Create a simple Python file
                (repo_path / "test_file.py").write_text("""
# Test file for GitHub agent
def hello_world():
    return "Hello, World!"

def add_numbers(a, b):
    return a + b
""")
                
                # Create a README
                (repo_path / "README.md").write_text(f"""
# {repo_name}

Test repository for TameSDK GitHub agent testing.

This repository is used to test:
- AI-powered PR reviews
- Policy enforcement on GitHub operations
- Compliance checking
- Security issue creation
""")
                
                # Commit initial files
                os.chdir(repo_path)
                subprocess.run(["git", "add", "."], check=True)
                subprocess.run(["git", "commit", "-m", "Initial commit for agent testing"], check=True)
                subprocess.run(["git", "push", "origin", "main"], check=True)
                os.chdir("..")
                
                print(f"✅ Repository setup complete: https://github.com/{os.getenv('GITHUB_USER', 'USERNAME')}/{repo_name}")
                return f"{os.getenv('GITHUB_USER', 'USERNAME')}/{repo_name}"
        else:
            print(f"❌ Failed to create repository: {result.stderr}")
            
    except (subprocess.CalledProcessError, FileNotFoundError):
        print("⚠️  GitHub CLI not available. Please create a test repository manually:")
        print("1. Go to https://github.com/new")
        print("2. Create a public repository")
        print("3. Add some test files")
        print("4. Create a test PR for the agent to review")
        
        manual_repo = input("Enter your repository name (owner/repo): ").strip()
        return manual_repo if manual_repo else None

def create_test_policy():
    """Update the backend with the GitHub policy."""
    print("📋 Setting up GitHub agent policy...")
    
    # Read the policy file
    policy_path = Path("github_policy.yaml")
    if not policy_path.exists():
        print("❌ github_policy.yaml not found")
        return False
    
    print("✅ GitHub policy configuration ready")
    print("   Policy file: github_policy.yaml")
    print("   Note: You'll need to load this policy into your TameSDK backend")
    
    return True

def create_test_pr():
    """Create a test PR for the agent to review."""
    print("\n🔧 Creating a test PR...")
    
    repo = input("Enter repository name (owner/repo): ").strip()
    if not repo:
        print("Repository name required")
        return
    
    try:
        # Clone repo temporarily for PR creation
        temp_dir = "temp_pr_creation"
        subprocess.run(["git", "clone", f"https://github.com/{repo}.git", temp_dir], check=True)
        os.chdir(temp_dir)
        
        # Create a new branch
        subprocess.run(["git", "checkout", "-b", "test-pr-for-agent"], check=True)
        
        # Add a test file with some issues for the agent to find
        test_file_content = """
# Test file with intentional issues for AI review
import os
import requests

def process_user_data(user_input):
    # Security issue: SQL injection potential
    query = f"SELECT * FROM users WHERE name = '{user_input}'"
    
    # Performance issue: synchronous request in loop
    results = []
    for i in range(1000):
        response = requests.get(f"https://api.example.com/user/{i}")
        results.append(response.json())
    
    # Code quality issue: hardcoded values
    api_key = "sk-1234567890abcdef"  # Hardcoded API key
    password = "admin123"  # Hardcoded password
    
    return results

def insecure_function():
    # Another security issue: using eval
    user_code = input("Enter Python code: ")
    return eval(user_code)
"""
        
        with open("test_security_issues.py", "w") as f:
            f.write(test_file_content)
        
        # Commit and push
        subprocess.run(["git", "add", "test_security_issues.py"], check=True)
        subprocess.run(["git", "commit", "-m", "Add test file with security issues for AI review"], check=True)
        subprocess.run(["git", "push", "origin", "test-pr-for-agent"], check=True)
        
        # Create PR using GitHub CLI
        pr_result = subprocess.run([
            "gh", "pr", "create",
            "--title", "Test PR for TameSDK Agent Review",
            "--body", """This is a test PR created for the TameSDK GitHub agent to review.

The code intentionally contains several issues:
- Security vulnerabilities (SQL injection, hardcoded secrets)
- Performance problems (synchronous requests in loop)
- Code quality issues (hardcoded values, use of eval)

The AI agent should detect these issues and provide feedback while being restricted by TameSDK policies.""",
            "--head", "test-pr-for-agent",
            "--base", "main"
        ], capture_output=True, text=True, check=True)
        
        # Clean up
        os.chdir("..")
        subprocess.run(["rm", "-rf", temp_dir], check=True)
        
        print("✅ Test PR created successfully!")
        print(f"PR URL: {pr_result.stdout.strip()}")
        
        # Extract PR number
        pr_url = pr_result.stdout.strip()
        pr_number = pr_url.split("/")[-1]
        
        return int(pr_number)
        
    except subprocess.CalledProcessError as e:
        print(f"❌ Failed to create test PR: {e}")
        return None

def main():
    """Main setup function."""
    print("🚀 TameSDK GitHub Agent Setup")
    print("=" * 40)
    
    # Check requirements
    if not check_requirements():
        sys.exit(1)
    
    # Install dependencies
    if not install_dependencies():
        sys.exit(1)
    
    # Setup policy
    if not create_test_policy():
        sys.exit(1)
    
    # Ask user what they want to do
    print("\n🎯 What would you like to do?")
    print("1. Create a new test repository")
    print("2. Create a test PR in existing repository")
    print("3. Skip setup and show usage instructions")
    
    choice = input("Enter choice (1-3): ").strip()
    
    if choice == "1":
        repo = create_test_repository()
        if repo:
            pr_number = create_test_pr()
            if pr_number:
                print(f"\n✅ Setup complete! Test with:")
                print(f"python openai_github_agent.py --repo {repo} --action review --pr {pr_number}")
    
    elif choice == "2":
        pr_number = create_test_pr()
        if pr_number:
            repo = input("Enter repository name (owner/repo): ").strip()
            print(f"\n✅ Test PR created! Test with:")
            print(f"python openai_github_agent.py --repo {repo} --action review --pr {pr_number}")
    
    else:
        print("\n📖 Usage Instructions:")
        print("1. Start TameSDK backend: docker-compose up -d")
        print("2. Load github_policy.yaml into your TameSDK backend")
        print("3. Set environment variables:")
        print("   export OPENAI_API_KEY='your-key'")
        print("   export GITHUB_TOKEN='your-token'")
        print("4. Run the agent:")
        print("   python openai_github_agent.py --repo owner/repo --action review --pr 123")

if __name__ == "__main__":
    main()