
# Daohq Quest Backend Service

This repository contains a FastAPI service for managing quests, including endpoints for completing quests, retrieving the last completed quest, and synchronizing story quests from an uploaded file.

## Table of Contents

- [Features](#features)
- [Installation](#installation)
- [Usage](#usage)
- [API Endpoints](#api-endpoints)

## Features

- Complete quests, including daily and non-daily quests.
- Retrieve the last completed quest for a user.
- Synchronize quests by uploading a JSON file.
- Reset daily quest completions at midnight UTC.

## Installation

1. Create a virtual environment and activate it:

   ```bash
   python3 -m venv venv
   source venv/bin/activate  # On Windows use `venv\Scripts\activate`
   ```

2. Install the dependencies:

   ```bash
   pip install -r requirements.txt
   ```

3. Run the FastAPI server:

   ```bash
   uvicorn main:app
   ```

## Usage

- The API documentation is available at `/docs` when the server is running.
- You can interact with the API using tools like `curl`, Postman or send requests directly from /docs.
