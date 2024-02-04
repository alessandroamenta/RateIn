# LinkedIn Profile Analyzer 🚀💼

Welcome to the LinkedIn Profile Analyzer! This tool not only reads your profile but also visually analyzes your profile picture to provide detailed feedback and actionable suggestions for elevating a LinkedIn profile.

## How It Works

Our app leverages the power of OpenAI's GPT-4 and GPT-4 Vision models through the Assistants API, integrating both text and visual analysis capabilities. Here's a quick overview:

- `app.py`: The frontend of the application, built with Streamlit. It manages the user interface, facilitating easy interaction and displaying insights directly to you.
- `main.py`: Initializes the OpenAI Assistant specifically designed for LinkedIn profile optimization, incorporating retrieval from documents and custom function calling.
- `linkedin_scraper.py`: Gathers data from your LinkedIn profile URL, preparing it for comprehensive analysis by the Assistant.

### Simple Steps for Users:
1. Input your LinkedIn profile URL.
2. The app scrapes your profile data, readying it for in-depth analysis.
3. Our custom AI Assistant, enhanced with vision capabilities, examines both the content and the profile picture, ensuring a holistic profile evaluation.

## Highlights

- **OpenAI Assistants API**: Using the Assistants API for textual analysis and recommendations.
- **Custom Function & GPT-4 Vision**: A custom function taps into GPT-4 Vision for an insightful critique of profile pictures, evaluating professional presentation and suitability.
- **Retrieval and Function Calling**: Seamlessly integrates document retrieval for enriched context and calls custom functions for specialized tasks like image analysis.

## Quick Start

1. **Clone and Setup**: Clone this repo and install dependencies (`pip install -r requirements.txt`).
2. **Run the App**: Use `streamlit run app.py` to start the application.
3. **Input and Analyze**: Simply enter your OpenAI API key and LinkedIn profile URL in the sidebar, then press "Analyze" to see the magic happen.

## Contributing

We welcome contributions! If you have suggestions or improvements, please fork the repo, commit your updates, and submit a pull request.

## Tech

- **Streamlit**: For creating the web app interface.
- **OpenAI API**: Leveraging Assistants API, including GPT-4 for textual analysis and GPT-4 Vision for image analysis.
- **Python**: For backend logic and integration with the OpenAI API.


Made with ❤️ and Python.
