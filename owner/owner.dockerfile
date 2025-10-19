FROM python:3.9

# Copy needed files
COPY configuration.py /configuration.py
COPY models.py /models.py
copy utilities.py /utilities.py
COPY requirements.txt /requirements.txt
COPY owner_account.json /owner_account.json
COPY owner/owner.py /owner.py

# dependencies
RUN pip install -r requirements.txt

# Entrypoint
Entrypoint ["python", "owner.py"]
