"""
Demo script showing MCP server capabilities for WorkBuddy.

This demonstrates how MCP servers can enhance WorkBuddy's Jarvis-like features.
"""

import asyncio
import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from core.mcp_manager import mcp_manager
from integrations.outlook_mcp import OutlookMCPIntegration


async def demo_filesystem_mcp():
    """Demonstrate filesystem operations via MCP."""
    print("\n=== Filesystem MCP Demo ===")
    
    try:
        # List files in Documents
        print("\nListing Documents folder...")
        files = await mcp_manager.list_directory("C:/Users/Documents")
        print(f"Found {len(files)} items")
        for file in files[:5]:  # Show first 5
            print(f"  - {file}")
        
        # Read a file
        print("\nReading a sample file...")
        content = await mcp_manager.read_file("C:/Users/Documents/sample.txt")
        print(f"File content: {content[:100]}...")
        
    except Exception as e:
        print(f"Filesystem demo error: {e}")


async def demo_windows_cli_mcp():
    """Demonstrate Windows CLI operations via MCP."""
    print("\n=== Windows CLI MCP Demo ===")
    
    try:
        # Check if enabled
        if not mcp_manager.config["servers"]["windows-cli"]["enabled"]:
            print("Windows CLI server is disabled for security. Enable in config to test.")
            return
        
        # Get system info
        print("\nGetting system information...")
        result = await mcp_manager.execute_command(
            "Get-ComputerInfo | Select-Object CsName, WindowsVersion, OsArchitecture | Format-List",
            shell="powershell"
        )
        print(result)
        
        # List running processes
        print("\nTop 5 CPU-consuming processes...")
        result = await mcp_manager.execute_command(
            "Get-Process | Sort-Object CPU -Descending | Select-Object -First 5 | Format-Table Name, CPU, WorkingSet",
            shell="powershell"
        )
        print(result)
        
    except Exception as e:
        print(f"CLI demo error: {e}")


async def demo_outlook_mcp():
    """Demonstrate Outlook integration via COM MCP."""
    print("\n=== Outlook COM MCP Demo ===")
    
    try:
        # Check if enabled
        if not mcp_manager.config["servers"]["com-server"]["enabled"]:
            print("COM server is disabled. Install and enable to test Outlook integration.")
            return
        
        outlook = OutlookMCPIntegration()
        
        # Get calendar items
        print("\nFetching today's calendar...")
        appointments = await outlook.get_calendar_items(days_ahead=1)
        if appointments:
            print(f"Found {len(appointments)} appointments:")
            for appt in appointments:
                print(f"  - {appt['subject']} at {appt['start']}")
        else:
            print("No appointments found for today")
        
        # Get unread emails
        print("\nChecking unread emails...")
        emails = await outlook.get_unread_emails(max_items=5)
        if emails:
            print(f"Found {len(emails)} unread emails:")
            for email in emails:
                print(f"  - From: {email['sender']}")
                print(f"    Subject: {email['subject']}")
                print(f"    Preview: {email['preview'][:50]}...")
        else:
            print("No unread emails")
        
    except Exception as e:
        print(f"Outlook demo error: {e}")


async def demo_jarvis_workflow():
    """Demonstrate a complete Jarvis-like workflow using MCP."""
    print("\n=== Jarvis Workflow Demo ===")
    print("Simulating: 'Jarvis, prepare my daily report and email it to me'")
    
    try:
        # 1. Gather system information
        print("\n1. Gathering system information...")
        if mcp_manager.config["servers"]["windows-cli"]["enabled"]:
            disk_info = await mcp_manager.execute_command(
                "Get-PSDrive -PSProvider FileSystem | Format-Table Name, Used, Free",
                shell="powershell"
            )
            print("Disk usage collected")
        
        # 2. Create report file
        print("\n2. Creating report file...")
        report_content = f"""Daily System Report
==================

Date: {asyncio.get_event_loop().time()}

System Status:
- All systems operational
- Disk usage within normal parameters
- No critical alerts

Tasks Completed:
- Morning briefing delivered
- Email check completed
- Calendar synchronized

Recommendations:
- Review pending emails
- Prepare for upcoming meetings
- Run system maintenance this weekend
"""
        
        # In a real scenario, we'd write this using MCP
        print("Report created")
        
        # 3. Send via Outlook
        print("\n3. Sending report via email...")
        if mcp_manager.config["servers"]["com-server"]["enabled"]:
            outlook = OutlookMCPIntegration()
            success = await outlook.send_email(
                to="user@example.com",
                subject="Daily System Report",
                body=report_content
            )
            if success:
                print("Report emailed successfully!")
        else:
            print("(Email sending simulated - COM server not enabled)")
        
        print("\n✅ Workflow completed successfully!")
        
    except Exception as e:
        print(f"Workflow error: {e}")


async def main():
    """Run all MCP demos."""
    print("WorkBuddy MCP Server Demo")
    print("=" * 50)
    
    # Start enabled MCP servers
    print("\nStarting MCP servers...")
    await mcp_manager.start_all_enabled()
    
    # Run demos
    await demo_filesystem_mcp()
    await demo_windows_cli_mcp()
    await demo_outlook_mcp()
    await demo_jarvis_workflow()
    
    # Cleanup
    print("\nShutting down MCP servers...")
    await mcp_manager.stop_all()
    
    print("\nDemo complete!")


if __name__ == "__main__":
    # Create demos directory if needed
    Path("demos").mkdir(exist_ok=True)
    
    # Run the async main function
    asyncio.run(main()) 