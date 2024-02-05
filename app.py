import json
import os
import time
from dotenv import load_dotenv

import openai
import streamlit as st

from linkedin_scraper import scrape_linkedin_profile

# Load environment variables from .env file
load_dotenv()

assistant_id = os.getenv("ASSISTANT_ID")

# Initialize Streamlit session state variables
if "start_chat" not in st.session_state:
    st.session_state.start_chat = False
if "thread_id" not in st.session_state:
    st.session_state.thread_id = None
if "openai_api_key" not in st.session_state:
    st.session_state.openai_api_key = ""
# Add a new session state variable for analysis completion tracking
if "analysis_completed" not in st.session_state:
    st.session_state.analysis_completed = False

# Configure the Streamlit page
st.set_page_config(page_title="RateIn", page_icon=":computer:")

with st.sidebar:
    st.markdown("<h1 style='display: flex; align-items: center;'>RateIn <img src='https://www.pagetraffic.com/blog/wp-content/uploads/2022/09/linkedin-blue-logo-icon.png' alt='LinkedIn Logo' width='40' height='40'></h1>", unsafe_allow_html=True)
    #bullet points
    with st.expander("🚀 What does RateIn do?"):
        st.markdown("""
            - 🧐 **LinkedIn Profile Optimization:** Personalized, actionable advice for enhancing your profile.
            - 📚 **Specialized Knowledge:** Draws on a custom knowledge base tailored for LinkedIn profile improvements.
            - 💡 **Powered by OpenAI:** Leverages the Assistant's API with GPT-4 Turbo for analysis and conversation.
            - 🖼 **Vision Insights:** GPT-4 Vision for detailed feedback on profile pictures.
        """, unsafe_allow_html=True)


    st.session_state['openai_api_key'] = st.text_input("🔑 OpenAI API Key:", type="password")
    with st.expander("🎯 Job Preferences & Context (optional)"):
        job_preferences = st.text_area("Got any specific job-seeking goals? Let us know here!",
        placeholder="e.g., 'Software Engineer, entry-level, Tech industry and interested in AI.'")
    profile_url = st.text_input("🌐 Enter LinkedIn Profile URL:")

    # Check if both OpenAI API Key and LinkedIn Profile URL are provided
    if st.session_state['openai_api_key'] and profile_url:
        if st.button("Analyze"):
            st.session_state.start_chat = True
            openai.api_key = st.session_state.openai_api_key
            thread = openai.beta.threads.create()
            st.session_state.thread_id = thread.id
            st.session_state.analysis_requested = True
    else:
        # Optionally, display a message prompting the user to fill in all required fields
        st.warning("Friendly reminder - add your OpenAI API Key and LinkedIn Profile URL to kick things off!😎")

# Initialize or reset session state on page load
if 'init' not in st.session_state:
    st.session_state['init'] = True
    st.session_state.start_chat = False
    st.session_state.messages = []
    st.session_state.thread_id = None
    st.session_state.analysis_requested = False

