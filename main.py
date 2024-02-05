import json
import os
from dotenv import load_dotenv

from openai import OpenAI

load_dotenv() 

api_key = os.environ.get("OPENAI_API_KEY")
client = OpenAI(api_key=api_key)

# Define the function for creating the Assistant
def create_linkedin_profile_analyzer():
    # List of PDF files
    pdf_files = [
        "file1.pdf",
        "file2.pdf",
        "file3.pdf",
        "file4.pdf",
        "file5.pdf",
        "file6.pdf"
    ]

    # Path to the directory containing the PDFs
    pdf_directory = "knowledge"  # Adjust the path as necessary

    # Upload documents for Retrieval
    file_ids = []
    for pdf_file in pdf_files:
        file_path = os.path.join(pdf_directory, pdf_file)
        with open(file_path, "rb") as file_data:
            file = client.files.create(file=file_data, purpose="assistants")
            file_ids.append(file.id)

    # Create the Assistant with necessary tools
    assistant = client.beta.assistants.create(
        name="LinkedIn Profile Analyzer",
        instructions = (
            "You are an expert in LinkedIn profile optimization, tasked with providing a comprehensive analysis "
            "of a user's LinkedIn profile, analyze it thoroughly. Be helpful, "
            "and maintain a casual, approachable yet professional tone. Remember to address the user directly and use the first person.\n"
            "- analyze_profile_picture, when the image url of the profile is given."
        ),
        model="gpt-4-turbo-preview",
        tools=[
            {"type": "retrieval", "file_ids": file_ids},
            {"type": "function", "function": function_json}
        ]
    )
    return assistant

# Define the function to create thread and run
def create_thread_and_run(assistant_id, user_message):
    thread = client.beta.threads.create()
    client.beta.threads.messages.create(
        thread_id=thread.id, role="user", content=user_message
    )
    return client.beta.threads.runs.create(
        thread_id=thread.id,
        assistant_id=assistant_id,
    )

# Define the custom function for image analysis
function_json = {
    "name": "analyze_profile_picture",
    "description": "Analyze this LinkedIn profile picture provided through the image URL. Examine its appropriateness for a professional LinkedIn profile by focusing on the presentation, expression and body language, composition and setting (including background), and the quality of the image. Ensure your analysis determines whether these aspects meet professional standards and offer specific recommendations for any needed improvements to enhance the profile's professional image. Overall, describe the image in detail.",
    "parameters": {
        "type": "object",
        "properties": {
            "image_url": {"type": "string", "description": "URL of the profile picture"}
        },
        "required": ["image_url"]
    }
}


def handle_custom_function(run):
    if run.status == 'requires_action' and run.required_action.type == 'submit_tool_outputs':
        for tool_call in run.required_action.submit_tool_outputs.tool_calls:
            if tool_call.function.name == "analyze_profile_picture":
                image_url = json.loads(tool_call.function.arguments)["image_url"]
                
                # Call GPT-4 Vision API to analyze the image
                vision_response = client.chat.completions.create(
                    model='gpt-4-vision-preview',
                    messages=[
                        {
                        "role": "user",
                        "content": [
                            {
                            "type": "text", 
                            "text": (
                                        "Analyze this LinkedIn profile picture. Provide an analysis focusing on its "
                                        "appropriateness and effectiveness for a LinkedIn profile. Consider the following aspects:\n\n"
                                        "1. Presentation: Evaluate the subject's attire and grooming. Does it align with professional standards suitable for "
                                        "their industry or field?\n"
                                        "2. Expression and Body Language: Assess the subject's facial expression and body language. Does it project confidence, "
                                        "approachability, and professionalism?\n"
                                        "3. Composition and Setting: Comment on the composition of the photograph, including the background. Is it distraction-free "
                                        "and does it enhance the subject's professional image?\n"
                                        "4. Quality and Lighting: Evaluate the quality of the photograph, including lighting and clarity. Does the image quality "
                                        "uphold professional standards?\n\n"
                                        "Provide recommendations for improvement if necessary, highlighting aspects that could enhance the subject's professional "
                                        "portrayal on LinkedIn."
                                    )
                            },
                            {
                            "type": "image_url",
                            "image_url": {
                                "url": image_url,
                            },
                            },
                        ],
                        }
                    ],
                    max_tokens=400
                )


                # Submit the output back to the Assistant
                client.beta.threads.runs.submit_tool_outputs(
                    thread_id=run.thread_id,
                    run_id=run.id,
                    tool_outputs=[
                        {
                            'tool_call_id': tool_call.id,
                            'output': vision_response.choices[0].message.content
                        }
                    ]
                )


# Main function to create the assistant
def main():
    assistant = create_linkedin_profile_analyzer()

if __name__ == "__main__":
    main()