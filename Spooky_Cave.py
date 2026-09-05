import os
import io
from fastapi import FastAPI, HTTPException
from fastapi.responses import StreamingResponse
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

app = FastAPI(title="Spooky Cave Server Engine", version="2.0")

# Enable CORS so your portal can talk cleanly to the backend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Adjust in production to your exact domain
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class AssetRequest(BaseModel):
    asset_id: str
    os_target: str = "Unknown"

@app.post("/api/process-order")
async def process_order(req: AssetRequest):
    """
    Receives asset requests from the Spooky portal, applies secure 
    encapsulation, and returns a hardware-lockable .spooky container.
    """
    try:
        clean_asset_id = req.asset_id.strip() or "DEFAULT_SECURE_ASSET"
        
        # --- SPOOKY CAVE CORE PROCESSING ---
        # Here is where your server-side data transformation and encapsulation occur.
        # For testing, we generate a secure binary payload representing the "spookified" asset.
        raw_payload = f"SPOOKY_SECURE_CONTAINER_DATA::{clean_asset_id}::TARGET_OS:{req.os_target}".encode('utf-8')
        
        # In full production, you would read your master file here, apply your 
        # proprietary transformation matrix, and pack it into the binary stream.
        
        # Package into a memory stream for transmission
        file_stream = io.BytesIO(raw_payload)
        
        # Format the output filename
        safe_filename = f"{clean_asset_id.replace(' ', '_')}_secure.spooky"
        
        return StreamingResponse(
            file_stream,
            media_type="application/octet-stream",
            headers={
                "Content-Disposition": f"attachment; filename={safe_filename}"
            }
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Spooky Cave processing error: {str(e)}")

if __name__ == "__main__":
    import uvicorn
    # Run the sovereign server locally on port 8000 (or whichever port your Cloudflare tunnel points to)
    uvicorn.run(app, host="127.0.0.1", port=8000)