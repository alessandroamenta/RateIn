import os
import requests

def scrape_linkedin_profile(profile_url):
    username = extract_username(profile_url)
    rapidapi_key = os.getenv('RAPIDAPI_KEY')

    url = "https://linkedin-data-api.p.rapidapi.com/"
    querystring = {"username": username}

    headers = {
        "X-RapidAPI-Key": rapidapi_key,
        "X-RapidAPI-Host": "linkedin-data-api.p.rapidapi.com"
    }

    response = requests.get(url, headers=headers, params=querystring)
    if response.status_code == 200:
        profile_data = response.json()
        formatted_text, profile_image_url = format_data_for_gpt(profile_data)
        return formatted_text, profile_image_url
		#print(formatted_data)
        #return formatted_data
    else:
        print("Failed to fetch profile data.")
        return None, None

def extract_username(linkedin_url):
    username = linkedin_url.split('/')[-1] or linkedin_url.split('/')[-2]
    return username.strip()

def format_data_for_gpt(profile_data):

	# Extract the profile image URL
    profile_image_url = profile_data.get('profilePicture', '')
    # Personal Information
    firstName = profile_data.get('firstName', 'No first name')
    lastName = profile_data.get('lastName', 'No last name')
    fullName = f"{firstName} {lastName}"
    headline = profile_data.get('headline', 'No headline provided')
    summary = profile_data.get('summary', 'No summary provided')
    #profilePicture = profile_data.get('profilePicture', 'No profile picture URL')
    location = profile_data.get('geo', {}).get('full', 'No location provided')

    formatted_text = f"Name: {fullName}\nHeadline: {headline}\nLocation: {location}\nSummary: {summary}\n"

    # Professional Experience
    formatted_text += "\nExperience:\n"
    for position in profile_data.get('position', []):
        company = position.get('companyName', 'No company name')
        title = position.get('title', 'No title')
        jobLocation = position.get('location', 'No location')
        jobDescription = position.get('description', 'No description').replace('\n', ' ')
        formatted_text += f"- {title} at {company}, {jobLocation}. {jobDescription}\n"

    # Education
    formatted_text += "\nEducation:\n"
    for education in profile_data.get('educations', []):
        school = education.get('schoolName', 'No school name')
        degree = education.get('degree', 'No degree')
        field = education.get('fieldOfStudy', 'No field of study')
        grade = education.get('grade', 'No grade')
        eduDescription = education.get('description', 'No description').replace('\n', ' ')
        formatted_text += f"- {degree} in {field} from {school}, Grade: {grade}. {eduDescription}\n"

    # Skills
    formatted_text += "\nSkills:\n"
    for skill in profile_data.get('skills', []):
        skillName = skill.get('name', 'No skill name')
        formatted_text += f"- {skillName}\n"

    # Languages
    formatted_text += "\nLanguages:\n"
    for language in profile_data.get('languages', []):
        langName = language.get('name', 'No language name')
        proficiency = language.get('proficiency', 'No proficiency level')
        formatted_text += f"- {langName} ({proficiency})\n"

    # Certifications
    formatted_text += "\nCertifications:\n"
    for certification in profile_data.get('certifications', []):
        certName = certification.get('name', 'No certification name')
        formatted_text += f"- {certName}\n"

    return formatted_text, profile_image_url
