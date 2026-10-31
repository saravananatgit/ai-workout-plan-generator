
import streamlit as st
import os

from dotenv import load_dotenv
from groq import Groq


# =====================================================
# 1. PAGE CONFIGURATION
# =====================================================

st.set_page_config(
    page_title="AI Workout Plan Generator",
    page_icon="💪",
    layout="centered"
)


# =====================================================
# 2. LOAD ENVIRONMENT VARIABLES
# =====================================================

load_dotenv()

groq_api_key = os.getenv("GROQ_API_KEY")

if not groq_api_key:
    st.error("Groq API key is missing. Please check your .env file.")
    st.stop()


# =====================================================
# 3. INITIALIZE GROQ CLIENT
# =====================================================

client = Groq(
    api_key=groq_api_key
)


# =====================================================
# 4. SYSTEM PROMPT
# =====================================================

def build_system_prompt() -> str:
    """
    Creates system instructions for the workout planning AI.
    """

    return """
    You are an experienced and responsible fitness planning assistant.

    Your task is to create personalized weekly workout plans.

    Follow these rules strictly:

    1. FITNESS GOAL
       - Design exercises according to the user's fitness goal.
       - Build muscle, lose fat, general fitness or endurance.

    2. EXPERIENCE LEVEL
       - Beginner: Simple exercises and manageable volume.
       - Intermediate: Moderate exercise complexity.
       - Advanced: More challenging but practical workouts.

    3. EQUIPMENT CONSTRAINTS
       - No equipment: Bodyweight exercises only.
       - Home dumbbells: Bodyweight and dumbbell exercises only.
       - Full gym: Gym equipment and free weights are allowed.
       - Never recommend equipment the user does not have.

    4. AVAILABLE DAYS
       - Create exactly the requested number of workout days.
       - Include appropriate recovery days.
       - Do not schedule additional workout days.

    5. INJURIES AND LIMITATIONS
       - Respect all user-provided physical limitations.
       - Avoid movements that may aggravate the stated limitation.
       - Do not diagnose medical conditions.
       - Do not prescribe rehabilitation exercises.
       - Do not assume an exercise is medically safe.
       - If limitations are mentioned, include a safety disclaimer.
       - Recommend consulting a qualified healthcare professional
         when appropriate.

    6. OUTPUT FORMAT
       Return the plan using Markdown.

       Include:
       - Fitness goal
       - Experience level
       - Weekly overview
       - Day-by-day workout breakdown
       - Exercise names
       - Sets and repetitions
       - Rest periods
       - Warm-up recommendations
       - Cool-down recommendations
       - Recovery guidance

    7. QUALITY
       - Avoid generic workout recommendations.
       - Make the plan realistic and practical.
       - Do not add exercises that violate user constraints.
       - If information is insufficient, state reasonable assumptions.

    Return only the workout plan.
    """


# =====================================================
# 5. USER PROMPT
# =====================================================

def build_user_prompt(
    fitness_goal: str,
    experience_level: str,
    days_per_week: int,
    equipment: str,
    injuries: str
) -> str:
    """
    Builds a personalized workout request using user inputs.
    """

    return f"""
    Create a personalized weekly workout plan using these details.

    USER FITNESS PROFILE:

    Fitness Goal: {fitness_goal}

    Experience Level: {experience_level}

    Available Workout Days: {days_per_week} days per week

    Equipment Available: {equipment}

    Injuries or Physical Limitations:
    {injuries.strip() if injuries.strip() else "None provided"}

    REQUIREMENTS:

    1. Create exactly {days_per_week} workout days.
    2. Respect the selected fitness goal.
    3. Respect the user's experience level.
    4. Use only the available equipment.
    5. Respect all stated physical limitations.
    6. Include exercise names, sets, repetitions and rest periods.
    7. Include recovery days in the weekly overview.
    8. Make the plan easy to understand and follow.

    Generate a practical weekly workout plan for this user.
    """


