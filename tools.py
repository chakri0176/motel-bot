import os
from langchain.tools import tool
from supabase import create_client, Client


url = os.environ.get("SUPABASE_URL")
key = os.environ.get("SUPABASE_SERVICE_KEY")
supabase: Client = create_client(url, key)

@tool
def check_room_availability(room_type: str):
    """Checks if a specific room type (Queen, King, Suite) is available."""
    # Query Supabase for available rooms of that type
    response = supabase.table("rooms").select("*").eq("room_type", room_type).eq("is_available", True).execute()
    rooms = response.data
    
    if not rooms:
        return f"I'm sorry, we don't have any {room_type} rooms available right now."
    
    count = len(rooms)
    price = rooms[0]['price_per_night']
    return f"Yes, we have {count} {room_type} rooms available starting at ${price} a night."

@tool
def book_reservation(name: str, room_type: str, date: str):
    """Books a room. Requires guest name, room type, and date."""
    # 1. Find an available room ID
    response = supabase.table("rooms").select("id").eq("room_type", room_type).eq("is_available", True).limit(1).execute()
    if not response.data:
        return "I apologize, but that room type just sold out."
    
    room_id = response.data[0]['id']
    
    # 2. Create Booking
    data = {"guest_name": name, "room_id": room_id, "check_in_date": date}
    supabase.table("bookings").insert(data).execute()
    
    # 3. Mark room as unavailable (simplified logic)
    supabase.table("rooms").update({"is_available": False}).eq("id", room_id).execute()
    
    return f"Success! I have booked a {room_type} room for {name} on {date}."