FROM apify/actor-python:3.11

# Install Playwright
RUN pip install playwright && python -m playwright install

# Copy package files
COPY requirements.txt ./

# Install dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy source code
COPY . ./

# Run the actor
CMD ["python", "src/main.py"]
