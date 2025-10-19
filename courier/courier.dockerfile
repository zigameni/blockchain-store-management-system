FROM python:3.9

# Copy necessary files
COPY configuration.py /configuration.py
COPY models.py /models.py
COPY utilities.py /utilities.py
COPY requirements.txt /requirements.txt
COPY courier/courier.py /courier.py

# Install dependencies
RUN pip install -r requirements.txt

# Set entrypoint
ENTRYPOINT ["python", "courier.py"]