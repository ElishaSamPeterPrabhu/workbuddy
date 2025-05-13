from datetime import datetime, timedelta
from integrations.calendar import GoogleCalendarIntegration

cal = GoogleCalendarIntegration()

# 1. Add an event
start = datetime.now() + timedelta(minutes=15)
end = start + timedelta(hours=1)
event = cal.add_event(
    summary="WorkBuddy Test Meeting",
    start=start,
    end=end,
    description="This is a test event created by WorkBuddy.",
    attendees=["your@email.com"],
)
print("Created event:", event)

# 2. List today's events
events = cal.get_events()
print("Today's events:")
for e in events:
    print("-", e.get("summary"), e.get("start"), e.get("id"))

# 3. Update the event (if created)
if "id" in event:
    updated = cal.update_event(event["id"], {"summary": "WorkBuddy Updated Meeting"})
    print("Updated event:", updated)

# 4. Delete the event (if created)
if "id" in event:
    deleted = cal.delete_event(event["id"])
    print("Deleted event:", deleted)
