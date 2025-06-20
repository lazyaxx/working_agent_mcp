#!/usr/bin/env python

import sys
import warnings
import os
from datetime import datetime
from crew import SecurityCrew
from crewai_tools import MCPServerAdapter
from mcp import StdioServerParameters

warnings.filterwarnings("ignore", category=SyntaxWarning, module="pysbd")

def run():
    urls = [
        "https://example.com",
        "https://malware.com/download.exe", 
        "https://phishing-site.net/fake-login",
        "https://legitimate-site.org",
        "https://suspicious-download.org/file.exe",
        "http://unsecure-site.com"
    ]

    print(f"\n🔍 Processing {len(urls)} URLs with MCP protocol...")
    
    # Setup MCP server parameters
    current_dir = os.path.dirname(os.path.abspath(__file__))
    mcp_server_path = os.path.join(current_dir, "mcp_soc_server.py")
    
    server_params = StdioServerParameters(
        command=sys.executable,
        args=[mcp_server_path],
        env=dict(os.environ),
    )
    
    # Use context manager for MCP connection
    try:
        with MCPServerAdapter(server_params) as mcp_tools:
            print(f"Available MCP tools: {[tool.name for tool in mcp_tools]}")
            
            # Create security crew with MCP tools
            security_crew = SecurityCrew(mcp_tools=list(mcp_tools))
            
            url_inputs = [{"url": url} for url in urls]
            results = security_crew.crew().kickoff_for_each(inputs=url_inputs)

            processed_urls = []
            output_results = []
            
            for i, (url, result) in enumerate(zip(urls, results)):
                print(f"✅ Completed processing: {url}")
                processed_urls.append(url)
                output_results.append({
                    "url": url,
                    "result": str(result),
                    "crew_result": result
                })
                print(f"   Status: {'Success' if result else 'Failed'}")
                print("-" * 50)

            print("\n📊 SECURITY MONITORING SUMMARY (MCP-Enabled)")
            print("=" * 60)
            print(f"URLs Processed: {len(processed_urls)}")

            blocked_urls = []
            allowed_urls = []
            review_urls = []

            for i, result in enumerate(output_results, 1):
                result_str = result['result'].lower()
                url = result['url']
                print(f"\n{i}. {url}")
                
                if 'block' in result_str:
                    blocked_urls.append(url)
                    print(f"   🚫 Decision: BLOCKED")
                elif 'allow' in result_str:
                    allowed_urls.append(url)
                    print(f"   ✅ Decision: ALLOWED")
                elif 'review' in result_str:
                    review_urls.append(url)
                    print(f"   🔍 Decision: REVIEW REQUIRED")
                else:
                    print(f"   ❓ Decision: UNKNOWN")
                
                print(f"   Summary: {result['result'][:100]}...")

            print(f"\n🛡️ SECURITY SUMMARY:")
            print(f"   🚫 Blocked: {len(blocked_urls)} URLs")
            print(f"   ✅ Allowed: {len(allowed_urls)} URLs") 
            print(f"   🔍 Review Required: {len(review_urls)} URLs")

            if blocked_urls:
                print(f"\n🚫 BLOCKED URLS:")
                for url in blocked_urls:
                    print(f"   - {url}")

            return {
                "summary": "Security monitoring completed with MCP protocol",
                "stats": {
                    "total": len(processed_urls),
                    "blocked": len(blocked_urls),
                    "allowed": len(allowed_urls),
                    "review": len(review_urls)
                }
            }
            
    except Exception as e:
        print(f"Error with MCP connection: {e}")
        print("Make sure the MCP server is properly configured.")
        return {"error": str(e)}

if __name__ == "__main__":
    results = run()
    print("\nFinal Results:")
    print(results)
    sys.exit(0)
