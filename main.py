import requests
import json
import sys

def call_langflow_api(message, api_token):
    """
    Call the Langflow API with a message and return the response.
    
    Args:
        message (str): The input message to send to the Langflow API
        api_token (str): Your Langflow API token
    
    Returns:
        dict: The API response
    """
    # API endpoint
    url = "https://api.langflow.astra.datastax.com/lf/6a45b841-eabe-4f9b-b5a0-8711e83beddf/api/v1/run/795cb236-e7bf-4769-a71c-cc599a4d3165"
    
    # Query parameters
    params = {
        "stream": "false"
    }
    
    # Headers
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {api_token}"
    }
    
    # Request payload
    payload = {
        "input_value": message,
        "output_type": "chat",
        "input_type": "chat",
        "tweaks": {
            "Agent-P5ux3": {},
            "ChatInput-UG3MA": {},
            "ChatOutput-bBEAX": {},
            "URL-2vuYK": {},
            "CalculatorComponent-b0roK": {}
        }
    }
    
    try:
        # Make the API request
        response = requests.post(url, params=params, headers=headers, json=payload)
        
        # Check if the request was successful
        response.raise_for_status()
        
        # Parse the JSON response
        return response.json()
    
    except requests.exceptions.RequestException as e:
        print(f"Error calling Langflow API: {e}")
        return None

def main():
    # Check if command-line arguments are provided
    if len(sys.argv) < 3:
        print("Usage: python script.py \"your message\" YOUR_API_TOKEN")
        return
    
    # Get message and API token from command-line arguments
    message = sys.argv[1]
    api_token = sys.argv[2]
    
    # Call the API
    result = call_langflow_api(message, api_token)
    
    # Print the result
    if result:
        print(json.dumps(result, indent=2))

if __name__ == "__main__":
    main()