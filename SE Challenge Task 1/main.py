import requests
import time
import os
import json

#API = "https://u8whitimu7.execute-api.ap-southeast-1.amazonaws.com/prod"
API = os.environ['API_URL']

DATASET = []

def getAuthToken():
	data = requests.get(f"{API}/register")
	token = (data.json()["data"]["authorizationToken"])
	return token

def dlDataset(next_id, authToken):
	data = {"next_id": next_id}
	headers = {
	"authorizationToken": authToken,
	"Content-Type": "application/json"
	}

	count = 0
	while True:
		r = requests.post(f"{API}/download-dataset", headers=headers, json=data)
		r = r.json()["data"]
		dataset = requests.get(r["dataset_url"])
		open(f"{count}.json", 'w').write(dataset.text)
		print(f"DATASET {count} LOADED")
		count += 1

		if r["next_id"]:
			data["next_id"] = r["next_id"]
			time.sleep(10)
		else:
			break

def cleanData(data):
	try:
		if not isinstance(data['id'], int):
			print("Invalid 'id': must be an integer.", data)
			return None

		restaurant_name = data['restaurant_name']
		if not isinstance(restaurant_name, str) or len(restaurant_name) < 1:
			return None
		for c in restaurant_name.replace(' ', '').upper():
			if not 65 <= ord(c) <= 90:
				# print("Invalid 'restaurant_name': must contain only alphabets and spaces.", data)
				return None			

		rating = data['rating']
		if not isinstance(rating, float) or not (1.00 <= rating <= 10.00):
			# print("Invalid 'rating': must be a float between 1.00 and 10.00.", data)
			return None

		distance = data['distance_from_me']
		if not isinstance(distance, float) or not (10.00 <= distance <= 1000.00):
			# print("Invalid 'distance_from_me': must be a float between 10.00 and 1000.00.", data)
			return None


		cleaned_data = {
			"id": data["id"],
			"restaurant_name": restaurant_name.strip(),
			"rating": rating,
			"distance_from_me": distance
		}

		return cleaned_data

	except json.JSONDecodeError:
		print("error")
	return None

def validate_data(files):
	validated_data = []
	
	for f in files:
		try:
			data = open(f,'r').read()
			json_data = json.loads(data)
			for d in json_data:
				cleaned = cleanData(d)
				if cleaned:
					validated_data.append(cleaned)
		except:
			pass
	print(f"Data Cleaned")
	return validated_data

def main():
	authToken = getAuthToken()
	dlDataset("", authToken)

	validated_data = validate_data(files = [f for f in os.listdir() if f.endswith(".json") and f != "validated_dataset.json"])
	with open("validated_dataset.json", 'w') as f:
		json.dump(validated_data, f, indent=4)

	check_data_validation = requests.post(f"{API}/test/check-data-validation", json={"data": validated_data})
	print(check_data_validation.text)
		

if __name__ == "__main__":
	main()