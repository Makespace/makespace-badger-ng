#!/usr/bin/env python3
import json
import requests

class Database():
    def __init__(self, base_url):
        self.base_url = base_url

    def close(self):
        pass

    def initialise(self):
        raise NotImplementedError()

    def lookup(self, tag):
        r = requests.get(self.base_url + "/api/v1/member/" + tag.hex())
        if r.status_code != 200:
            raise RuntimeError(f"request failed: {r.status_code}")

        result = r.json()
        return result["name"], result["contact_data"]

    def update(self, tag, name, comment):
        payload = { "fob_id": tag.hex(), "name": name, "contact_data": comment }

        r = requests.put(self.base_url + "/api/v1/member/" + tag.hex(), json=payload)

        if r.status_code != 200:
            raise RuntimeError(f"request failed: {r.status_code}")

    def delete(self, tag):
        r = requests.delete(self.base_url + "/api/v1/member/" + tag.hex())
        if r.status_code != 204:
            raise RuntimeError(f"request failed: {r.status_code}")

    def insert(self, tag, name, comment):
        payload = { "fob_id": tag.hex(), "name": name, "contact_data": comment }

        r = requests.post(self.base_url + "/api/v1/member", json=payload)

        if r.status_code != 201:
            raise RuntimeError(f"request failed: {r.status_code}")