def handle_custom_function(run, job_preferences=""):
    if run.status == 'requires_action' and run.required_action.type == 'submit_tool_outputs':
        for tool_call in run.required_action.submit_tool_outputs.tool_calls:
            if tool_call.function.name == "analyze_profile_picture":
                image_url = json.loads(tool_call.function.arguments)["image_url"]
                print(f"Analyzing image at URL: {image_url}")
                additional_context = ""
                if job_preferences:
                    additional_context += f"\n\n**ADDITIONAL** - If relevant for your analysis, please consider the following context about the user's job preferences: {job_preferences}"
                
                # Call GPT-4 Vision API to analyze the image
                vision_response = openai.chat.completions.create(
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
                                        "portrayal on LinkedIn. {additional_context}"
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
                vision_content = vision_response.choices[0].message.content
                print(f"Vision API response: {vision_content}")

                # Submit the output back to the Assistant
                openai.beta.threads.runs.submit_tool_outputs(
                    thread_id=run.thread_id,
                    run_id=run.id,
                    tool_outputs=[
                        {
                            'tool_call_id': tool_call.id,
                            'output': vision_response.choices[0].message.content
                        }
                    ]
                )
                print(f"Submitted vision analysis back to the assistant: {vision_content}")

# Main interaction logic
if st.session_state.start_chat:
    if "messages" not in st.session_state:
        st.session_state.messages = []
    
    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])

    if st.session_state.analysis_requested:
        with st.spinner('⏳🔍 Crunching the numbers - going to take a sec chief!😊'):
            # Process the LinkedIn profile URL
            formatted_text, image_url = scrape_linkedin_profile(profile_url)
            time.sleep(3)
            if formatted_text and image_url:
                # Instructions for analysis
                instructions = """
                                Provide an analysis/report of my LinkedIn profile below. Approach this task with professionalism and friendliness, ensure your recommendations is are both helpful and actionable. Provide detailed feedback for improvement. You can follow this structure:

                                1. **Profile Picture**: Begin with the profile picture. Assess its alignment. Suggest specific changes to enhance the first impression it makes, if needed.
                                2. **Headline and Summary**: Evaluate the clarity and impact of the headline and summary. How well do they communicate the individual's professional narrative and unique value proposition? Provide actionable advice to refine these elements, enhancing their appeal and coherence.
                                3. **Work Experience and Skills**: Delve into the work experience and skills sections. Identify the strengths and pinpoint areas that can benefit from greater detail or stronger examples of achievements. Recommend strategies to showcase expertise/skills more effectively.
                                4. **Educational Background and Volunteer Experience**: Analyze the education section and provide recommendations, if needed. Do the same for the Volunteer experience, if present. Advise on optimizing these areas to support the professional identity and narrative.
                                Each section should receive an assessment that contributes to an overall profile rating. Conclude with:
                                5. **Overall Quality Evaluation and Potential**: Rate the profile's current state out of 100, based on the coherence, presentation, and effectiveness of all sections combined - be as objective as you can, refrain from giving overly high ratings, unless the profile really is amazing. Then, estimate the potential score increase achievable by implementing your recommendations. Highlight the transformative impact of suggested changes, not just incrementally but in terms of elevating the profile's professional stature and networking potential.

                                Remember, your analysis should be comprehensive and nuanced, leveraging your expertise and any relevant external information from the files, where relevant.Address me directly and use the first person for a personal touch Let's evaluate this LinkedIn profile:
                            """
                # Concatenate instructions with the profile text and image URL for analysis
                analysis_request = f"{instructions}\n\n**HERE IS THE CONTENT FOR ANALYSIS**:\n- **Profile Text**: {formatted_text}\n- **Profile Image URL**: {image_url}"
                
                # Add job preferences to the analysis request if any
                if job_preferences:
                    analysis_request += f"\n\n**ADDITIONAL** - If relevant, please incorporate the following context about the job preferences of the user to tailor the recommendations: {job_preferences}"
                
                print(analysis_request)
            
                openai.beta.threads.messages.create(
                    thread_id=st.session_state.thread_id,
                    role="user",
                    content=analysis_request
                )
                    
                # Wait for the analysis to complete
                run = openai.beta.threads.runs.create(
                    thread_id=st.session_state.thread_id,
                    assistant_id=assistant_id,
                    instructions="Address me directly and use first person for a personal touch. Be helpful and approachable."
                )
                    
                while run.status != 'completed':
                    time.sleep(1)
                    run = openai.beta.threads.runs.retrieve(thread_id=st.session_state.thread_id, run_id=run.id)
                    if run.status == 'requires_action':
                        print("Function Calling")
                        handle_custom_function(run)

                # Fetch and display the analysis results
                messages = openai.beta.threads.messages.list(
                    thread_id=st.session_state.thread_id
                )

                # Filter and display messages for the current run
                for message in messages.data:
                    if message.run_id == run.id and message.role == "assistant":
                        st.session_state.messages.append({"role": "assistant", "content": message.content[0].text.value})
                        with st.chat_message("assistant"):
                            st.markdown(message.content[0].text.value)
                    
                # Mark the analysis as completed and ready for user follow-up
                st.session_state.analysis_requested = False
                st.session_state.analysis_completed = True


    # After completing the initial analysis, enable follow-up conversations
    if st.session_state.analysis_completed:
        user_input = st.chat_input("Ask me anything about improving your LinkedIn profile!")
        if user_input:  # If there's user input, process it
            # Append user input to messages for display
            st.session_state.messages.append({"role": "user", "content": user_input})
            with st.chat_message("user"):
                st.markdown(user_input)

            # Send the user input to OpenAI API as a new message in the thread
            openai.beta.threads.messages.create(
                thread_id=st.session_state.thread_id,
                role="user",
                content=user_input
            )

            # Wait for response
            run = openai.beta.threads.runs.create(
                thread_id=st.session_state.thread_id,
                assistant_id=assistant_id,
                instructions="Be helpful and approachable."
            )
                
            while run.status != 'completed':
                time.sleep(1)
                run = openai.beta.threads.runs.retrieve(thread_id=st.session_state.thread_id, run_id=run.id)

            # Fetch and display the analysis results
            messages = openai.beta.threads.messages.list(
                thread_id=st.session_state.thread_id
            )

            # Filter and display messages for the current run
            for message in messages.data:
                if message.run_id == run.id and message.role == "assistant":
                    st.session_state.messages.append({"role": "assistant", "content": message.content[0].text.value})
                    with st.chat_message("assistant"):
                        st.markdown(message.content[0].text.value)


# Display a message to start chat if not yet started
if not st.session_state.start_chat:
    st.markdown(
        """
        <h2 style='text-align: center;'>
            🚀 Ready to enhance your LinkedIn profile? <br>
            Drop your <img src='https://upcdn.io/FW25bBB/image/content/app_logos/485244ee-9158-4685-8f1e-d349e97b35e1.png?f=webp&w=1920&q=85&fit=shrink-cover' alt='LinkedIn Logo' width='45' height='45' style='border-radius: 15%'> API key and <img src='https://www.pagetraffic.com/blog/wp-content/uploads/2022/09/linkedin-blue-logo-icon.png' alt='LinkedIn Logo' width='40' height='40'> profile URL in the sidebar and let's dive in!
        </h2>
        """,
        unsafe_allow_html=True
    )