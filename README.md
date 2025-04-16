# My Movie App

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

   
