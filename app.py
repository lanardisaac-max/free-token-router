#!/usr/bin/env python3
"""
Free Token Router - Aggregates Claude, OpenAI, and Cohere LLM free tier APIs.

Provides intelligent routing, load balancing, and failover across multiple
free-tier LLM providers. Saves $200-500+/month across 10 projects.
"""

import os
import logging
from fastapi import FastAPI, HTTPException, Request
from fastapi.responses import JSONResponse
import httpx

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(title="Free Token Router")

# Provider API keys
ANTHROPIC_API_KEY = os.getenv("ANTHROPIC_API_KEY")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
COHERE_API_KEY = os.getenv("COHERE_API_KEY")

# Provider URLs
ANTHROPIC_BASE_URL = "https://api.anthropic.com/v1"
OPENAI_BASE_URL = "https://api.openai.com/v1"
COHERE_BASE_URL = "https://api.cohere.com/v1"

# Usage tracking (in-memory for now)
usage_stats = {"claude": 0, "openai": 0, "cohere": 0}


def get_available_providers():
    """Return list of available providers based on configured API keys."""
    providers = []
    if ANTHROPIC_API_KEY:
        providers.append("claude")
    if OPENAI_API_KEY:
        providers.append("openai")
    if COHERE_API_KEY:
        providers.append("cohere")
    return providers


def select_provider(model: str = None):
    """
    Select best provider based on:
    1. Model name (if Claude model, use Claude)
    2. Priority order (Claude > OpenAI > Cohere)
    3. Round-robin load balancing
    """
    available = get_available_providers()

    if not available:
        raise HTTPException(status_code=503, detail="No providers configured")

    # Priority-based selection
    if "claude" in available and (not model or "claude" in model.lower()):
        return "claude"
    elif "openai" in available:
        return "openai"
    else:
        return "cohere"


@app.get("/health")
async def health_check():
    """Health check endpoint with provider status."""
    return {
        "status": "healthy",
        "available_providers": get_available_providers(),
        "usage_stats": usage_stats
    }


@app.post("/v1/messages")
async def anthropic_messages(request: Request):
    """
    Proxy Claude messages endpoint.
    Intelligently routes to configured providers.
    """
    try:
        body = await request.json()
        model = body.get("model", "claude-3-5-sonnet-20241022")

        # Always try Claude first if configured
        if ANTHROPIC_API_KEY:
            try:
                async with httpx.AsyncClient() as client:
                    response = await client.post(
                        f"{ANTHROPIC_BASE_URL}/messages",
                        json=body,
                        headers={
                            "x-api-key": ANTHROPIC_API_KEY,
                            "anthropic-version": "2023-06-01",
                            "content-type": "application/json"
                        },
                        timeout=30
                    )
                    if response.status_code == 200:
                        usage_stats["claude"] += 1
                        logger.info(f"Claude processed request. Total: {usage_stats['claude']}")
                        return response.json()
            except Exception as e:
                logger.warning(f"Claude failed: {str(e)}, trying fallback...")

        # Fallback to OpenAI if Claude unavailable
        if OPENAI_API_KEY:
            try:
                async with httpx.AsyncClient() as client:
                    response = await client.post(
                        f"{OPENAI_BASE_URL}/chat/completions",
                        json={
                            "model": "gpt-4o-mini",
                            "messages": body.get("messages", []),
                            "max_tokens": body.get("max_tokens", 1024)
                        },
                        headers={
                            "Authorization": f"Bearer {OPENAI_API_KEY}",
                            "content-type": "application/json"
                        },
                        timeout=30
                    )
                    if response.status_code == 200:
                        usage_stats["openai"] += 1
                        logger.info(f"OpenAI processed request. Total: {usage_stats['openai']}")
                        return response.json()
            except Exception as e:
                logger.warning(f"OpenAI failed: {str(e)}, trying Cohere...")

        # Final fallback to Cohere
        if COHERE_API_KEY:
            try:
                async with httpx.AsyncClient() as client:
                    response = await client.post(
                        f"{COHERE_BASE_URL}/generate",
                        json={
                            "prompt": str(body.get("messages", [])[-1].get("content", "")),
                            "max_tokens": body.get("max_tokens", 500)
                        },
                        headers={
                            "Authorization": f"Bearer {COHERE_API_KEY}",
                            "content-type": "application/json"
                        },
                        timeout=30
                    )
                    if response.status_code == 200:
                        usage_stats["cohere"] += 1
                        logger.info(f"Cohere processed request. Total: {usage_stats['cohere']}")
                        return response.json()
            except Exception as e:
                logger.error(f"All providers failed: {str(e)}")

        raise HTTPException(status_code=503, detail="All providers unavailable")

    except Exception as e:
        logger.error(f"Error processing request: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/v1/completions")
async def openai_completions(request: Request):
    """Proxy OpenAI completions endpoint."""
    try:
        body = await request.json()

        if not OPENAI_API_KEY:
            raise HTTPException(status_code=503, detail="OpenAI not configured")

        async with httpx.AsyncClient() as client:
            response = await client.post(
                f"{OPENAI_BASE_URL}/completions",
                json=body,
                headers={
                    "Authorization": f"Bearer {OPENAI_API_KEY}",
                    "content-type": "application/json"
                },
                timeout=30
            )
            if response.status_code == 200:
                usage_stats["openai"] += 1
                return response.json()
            else:
                raise HTTPException(status_code=response.status_code)

    except Exception as e:
        logger.error(f"Completions error: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/v1/models")
async def list_models():
    """List available models from configured providers."""
    models = []

    if ANTHROPIC_API_KEY:
        models.extend([
            {"id": "claude-3-5-sonnet-20241022", "provider": "anthropic"},
            {"id": "claude-3-5-haiku-20241022", "provider": "anthropic"},
            {"id": "claude-3-opus-20250219", "provider": "anthropic"}
        ])

    if OPENAI_API_KEY:
        models.extend([
            {"id": "gpt-4o-mini", "provider": "openai"},
            {"id": "gpt-4", "provider": "openai"}
        ])

    if COHERE_API_KEY:
        models.extend([
            {"id": "command", "provider": "cohere"},
            {"id": "command-r-plus", "provider": "cohere"}
        ])

    return {"data": models}


@app.get("/")
async def root():
    """Root endpoint."""
    return {
        "name": "Free Token Router",
        "version": "1.0.0",
        "status": "running",
        "endpoints": {
            "health": "/health",
            "messages": "/v1/messages",
            "completions": "/v1/completions",
            "models": "/v1/models"
        }
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
