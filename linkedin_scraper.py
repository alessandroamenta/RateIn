import os
import requests
import argparse
import logging
from dotenv import load_dotenv

# Set up basic configuration for logging
logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(levelname)s - %(message)s')

load_dotenv()
rapidapi_key = os.getenv('RAPIDAPI_KEY')

def main(profile_url):
    formatted_text, profile_image_url = scrape_linkedin_profile(profile_url)
    if formatted_text:  # Just check if formatted_text is not None or empty
        logging.info("Profile Data Scraped Successfully:")
        logging.info(formatted_text)
        if profile_image_url:
            logging.info(f"Profile Image URL: {profile_image_url}")
        else:
            logging.info("No Profile Image URL found.")
    else:
        logging.error("Failed to scrape profile data or profile is incomplete/private.")

def scrape_linkedin_profile(profile_url):
    username = extract_username(profile_url)
    if not rapidapi_key:
        logging.error("RapidAPI key not found. Please set the RAPIDAPI_KEY environment variable.")
        return None, None

    url = "https://linkedin-data-api.p.rapidapi.com/"
    querystring = {"username": username}

    headers = {
        "X-RapidAPI-Key": rapidapi_key,
        "X-RapidAPI-Host": "linkedin-data-api.p.rapidapi.com"
    }

    try:
        response = requests.get(url, headers=headers, params=querystring)
        if response.status_code == 200:
            profile_data = response.json()
            logging.debug(f"API Response: {profile_data}")
            formatted_text, profile_image_url = format_data_for_gpt(profile_data)
            # Additional logging to confirm data formatting
            logging.debug(f"Formatted Text: {formatted_text[:500]}")
            logging.debug(f"Profile Image URL: {profile_image_url}")
            return formatted_text, profile_image_url
        else:
            logging.error(f"Failed to fetch profile data. Status Code: {response.status_code}")
            return None, None
    except Exception as e:
        logging.exception("An error occurred while fetching the profile data.")
        return None, None

def extract_username(linkedin_url):
    username = linkedin_url.split('/')[-1] if linkedin_url.split('/')[-1] else linkedin_url.split('/')[-2]
    return username.strip()

import logging

def safe_get_list(data, key):
    """
    Safely get a list value from a dictionary. Returns an empty list if the key is not found or the value is None.
    """
    value = data.get(key)
    return [] if value is None else value

def safe_get_value(data, key, default=''):
    """Safely get a single value from a dictionary. Returns a default value if the key is not found or the value is None."""
    return data.get(key) if data.get(key) is not None else default

def format_data_for_gpt(profile_data):
    try:
        # Extract the profile image URL safely
        profile_image_url = safe_get_value(profile_data, 'profilePicture', '')

        # Personal Information with safe retrieval
        firstName = safe_get_value(profile_data, 'firstName', 'No first name')
        lastName = safe_get_value(profile_data, 'lastName', 'No last name')
        fullName = f"{firstName} {lastName}"
        headline = safe_get_value(profile_data, 'headline', 'No headline provided')
        summary = safe_get_value(profile_data, 'summary', 'No summary provided')
        location = safe_get_value(profile_data.get('geo', {}), 'full', 'No location provided')

        formatted_text = f"Name: {fullName}\nHeadline: {headline}\nLocation: {location}\nSummary: {summary}\n"

        # Professional Experience
        formatted_text += "Experience:\n"
        for position in safe_get_list(profile_data, 'position'):
            company = position.get('companyName', 'No company name')
            title = position.get('title', 'No title')
            jobLocation = position.get('location', 'No location')
            jobDescription = position.get('description', 'No description').replace('\n', ' ')
            formatted_text += f"- {title} at {company}, {jobLocation}. {jobDescription}\n"

        # Education
        formatted_text += "Education:\n"
        for education in safe_get_list(profile_data, 'educations'):
            school = education.get('schoolName', 'No school name')
            degree = education.get('degree', 'No degree')
            field = education.get('fieldOfStudy', 'No field of study')
            grade = education.get('grade', 'No grade')
            eduDescription = education.get('description', 'No description').replace('\n', ' ')
            formatted_text += f"- {degree} in {field} from {school}, Grade: {grade}. {eduDescription}\n"

        # Skills
        formatted_text += "Skills:\n"
        for skill in safe_get_list(profile_data, 'skills'):
            skillName = skill.get('name', 'No skill name')
            formatted_text += f"- {skillName}\n"

        # Languages
        formatted_text += "Languages:\n"
        languages = safe_get_list(profile_data, 'languages')
        if languages:
            for language in languages:
                langName = language.get('name', 'No language name')
                proficiency = language.get('proficiency', 'No proficiency level')
                formatted_text += f"- {langName} ({proficiency})\n"
        else:
            formatted_text += "- No languages provided\n"

        # Certifications
        formatted_text += "Certifications:\n"
        for certification in safe_get_list(profile_data, 'certifications'):
            certName = certification.get('name', 'No certification name')
            formatted_text += f"- {certName}\n"

        return formatted_text, profile_image_url

    except Exception as e:
        logging.exception("An error occurred during data formatting.")
        return None, None


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Scrape LinkedIn profile data.")
    parser.add_argument("profile_url", help="LinkedIn profile URL to scrape.")
    args = parser.parse_args()

    main(args.profile_url)