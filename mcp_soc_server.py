#!/usr/bin/env python3
"""
MCP Server for SOC Admin functionality
Replaces the FastAPI server with MCP protocol
"""

from mcp.server.fastmcp import FastMCP
from typing import Dict, Any
import json

# Create MCP server instance
mcp = FastMCP("SOC Admin Server")

@mcp.tool()
def assess_severity(url: str, confidence_score: float) -> Dict[str, Any]:
    """
    SOC Admin tool to assess URL severity based on confidence score
    
    Args:
        url: The URL to assess
        confidence_score: Confidence score between 0 and 1
    
    Returns:
        Dictionary with assessment result
    """
    try:
        # Validate confidence score
        if not isinstance(confidence_score, (int, float)):
            return {
                "url": url,
                "confidence_score": confidence_score,
                "result": "error"
            }
        
        if not (0 <= confidence_score <= 1):
            return {
                "url": url,
                "confidence_score": confidence_score,
                "result": "error"
            }
        
        # Apply the same logic as the original FastAPI server
        if confidence_score > 0.8:
            action = "block"
        elif confidence_score > 0.5:
            action = "review"
        else:
            action = "allow"
        
        return {
            "url": url,
            "confidence_score": confidence_score,
            "result": action
        }
        
    except Exception as e:
        return {
            "url": url,
            "confidence_score": confidence_score,
            "result": "error"
        }

@mcp.tool()
def health_check() -> Dict[str, str]:
    """
    Health check tool for SOC admin server
    
    Returns:
        Health status
    """
    return {"status": "healthy"}

# Add a resource for SOC guidelines (optional)
@mcp.resource("soc://guidelines")
def get_soc_guidelines() -> str:
    """Get SOC assessment guidelines"""
    return """
    SOC Assessment Guidelines:
    - Confidence Score > 0.8: BLOCK (High threat)
    - Confidence Score > 0.5: REVIEW (Medium threat)  
    - Confidence Score <= 0.5: ALLOW (Low threat)
    """

if __name__ == "__main__":
    # Run the MCP server with stdio transport
    mcp.run(transport="stdio")
