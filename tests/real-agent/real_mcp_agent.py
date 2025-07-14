import time
import random
from tame_sdk import TameClient

# Simulated tool functions (replace with real ones in production)
def send_email(to, subject, body):
    print(f"[TOOL] Sending email to {to} | Subject: {subject} | Body: {body}")
    return True

def post_to_slack(channel, message):
    print(f"[TOOL] Posting to Slack channel {channel}: {message}")
    return True

def delete_file(path):
    print(f"[TOOL] Deleting file: {path}")
    return True

def main():
    tame = TameClient(api_url="http://localhost:8000")
    session_id = f"real-agent-test-{int(time.time())}-{random.randint(1000,9999)}"
    agent_id = "real-mcp-agent"
    user_id = "test-user"

    print(f"\n=== Real MCP Agent Test (Session: {session_id}) ===\n")

    # 1. Try to send an internal email (should be allowed by safe policy)
    print("[STEP 1] Attempting to send internal email...")
    decision = tame.check_policy("send_email", {"to": "alice@yourcompany.com", "subject": "Hello"}, session_id=session_id, agent_id=agent_id, user_id=user_id)
    print(f"Policy decision: {decision['action']} | Reason: {decision['reason']}")
    if decision['action'] == 'allow':
        send_email("alice@yourcompany.com", "Hello", "This is a test email.")
    print()

    # 2. Try to send an external email (should be denied by safe policy)
    print("[STEP 2] Attempting to send external email...")
    decision = tame.check_policy("send_email", {"to": "bob@gmail.com", "subject": "Hi"}, session_id=session_id, agent_id=agent_id, user_id=user_id)
    print(f"Policy decision: {decision['action']} | Reason: {decision['reason']}")
    if decision['action'] == 'allow':
        send_email("bob@gmail.com", "Hi", "This should be blocked!")
    print()

    # 3. Post to allowed Slack channel
    print("[STEP 3] Posting to #general Slack channel...")
    decision = tame.check_policy("post_to_slack", {"channel": "#general", "message": "Hello team!"}, session_id=session_id, agent_id=agent_id, user_id=user_id)
    print(f"Policy decision: {decision['action']} | Reason: {decision['reason']}")
    if decision['action'] == 'allow':
        post_to_slack("#general", "Hello team!")
    print()

    # 4. Attempt a dangerous action (delete_file)
    print("[STEP 4] Attempting dangerous action: delete_file...")
    decision = tame.check_policy("delete_file", {"path": "/etc/passwd"}, session_id=session_id, agent_id=agent_id, user_id=user_id)
    print(f"Policy decision: {decision['action']} | Reason: {decision['reason']}")
    if decision['action'] == 'allow':
        delete_file("/etc/passwd")
    print()

    print("=== Test Complete ===\n")
    print("Check the Tame dashboard for logs, policy hits, and compliance status.")

if __name__ == "__main__":
    main() 