from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field
from agno.agent import Agent, RunResponse
from agno.models.openai import OpenAIChat
from agno.tools.sql import SQLTools
from agno.storage.sqlite import SqliteStorage
from agno.utils.pprint import pprint_run_response
from fastapi.responses import FileResponse 
from fastapi.staticfiles import StaticFiles
import os


# --- OpenAI API Key ---
os.environ["OPENAI_API_KEY"] = "ENTER_YOUR_OPENAI_API_KEY_HERE"

# --- Agent prompt ---
AGENT_PROMPT = """
You are an AI assistant helping customers to track their orders.
- Always ask the customers for their tracking ID if they have not provided it yet.
- If the tracking ID is missing or invalid, politely ask the customer to provide it again.
- Respond clearly and helpfully with the order status and all other details, including Customer name.
"""

# --- Database setup ---
db_path = os.path.join(os.getcwd(), "orders.db")
DATABASE_URL = f"sqlite:///{db_path}"

# --- SQL Tool ---
sql_tool = SQLTools(db_url=DATABASE_URL)  # ✅ No table_name needed

# --- Optional: Agent memory storage ---
storage = SqliteStorage(db_url=DATABASE_URL, table_name="agent_memory")

# --- OpenAI Model ---
openai_model = OpenAIChat("gpt-4o-mini")  

# --- Agent setup ---
order_agent = Agent(
    name="OrderTrackingAgent",
    model=openai_model,
    tools=[sql_tool],
    storage=storage,
    instructions=AGENT_PROMPT   # ✅ use 'instructions'
)


# --- FastAPI App ---
app = FastAPI(title="Order Tracking AI Agent")

# Mount a "static" directory for frontend files
app.mount("/static", StaticFiles(directory="static"), name="static")


# --- Request/Response Models ---
class ChatRequest(BaseModel):
    message: str = Field(..., description="User message (tracking ID or general query)")

class TrackingResponse(BaseModel):
    message: str

@app.get("/")
async def serve_home():
    return FileResponse("static/index.html")

# --- Endpoint ---
@app.post("/chat", response_model=TrackingResponse)
async def chat(request: ChatRequest):
    from sqlalchemy import create_engine, text
    engine = create_engine(DATABASE_URL, echo=True, future=True)

    try:
        user_msg = request.message.strip()

        # If the user message looks like a tracking ID, check DB
        if user_msg.upper().startswith("TRACK"):
            with engine.connect() as conn:
                result = conn.execute(
                    text("SELECT * FROM orders WHERE tracking_id = :tid"),
                    {"tid": user_msg}
                ).mappings().fetchone()

            if result:
                order_info = (
                    f"Tracking ID: {result['tracking_id']}, "
                    f"Customer: {result['customer_name']}, "
                    f"Status: {result['order_status']}, "
                    f"Details: {result['details']}"
                )
                response: RunResponse = order_agent.run(
                    f"Customer asked about tracking ID '{user_msg}'. Order info: {order_info}"
                )
                return {"message": response.content}
            else:
                response: RunResponse = order_agent.run(
                    f"Customer provided tracking ID '{user_msg}', but no order found."
                )
                return {"message": response.content}

        # Otherwise, let the agent handle normal conversation like "Hi"
        response: RunResponse = order_agent.run(user_msg)
        return {"message": response.content}

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
