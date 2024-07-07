import json

def extract_json_from_text(text):
    try:
        # Find the indices of the first and last curly braces
        start_index = text.index('{')
        end_index = text.rindex('}') + 1  # +1 to include the closing brace
        
        # Extract the potential JSON string
        json_string = text[start_index:end_index]
        
        # Attempt to parse the extracted string as JSON
        json_object = json.loads(json_string)
        
        return json_object
    except ValueError as e:
        print(f"Error: Unable to extract valid JSON. {str(e)}")
        return None
    except json.JSONDecodeError as e:
        print(f"Error: Invalid JSON format. {str(e)}")
        return None