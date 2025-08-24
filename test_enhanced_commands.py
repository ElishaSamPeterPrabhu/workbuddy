"""
Test enhanced commands with updated AI system prompt.
"""

import sys
import os
import json

# Add the project root to the Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

def test_ai_commands():
    """Test enhanced commands with the AI client."""
    print("🧪 Testing Enhanced Commands with Updated System Prompt")
    print("=" * 60)
    
    try:
        from core.ai_client import AIClient
        
        ai_client = AIClient()
        print("✅ AI client initialized")
        
        # Test commands that should trigger enhanced actions
        test_commands = [
            # Email commands
            ("Check my emails", "email_summary"),
            ("Priority emails", "email_priorities"),
            ("Email summary", "email_summary"),
            ("Show me urgent emails", "email_priorities"),
            
            # Calendar commands  
            ("What's on my calendar?", "calendar_overview"),
            ("Today's meetings", "calendar_overview"),
            ("Calendar overview", "calendar_overview"),
            ("Meeting prep", "meeting_prep"),
            
            # Briefing commands
            ("Morning briefing", "enhanced_briefing"),
            ("Daily priorities", "daily_priorities"),
            ("Today's summary", "enhanced_briefing"),
            ("What should I focus on today?", "daily_priorities"),
            
            # Control tests (should be convo)
            ("Hello", "convo"),
            ("How are you?", "convo"),
        ]
        
        print(f"\n🔄 Testing {len(test_commands)} commands...\n")
        
        results = []
        
        for i, (command, expected_action) in enumerate(test_commands, 1):
            print(f"Test {i}: \"{command}\"")
            print(f"Expected action: {expected_action}")
            
            try:
                # Get AI response
                response = ai_client.get_response(command)
                print(f"AI Response: {response[:100]}{'...' if len(response) > 100 else ''}")
                
                # Try to parse JSON from response
                parsed_action = None
                try:
                    # Look for JSON blocks in response
                    import re
                    json_match = re.search(r'```json\s*(\{.*?\})\s*```', response, re.DOTALL)
                    if json_match:
                        json_str = json_match.group(1)
                        parsed = json.loads(json_str)
                        parsed_action = parsed.get('action', 'unknown')
                    else:
                        # Try parsing the whole response as JSON
                        parsed = json.loads(response)
                        parsed_action = parsed.get('action', 'unknown')
                except:
                    parsed_action = "no_json"
                
                print(f"Parsed action: {parsed_action}")
                
                # Check if action matches expected
                if parsed_action == expected_action:
                    print("✅ SUCCESS - Action matches expected!")
                    results.append((command, True, expected_action, parsed_action))
                elif expected_action == "convo" and parsed_action in ["convo", "no_json"]:
                    print("✅ SUCCESS - Conversation response as expected!")  
                    results.append((command, True, expected_action, parsed_action))
                else:
                    print(f"❌ MISMATCH - Expected {expected_action}, got {parsed_action}")
                    results.append((command, False, expected_action, parsed_action))
                
            except Exception as e:
                print(f"❌ ERROR: {e}")
                results.append((command, False, expected_action, "error"))
            
            print("-" * 50)
        
        # Summary
        print("\n📊 TEST RESULTS SUMMARY")
        print("=" * 60)
        
        successes = 0
        failures = 0
        
        print("\n✅ SUCCESSFUL COMMANDS:")
        for command, success, expected, actual in results:
            if success:
                successes += 1
                print(f"   \"{command}\" → {actual}")
        
        print("\n❌ FAILED COMMANDS:")
        for command, success, expected, actual in results:
            if not success:
                failures += 1
                print(f"   \"{command}\" → Expected: {expected}, Got: {actual}")
        
        print(f"\nOverall: {successes}/{len(results)} commands working correctly")
        
        if successes >= len(results) - 2:  # Allow for a couple of failures
            print("\n🎉 ENHANCED FEATURES ARE WORKING!")
            print("\n🚀 Ready for Windows deployment!")
            print("\nUsers can now ask:")
            print("• \"Check my emails\" → Gets intelligent email analysis")
            print("• \"What's on my calendar?\" → Gets calendar with meeting insights") 
            print("• \"Morning briefing\" → Gets comprehensive daily briefing")
            print("• \"Daily priorities\" → Gets AI-generated priority list")
        else:
            print(f"\n⚠️ Some commands need adjustment in the system prompt")
        
        return successes >= len(results) - 2
        
    except Exception as e:
        print(f"❌ Test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == '__main__':
    try:
        success = test_ai_commands()
        print(f"\nTest completed: {'SUCCESS' if success else 'NEEDS_WORK'}")
    except KeyboardInterrupt:
        print("\n\n👋 Test interrupted by user.")
