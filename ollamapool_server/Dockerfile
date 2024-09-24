FROM python

WORKDIR /usr/src/app

# Install Python dependencies
COPY requirements.txt ./
RUN pip install --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

# Copy the source code
COPY src/ ./

CMD ["python3", "./server.py"]
