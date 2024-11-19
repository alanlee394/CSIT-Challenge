import json
import math
import requests

API_URL = "https://u8whitimu7.execute-api.ap-southeast-1.amazonaws.com/prod"
REGISTER_ENDPOINT = "/register"
CHECK_TOPK_ENDPOINT = "/test/check-topk-sort"
INPUT_FILE = "validated_dataset.json"
OUTPUT_FILE = "top_results.json"

def get_authorization_token(api_url):
    """Fetch the authorization token from the API."""
    register_endpoint = api_url + REGISTER_ENDPOINT
    try:
        print("Fetching authorization token...")
        response = requests.get(register_endpoint)
        response.raise_for_status()
        data = response.json().get("data", {})
        token = data.get("authorizationToken")
        if token:
            print("Authorization Token received.")
            return token
        else:
            print("Token not found in response.")
            return None
    except requests.exceptions.RequestException as e:
        print(f"An error occurred while fetching the token: {e}")
        return None

def calculate_score(entry):
    """Calculate the score for a restaurant entry."""
    rating = entry["rating"]
    distance = entry["distance_from_me"]
    id_ = entry["id"]
    # Calculate score
    score = (rating * 10 - distance * 0.5 + math.sin(id_) * 2) * 100 + 0.5
    final_score = round(score / 100, 2)
    return final_score

def load_validated_data(input_file):
    """Load validated data from JSON file."""
    try:
        with open(input_file, 'r') as f:
            data = json.load(f)
        # If data is wrapped in a "data" field, extract it
        if isinstance(data, dict) and "data" in data:
            data = data["data"]
        return data
    except FileNotFoundError:
        print(f"Input file '{input_file}' not found.")
        return []
    except json.JSONDecodeError as e:
        print(f"Error decoding JSON from '{input_file}': {e}")
        return []

def write_output_file(output_data, output_file):
    """Write the output data to a JSON file."""
    try:
        with open(output_file, 'w') as f:
            json.dump(output_data, f, indent=4)
        print(f"Top 10 results saved to '{output_file}'.")
    except IOError as e:
        print(f"Error writing to output file '{output_file}': {e}")

def submit_results(api_url, token, output):
    """Submit the top 10 results for verification."""
    headers = {"Authorization": token, "Content-Type": "application/json"}
    try:
        print("Submitting the top 10 results for verification...")
        response = requests.post(api_url + CHECK_TOPK_ENDPOINT, json={"data": output}, headers=headers)
        response.raise_for_status()
        print("Submission successful!")
        print("Response from server:")
        print(response.text)
    except requests.exceptions.RequestException as e:
        print(f"An error occurred while submitting the results: {e}")
    except Exception as e:
        print(f"An unexpected error occurred: {e}")

def main():
    # Load the validated data from the JSON file
    validated_data = load_validated_data(INPUT_FILE)
    if not validated_data:
        print("No data to process. Exiting.")
        return

    # Add score to each restaurant entry
    for entry in validated_data:
        try:
            entry["score"] = calculate_score(entry)
        except KeyError as e:
            print(f"Missing expected field {e} in entry: {entry}")
            continue
        except TypeError as e:
            print(f"Type error in entry {entry}: {e}")
            continue

    # Sort the restaurants based on the required criteria
    # 1. Score (descending)
    # 2. Rating (descending)
    # 3. Distance (ascending)
    # 4. Restaurant name (alphabetically ascending)
    sorted_data = sorted(
        validated_data,
        key=lambda x: (-x["score"], -x["rating"], x["distance_from_me"], x["restaurant_name"])
    )

    # Extract the top 10 restaurants
    top_10_results = sorted_data[:10]

    # Prepare the output
    output = [
        {
            "id": entry["id"],
            "restaurant_name": entry["restaurant_name"],
            "rating": entry["rating"],
            "distance_from_me": entry["distance_from_me"],
            "score": entry["score"]
        }
        for entry in top_10_results
    ]

    # Write the result to a JSON file
    write_output_file(output, OUTPUT_FILE)

    # Get authorization token
    token = get_authorization_token(API_URL)
    if not token:
        print("Failed to fetch authorization token. Exiting...")
        return

    # Submit the result for verification
    submit_results(API_URL, token, output)

if __name__ == "__main__":
    main()
