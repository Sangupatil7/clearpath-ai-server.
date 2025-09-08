from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import uvicorn

# --- 1. DEFINE THE DATA MODELS ---
# These define the structure of the data sent between the Flutter app and this server.

class Location(BaseModel):
    lat: float
    lon: float

class ConversationRequest(BaseModel):
    trip_id: str
    current_step: str
    audio_text: str
    current_location: Location
    trip_context: dict

class DisplayData(BaseModel):
    polyline: str
    eta_sec: int
    distance_km: float

class ConversationResponse(BaseModel):
    next_step: str
    action_required: str
    speak_text: str
    display_data: DisplayData | None = None
    updated_context: dict

# --- 2. CREATE THE FASTAPI APP ---
app = FastAPI()

# --- 3. ADD CORS MIDDLEWARE ---
# This is a security feature that allows your friend's Flutter app (running on a phone)
# to make requests to this server (running on your computer).
origins = ["*"] # Allow all origins for simplicity in a demo

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# --- 4. THE CONVERSATIONAL AI ENDPOINT ---
# This is the "brain" of your voice assistant. The Flutter app will call this endpoint.
@app.post("/ai/assistant/conversation", response_model=ConversationResponse)
async def handle_conversation(request: ConversationRequest):
    print(f"Received request for step: {request.current_step}")
    print(f"Spoken text: {request.audio_text}")

    # --- Step 1 of the conversation: Ask for the hospital ---
    if request.current_step == "get_emergency_level":
        level = "red" # For the demo, we assume the emergency level from the spoken text.
        
        # The server's response:
        return ConversationResponse(
            next_step="get_destination",
            action_required="SPEAK_AND_LISTEN",
            speak_text=f"Emergency level {level} recorded. What is the destination hospital?",
            updated_context={"emergency_level": level}
        )
    
    # --- Step 2 of the conversation: Provide the route ---
    elif request.current_step == "get_destination":
        hospital_name = request.audio_text
        print(f"Finding route to {hospital_name}...")
        
        # In a real app, this is where you would calculate a route.
        # For the demo, we return a hardcoded route.
        fake_polyline = '[[12.9716, 77.5946], [12.96, 77.60], [12.95, 77.61], [12.9342, 77.6109]]'
        
        # The server's final response:
        return ConversationResponse(
            next_step="routing_complete",
            action_required="DISPLAY_ROUTE_AND_GO",
            speak_text=f"Route found to {hospital_name}. Starting navigation.",
            display_data=DisplayData(
                polyline=str(fake_polyline),
                eta_sec=900, # 15 minutes
                distance_km=12.5
            ),
            updated_context=request.trip_context
        )

# --- 5. RUN THE SERVER ---
if __name__ == "__main__":
    # This makes the server accessible from other devices on your network
    uvicorn.run(app, host="0.0.0.0", port=8000)

