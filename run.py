#!/usr/bin/env python

from datetime import datetime
from pathlib import Path

from cryptography.x509 import load_pem_x509_certificate
from requests import Session

BASE_URL = "https://kernighan.hitchhikerprod.com/api/states/sensor.certificate"

with open("/root/.hassio-key", "rt", encoding="utf-8") as key_file:
    bearer_token = key_file.read()

session = Session()
session.headers.update({
    'Authorization': f"Bearer {bearer_token}",
    'Content-type': 'application/json',
})

for dirname in Path("/etc/letsencrypt/live").glob("*.com"):
    site = dirname.parts[-1]
    sensor_name = site.replace(".", "_")
    with open(dirname / "cert.pem", "rb") as cert_file:
        cert = load_pem_x509_certificate(cert_file.read())

    valid = cert.not_valid_before <= datetime.now() <= cert.not_valid_after
    body = {
        "state": valid,
        "attributes": {
            "not_valid_before": cert.not_valid_before.isoformat(),
            "not_valid_after": cert.not_valid_after.isoformat()
        }
    }

    response = session.post(f"{BASE_URL}_{sensor_name}")
    if not response.ok:
        print(f"Error setting {sensor_name}")
