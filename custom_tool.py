from crewai.tools import BaseTool
import json
import http.client
from typing import Dict, Any, Union


class SOCCommunicationTool(BaseTool):
    name: str = "soc_communicator"
    description: str = "Communicates with SOC admin server for severity assessment"
    
    def _run(self, analysis_data: Union[dict, str]) -> Dict[str, Any]:
        """Send analysis to SOC admin and get severity assessment"""
        
        if isinstance(analysis_data, str):
            try:
                parsed_data = json.loads(analysis_data)
            except json.JSONDecodeError:
                return {"error": "Invalid input: analysis_data must be a dictionary or a valid JSON string."}
        elif isinstance(analysis_data, dict):
            parsed_data = analysis_data
        else:
            return {"error": "Invalid input: analysis_data must be a dictionary or a string."}
        
        url = parsed_data.get("url")
        confidence_score = parsed_data.get("confidence_score", 0.5)
        
        if not url:
            return {"error": "Missing required field: url"}
        
        post_data = json.dumps({"url": url, "confidence_score": confidence_score})
        headers = {"Content-type": "application/json"}
        
        try:
            conn = http.client.HTTPConnection("localhost", 9000)
            conn.request("POST", "/assess_severity", post_data, headers)
            response = conn.getresponse()
            
            if response.status != 200:
                conn.close()
                return {"error": f"Server returned status {response.status}"}
            
            response_data = response.read().decode()
            conn.close()
            
            response_json = json.loads(response_data)
            
            result_dict = {
                "url": response_json.get("url", url),
                "confidence_score": response_json.get("confidence_score", confidence_score),
                "result": response_json.get("result", "null")
            }
            
            return result_dict
            
        except ConnectionRefusedError:
            return {"error": "Connection refused: SOC admin server is not running on localhost:8001"}
        except json.JSONDecodeError:
            return {"error": "Invalid JSON response from server"}
        except Exception as e:
            return {"error": f"Unexpected error: {str(e)}"}
