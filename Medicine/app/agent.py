import requests
from requests import HTTPError


class AgentsClient:
    def __init__(self, base_url):
        self.base_url = base_url.rstrip("/")
        self.last_response = None

    def success(self) -> bool:
        if not self.last_response:
            return False
        try:
            self.last_response.raise_for_status()
        except HTTPError:
            return False
        else:
            return True

    def auth(self, username, password):
        url = f"{self.base_url}/auth"
        payload = {"username": username, "password": password}
        response = requests.post(url, json=payload)
        self.last_response = response
        return response.json()

    def reg(self, username, password):
        url = f"{self.base_url}/reg"
        payload = {"username": username, "password": password}
        response = requests.post(url, json=payload)
        self.last_response = response
        return response.json()

    def nav(self, query, language):
        url = f"{self.base_url}/nav"
        payload = {"query": query, "language": language}
        response = requests.post(url, json=payload)
        self.last_response = response
        return response.json()

    def rec(self, query):
        url = f"{self.base_url}/rec"
        payload = {"query": query}
        response = requests.post(url, json=payload)
        self.last_response = response
        print(response.text)
        return response.json()

    def blood(self, wbc, rbc, platelets):
        url = f"{self.base_url}/blood"
        payload = {"wbc": wbc, "rbc": rbc, "platelets": platelets}
        response = requests.post(url, json=payload)
        self.last_response = response
        return response.json()

    def hormones_blood(self, tsh, fsh, lh):
        url = f"{self.base_url}/blood_hormones"
        payload = {"tsh": tsh, "fsh": fsh, "lh": lh}
        response = requests.post(url, json=payload)
        self.last_response = response
        return response.json()

    def micronutrients_blood(self, ca, mg, fe):
        url = f"{self.base_url}/blood_micronutrients"
        payload = {"ca": ca, "mg": mg, "fe": fe}
        response = requests.post(url, json=payload)
        self.last_response = response
        return response.json()

    def vitamin_blood(
            self,
            vitamin_e,
            vitamin_d,
            vitamin_k,
            vitamin_c,
            vitamin_b1,
            vitamin_b2,
            vitamin_b9,
            vitamin_b12,
            vitamin_a,
            vitamin_b6,
    ):
        url = f"{self.base_url}/blood_vitamin"
        payload = {
            "vitamin_e": vitamin_e,
            "vitamin_d": vitamin_d,
            "vitamin_k": vitamin_k,
            "vitamin_c": vitamin_c,
            "vitamin_b1": vitamin_b1,
            "vitamin_b2": vitamin_b2,
            "vitamin_b9": vitamin_b9,
            "vitamin_b12": vitamin_b12,
            "vitamin_a": vitamin_a,
            "vitamin_b6": vitamin_b6,
        }
        response = requests.post(url, json=payload)
        self.last_response = response
        return response.json()

    def diagnosis(
            self,
            symptoms,
    ):
        url = f"{self.base_url}/diagnosis"
        payload = {"symptoms": symptoms}
        response = requests.post(url, json=payload)
        print(response.request.body)
        self.last_response = response
        print(response)
        return response.json()