# =====================================================
# 6. GROQ API INTEGRATION
# =====================================================

def generate_workout_plan(
    system_prompt: str,
    user_prompt: str
) -> str:
    """
    Sends prompts to Groq and returns the AI-generated
    workout plan.
    """

    try:

        response = client.chat.completions.create(
            model="openai/gpt-oss-120b",

            messages=[
                {
                    "role": "system",
                    "content": system_prompt
                },
                {
                    "role": "user",
                    "content": user_prompt
                }
            ],

            temperature=0.7,
            max_completion_tokens=4000
        )

        workout_plan = response.choices[0].message.content

        if not workout_plan or not workout_plan.strip():
            raise ValueError("The AI returned an empty response.")

        return workout_plan

    except Exception as e:

        st.error(
            "Unable to generate your workout plan. "
            "Please try again."
        )

        st.exception(e)

        return ""


# =====================================================
# 7. STREAMLIT UI
# =====================================================

st.title("💪 AI Workout Plan Generator")

st.write(
    "Create a personalized weekly workout plan "
    "based on your fitness goals and available equipment."
)

st.divider()

st.header("Tell us about yourself")


# =====================================================
# 8. COLLECT USER INPUTS
# =====================================================

with st.form("workout_form"):

    # Fitness goal
    fitness_goal = st.selectbox(
        "What is your fitness goal?",
        [
            "Build muscle",
            "Lose fat",
            "General fitness",
            "Improve endurance"
        ]
    )

    # Experience level
    experience_level = st.selectbox(
        "What is your experience level?",
        [
            "Beginner",
            "Intermediate",
            "Advanced"
        ]
    )

    # Available workout days
    days_per_week = st.slider(
        "How many days can you work out per week?",
        min_value=1,
        max_value=7,
        value=3
    )

    # Equipment
    equipment = st.selectbox(
        "What equipment do you have access to?",
        [
            "No equipment",
            "Home dumbbells",
            "Full gym"
        ]
    )

    # Injuries or limitations
    injuries = st.text_area(
        "Any injuries or physical limitations? (Optional)",
        placeholder=(
            "Example: Bad knees, back pain, "
            "no overhead pressing..."
        )
    )

    # Submit button
    submitted = st.form_submit_button(
        "Generate Workout Plan",
        use_container_width=True
    )


# =====================================================
# 9. PROCESS FORM SUBMISSION
# =====================================================

if submitted:

    # Input validation
    if not 1 <= days_per_week <= 7:

        st.error("Please select between 1 and 7 days.")

    else:

        # Build prompts
        system_prompt = build_system_prompt()

        user_prompt = build_user_prompt(
            fitness_goal=fitness_goal,
            experience_level=experience_level,
            days_per_week=days_per_week,
            equipment=equipment,
            injuries=injuries
        )

        # Display user profile
        st.success(
            "Fitness information collected successfully!"
        )

        st.subheader("Your Fitness Profile")

        st.write(f"**Goal:** {fitness_goal}")
        st.write(f"**Experience:** {experience_level}")
        st.write(f"**Days:** {days_per_week}")
        st.write(f"**Equipment:** {equipment}")
        st.write(
            f"**Limitations:** {injuries or 'None specified'}"
        )

        # Display prompts for debugging
        with st.expander("View generated prompts"):

            st.write("System Prompt")
            st.code(system_prompt)

            st.write("User Prompt")
            st.code(user_prompt)

        # Generate workout plan
        st.divider()

        st.subheader("Your Personalized Workout Plan")

        with st.spinner(
            "Groq AI is generating your workout plan..."
        ):

            workout_plan = generate_workout_plan(
                system_prompt=system_prompt,
                user_prompt=user_prompt
            )

        # Display AI response
        if workout_plan:

            st.markdown(workout_plan)

            # Download workout plan
            st.download_button(
                label="Download Workout Plan",
                data=workout_plan,
                file_name="my_workout_plan.md",
                mime="text/markdown"
            )
