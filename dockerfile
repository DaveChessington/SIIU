# Use the official Python runtime image
FROM python:3.13-slim

# Create the app directory
RUN mkdir /app
 
# Set the working directory inside the container
WORKDIR /app

# Prevents python from writing .pyc files
ENV PYTHONDONTWRITEBYTECODE=1

# Forces python to send logs and errors directly to the console
ENV PYTHONUNBUFFERED=1

# Upgrade pip and install dependencies
RUN pip install --upgrade pip 

# Copy the requirements file first (better caching)
COPY requirements.txt /app/
 
# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy app code
COPY . /app/

# Copy the entrypoint.sh file
COPY entrypoint.sh /app/

# Make sure entrypoint.sh is executable iside the container
RUN chmod +x /app/entrypoint.sh

# Expose Django's port
EXPOSE 8000

# # Entrypoint (startup) file
# ENTRYPOINT ["/app/entrypoint.sh"]

