# MDBS : Movie Database system

A personalized movie recommendation and watchlist application built using Flask, Firebase, and the TMDB API. This project allows users to sign up, log in, search for movies, and manage a personal watchlist. It integrates Firebase Authentication and Firestore for user profiles while retrieving movie data from The Movie Database (TMDB).

## Table of Contents

- [Project Overview](#project-overview)
- [Features](#features)
- [Technologies Used](#technologies-used)
- [Setup and Installation](#setup-and-installation)
- [Firebase Setup and Service Key Instructions](#firebase-setup-and-service-key-instructions)
- [Configuration](#configuration)
- [Running the Application](#running-the-application)
- [Troubleshooting](#troubleshooting)
- [Contributing](#contributing)
- [License](#license)

## Project Overview

My Movie App is a web application that enables users to:

- **Sign Up and Customize Profiles:**  
  Create an account with email and password, choose favorite genres, upload a profile picture, and set personal details.
  
- **Search and Discover Movies:**  
  Search for movies via the TMDB API and receive recommendations based on favorite genres, actors, and titles.
  
- **Manage a Watchlist:**  
  Add and remove movies from a personal watchlist stored in the user's Firebase Firestore profile.

## Features

- **User Authentication:** Secure sign-up and login flows powered by Firebase.
- **User Profile Management:** Customize profile with name, profile picture, and personal preferences.
- **Movie Search:** Utilize TMDB's API to search and display movie data.
- **Personalized Recommendations:** Combine genres, actors, and movie titles from your session to create custom recommendations.
- **Responsive UI:** Modern design with reusable templates and CSS styling.

## Technologies Used

- **Backend:** Python, Flask
- **Database & Authentication:** Firebase (Firebase Admin SDK for Firestore and service account authentication, Firebase Auth REST API for login)
- **External API:** The Movie Database (TMDB) API
- **Frontend:** HTML, CSS, JavaScript (with Jinja2 templating)
- **Environment Management:** python-dotenv for environment variables

## Setup and Installation

1. **Clone the Repository:**

   ```bash
   git clone https://github.com/yourusername/my-movie-app.git
   cd my-movie-app
   ```
2. Create and Activate a Virtual Environment:

    On macOS/Linux:
   
    ```bash
    python3 -m venv venv
    source venv/bin/activate
    ```
    On Windows:
   
   ```bash
   python -m venv venv
   venv\Scripts\activate
   ```
4. Install Dependencies:

   ```bash
   pip install -r requirements.txt
   ```
   
## Firebase Setup and Service Key Instructions

1. Create a Firebase Account and Project
   - Visit the Firebase Console:
     Go to Firebase Console and sign in with your Google account.

   - Create a New Project:
     Click "Add project" and follow the prompts. Provide a project name (e.g., "My Movie App") and configure any settings you prefer.

2. Add a Web App to the Firebase Project
   - Register Your App:
     In the Firebase Console project overview, click on "Project settings" (gear icon) and under "Your apps", click the </> (Web) icon.

   - Set Up Your App:
     Follow the steps to register your web app. You will be provided with a Web API Key. Save this key – you'll need it for authenticating via Firebase Auth REST API (see Configuration).

3. Enable Email/Password Authentication
   - Navigate to Authentication:
     Click on "Build" in the left-hand menu, then select "Authentication".

   - Enable Sign-In Method:
     Under the "Sign-in method" tab, enable "Email/Password" authentication.

4. Generate and Download Your Service Key
   - Go to Service Accounts:
     In your Firebase Console, click on the gear icon next to "Project Overview" and select "Project settings". Then select the "Service accounts" tab.

   - Generate New Private Key:
     Click "Generate new private key". A JSON file will be downloaded automatically.
     Important: Rename this file to serviceAccountKey.json.

   - Place the File Securely:
     Move the serviceAccountKey.json file to the root directory of your project.
     
## Configuration

1. Firebase Initialization
   In your code (firebase_service.py), use the service key for Firebase initialization:

   ```bash
   import os
   from firebase_admin import credentials, initialize_app

   # Set the path to your service account key file
   service_key_path = "serviceAccountKey.json"  # Update the path if needed

   cred = credentials.Certificate(service_key_path)
   initialize_app(cred)
   ```
2. Firebase API Key
   Replace the placeholder in your code (login route in main.py) with your Web API Key noted during app registration:
   
   ```bash
   api_key = "YOUR_FIREBASE_API_KEY_HERE"  # Replace this with the Firebase Web API Key
   ```
3. Running the Application
   After completing the configuration steps, start the Flask development server:

   ```bash
   python main.py
   ```
   Then, visit http://127.0.0.1:5000 in your browser to see your app in action.
   
   
