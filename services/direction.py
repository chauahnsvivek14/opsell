import logging
from typing import Dict
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field
import os
import sys

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('/var/log/opsell/direction_service.log'),
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger(__name__)

# Initialize FastAPI app
app = FastAPI(
    title="Market Direction Classifier",
    version="1.0.0",
    description="Microservice for classifying market conditions based on price, VIX, and option premiums"
)


class MarketDataRequest(BaseModel):
    """Request model for market classification"""
    open_price: float = Field(..., gt=0, description="Market open price")
    current_price: float = Field(..., gt=0, description="Current market price")
    vix_open: float = Field(..., ge=0, description="VIX at market open")
    vix_now: float = Field(..., ge=0, description="Current VIX")
    straddle_open: float = Field(..., gt=0, description="Straddle premium at open")
    straddle_now: float = Field(..., gt=0, description="Current straddle premium")

    class Config:
        json_schema_extra = {
            "example": {
                "open_price": 23945.45,
                "current_price": 24040.25,
                "vix_open": 19.3,
                "vix_now": 18.97,
                "straddle_open": 241.35,
                "straddle_now": 235.85
            }
        }


class MarketClassificationResponse(BaseModel):
    """Response model for market classification"""
    classification: str
    price_move_pct: float
    vix_change: float
    premium_change_pct: float
    timestamp: str = None


def classify_market(open_price: float, current_price: float, vix_open: float, 
                    vix_now: float, straddle_open: float, straddle_now: float) -> Dict[str, any]:
    """
    Classify market conditions based on price movement, VIX change, and option premium decay
    
    Returns:
        dict: Classification result with metrics
    """
    try:
        # Price movement %
        price_move_pct = ((current_price - open_price) / open_price) * 100
        
        # VIX change
        vix_change = vix_now - vix_open
        
        # Premium decay %
        premium_change_pct = ((straddle_now - straddle_open) / straddle_open) * 100

        # --- Classification Logic ---
        
        # OPTION SELLER DAY
        if abs(price_move_pct) < 0.4 and vix_change < -0.5 and premium_change_pct < -20:
            classification = "🟢 OPTION SELLER DAY (Range + Decay)"
        
        # OPTION BUYER DAY
        elif abs(price_move_pct) > 0.7 and vix_change > 0.5 and premium_change_pct > -10:
            classification = "🔴 OPTION BUYER DAY (Trending / Expansion)"
        
        # MIXED DAY
        else:
            classification = "🟡 MIXED / TRAP DAY (Avoid aggressive trades)"
        
        return {
            "classification": classification,
            "price_move_pct": round(price_move_pct, 2),
            "vix_change": round(vix_change, 2),
            "premium_change_pct": round(premium_change_pct, 2)
        }
    
    except Exception as e:
        logger.error(f"Error in classify_market: {str(e)}")
        raise


@app.get("/health", tags=["Health"])
async def health_check():
    """Health check endpoint for load balancer"""
    return {"status": "healthy", "service": "market-direction-classifier"}


@app.post("/classify", response_model=MarketClassificationResponse, tags=["Classification"])
async def classify_endpoint(request: MarketDataRequest) -> MarketClassificationResponse:
    """
    Classify market conditions based on provided market data
    
    - **open_price**: Market open price
    - **current_price**: Current market price
    - **vix_open**: VIX at market open
    - **vix_now**: Current VIX value
    - **straddle_open**: Straddle premium at open
    - **straddle_now**: Current straddle premium
    """
    try:
        logger.info(f"Received classification request: {request}")
        
        result = classify_market(
            open_price=request.open_price,
            current_price=request.current_price,
            vix_open=request.vix_open,
            vix_now=request.vix_now,
            straddle_open=request.straddle_open,
            straddle_now=request.straddle_now
        )
        
        from datetime import datetime
        response = MarketClassificationResponse(
            **result,
            timestamp=datetime.utcnow().isoformat()
        )
        
        logger.info(f"Classification result: {response.classification}")
        return response
    
    except ValueError as e:
        logger.error(f"Validation error: {str(e)}")
        raise HTTPException(status_code=400, detail=f"Invalid input: {str(e)}")
    except Exception as e:
        logger.error(f"Unexpected error: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal server error")


@app.get("/", tags=["Info"])
async def root():
    """API information endpoint"""
    return {
        "service": "Market Direction Classifier",
        "version": "1.0.0",
        "endpoints": {
            "health": "/health",
            "classify": "/classify",
            "docs": "/docs",
            "redoc": "/redoc"
        }
    }


if __name__ == "__main__":
    import uvicorn
    
    # Read configuration from environment
    host = os.getenv("SERVICE_HOST", "0.0.0.0")
    port = int(os.getenv("SERVICE_PORT", "8000"))
    workers = int(os.getenv("SERVICE_WORKERS", "4"))
    
    logger.info(f"Starting Market Direction Classifier on {host}:{port} with {workers} workers")
    
    uvicorn.run(
        app,
        host=host,
        port=port,
        workers=1,  # Use 1 worker here; gunicorn will manage workers in production
        log_level="info"
    )
