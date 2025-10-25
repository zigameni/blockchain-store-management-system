FROM python:3.9

# Copy needed files
COPY configuration.py /configuration.py
COPY models.py /models.py
COPY utilities.py /utilities.py
COPY requirements.txt /requirements.txt
COPY owner_account.json /owner_account.json
COPY blockchain/output/OrderPayment.abi /blockchain/output/OrderPayment.abi
COPY blockchain/output/OrderPayment.bin /blockchain/output/OrderPayment.bin
COPY owner/owner.py /owner.py

# dependencies
RUN pip install -r requirements.txt

# Entrypoint
Entrypoint ["python", "owner.py"]
