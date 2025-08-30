import streamlit as st
import pandas as pd
import google.generativeai as genai
import os
from gtts import gTTS
import io
from datetime import datetime

st.markdown(
    """
    <style>
    /* Increase font size for general text (paragraphs) */
    /* Increase font size for headings */
   
    /* Increase font size for specific Streamlit widgets, e.g., text input labels */
    div[data-testid="stTextInput"] label p {
        font-size: 20px;
    }
    /* Increase font size for Streamlit buttons */
    div[data-testid="stButton"] button {
        font-size: 20px;
        padding: 10px 20px; /* Increase button size */
    }    
    /*caption font size for tables */
    div[data-testid="stTable"] caption {
        font-size: 20px;
    }
    /* Increase font size for Streamlit selectbox */
    div[data-testid="stSelectbox"] label p {
        font-size: 18px;
    }
    /dashboard font size for Streamlit multiselect */
    div[data-testid="stMultiSelect"] label p {
        font-size: 18px;
    }
    
    input[type="radio"] {
        transform: scale(2);  /* 1.5 = 150% size */
        margin-right: 8px;
    }

    /* Increase label font size for all radio buttons */
    label {
        font-size: 20px !important;
    }
    label {
        font-size: 20px !important; /* Increase label font size */
    }

    /* Increase font size for expander labels */
    
/* Increase size of radio buttons globally */
    div[data-testid="stRadio"] input[type="radio"] {
        transform: scale(1.8); /* Circle size */
        margin-right: 10px;
    }

    /* Increase label font size for all radio options */
    div[data-testid="stRadio"] label {
        font-size: 20px !important;
    }

    /* Increase question/heading font size for the radio group */
    div[data-testid="stRadio"] p {
        font-size: 20px;    }
    /* Increase font size for code blocks */
    pre code {
        font-size: 20px;
    }

    input[type="text"] {
    width: 250px !important;
    max-width: 100%;
}
    </style>
    """,
    unsafe_allow_html=True
)


ADMIN_USERNAME = st.secrets["passwords"]["adminusername"]
ADMIN_PASSWORD = st.secrets["passwords"]["adminpassword"]
QUESTION_FILE = st.secrets["passwords"]["questionFile"]
RESULT_FILE = st.secrets["passwords"]["resultFile"]
STUDENT_FILE = st.secrets["passwords"]["studentFile"]

genai.configure(api_key=st.secrets["passwords"]["GEMINI_API_KEY"])
model = genai.GenerativeModel("gemini-2.0-flash")

if "user_role" not in st.session_state:
    st.session_state.user_role = None
if "student_username" not in st.session_state:
    st.session_state.student_username = None

def student_signup(username, password, roll_no, email):
    if os.path.exists(STUDENT_FILE):
        df = pd.read_csv(STUDENT_FILE)
        if username in df["Username"].values:
            return False, "Username already exists."
        df = pd.concat([df, pd.DataFrame([{"Username": username, "Password": password, "Roll Number": roll_no, "Email": email}])], ignore_index=True)
    else:
        df = pd.DataFrame([{"Username": username, "Password": password, "Roll Number": roll_no, "Email": email}])
    df.to_csv(STUDENT_FILE, index=False)
    return True, "Sign up successful! Please sign in."

def student_signin(username, password):
    username = username.strip()
    password = password.strip()
    if os.path.exists(STUDENT_FILE):
        df = pd.read_csv(STUDENT_FILE)
        match = df[(df["Username"] == username) & (df["Password"] == password)]
        if not match.empty:
            roll_no = match.iloc[0]["Roll Number"]
            email = match.iloc[0]["Email"]
            return True, "Sign in successful!", roll_no, email
        else:
            return False, "Invalid username or password.",None, None
    else:
        return False, "No students registered yet."
    
def tra_score():
    english_text = st.text_input("Enter English text to translate:")
    if english_text.strip():
        prompt = f"Translate the following English text to German. Avoid Suggestions:\n\n{english_text}"
        response = model.generate_content(prompt)
        german_translation = response.text.strip()
        st.session_state["german_translation"] = german_translation

        # Generate and store German audio
        tts = gTTS(german_translation, lang="de") #Converts the german_translation text into speech.gTTS: A Python library and CLI tool to interface with Google Translate’s Text-to-Speech API lang="de": Specifies the language as German.
        audio_bytes = io.BytesIO() # Creates a bytes buffer to hold the audio data
        tts.write_to_fp(audio_bytes) # Writes the audio data to the bytes buffer
        st.session_state["german_audio"] = audio_bytes.getvalue() 
        
        # Save audio to file
        if "german_audio" in st.session_state:
            original_path = "german_translation_audio.mp3"
            with open(original_path, "wb") as f:
                f.write(st.session_state["german_audio"])
            st.session_state["original_path"] = original_path
        

        # Show translation and audio
        if "german_translation" in st.session_state:
            st.markdown("**German Translation:**")
            st.success(st.session_state["german_translation"])
            st.audio(st.session_state["german_audio"], format="audio/mp3")

        # # Record audio
        # duration = 5
        # sample_rate = 44100
        # if st.button("Start Recording"):
        #     st.info("Recording... Speak now!")
        #     recording = sd.rec(int(duration * sample_rate), samplerate=sample_rate, channels=1)
        #     sd.wait()
        #     st.success("Recording finished!")

        #     compare_path = "user_recording.wav"
        #     write(compare_path, sample_rate, recording)
        #     st.audio(compare_path, format="audio/wav")
        #     #st.success(f"Recording saved to: {os.path.abspath(compare_path)}")
        #     st.session_state["compare_path"] = compare_path
        # # Transcribe and compare
        # if "german_translation" in st.session_state:
        #     file_to_compare = st.session_state.get("compare_path", None)
        #     original_path = st.session_state.get("original_path", "german_translation_audio.mp3")
        #     sample_rate = 16000  # Set your expected sample rate

        #     if not file_to_compare or not os.path.exists(file_to_compare):
        #         st.warning("No valid speech file uploaded for comparison.")
        #     elif not os.path.exists(original_path):
        #         st.warning("Original German translation audio file not found. Please translate first.")
        #     else:
        #         # Step 1: Transcribe the uploaded audio
        #         st.info("Transcribing your speech...")
        #         model_whisper = whisper.load_model("base")
        #         result = model_whisper.transcribe(file_to_compare, language="de")
        #         user_spoken = result["text"].strip()

        #         if user_spoken == "":
        #             st.error("The uploaded file appears to be empty or silent. Please try again.")
        #         else:
        #             st.markdown(f"**You said:** {user_spoken}")

        #             # Step 2: Compute audio similarity
        #             weights = {
        #                 'zcr_similarity': 0.2,
        #                 'rhythm_similarity': 0.2,
        #                 'chroma_similarity': 0.2,
        #                 'energy_envelope_similarity': 0.1,
        #                 'spectral_contrast_similarity': 0.1,
        #                 'perceptual_similarity': 0.2
        #             }

        #             audio_similarity = AudioSimilarity(
        #                 original_path=original_path,
        #                 compare_path=file_to_compare,
        #                 sample_rate=sample_rate,
        #                 weights=weights,
        #                 verbose=True,
        #                 sample_size=1
        #             )

        #             similarity_score = audio_similarity.stent_weighted_audio_similarity(metrics='all')

        #             # Display Scores
        #             st.markdown("### 🎧 Audio Similarity Scores")
        #             st.markdown(f"**SWASS Similarity Score:** {similarity_score.get('swass', 0):.2f} / 1.00")
        #             for key, value in similarity_score.items():
        #                 if key != "swass":
        #                     st.markdown(f"**{key.replace('_', ' ').title()}:** {value:.2f}")

if st.session_state.user_role is None:
    st.title("Welcome to the Quiz Demo!")
    role = st.radio("Login As:", ["Admin", "Student"])
    if role == "Admin":
        st.subheader("🔐 Admin Login")
        username = st.text_input("Username")
        password = st.text_input("Password", type="password")
        if st.button("Login"):
            if username == ADMIN_USERNAME and password == ADMIN_PASSWORD:
                st.session_state.user_role = "admin"
                st.success("Admin login successful!")
                st.rerun()
            else:
                st.error("Invalid credentials")
    elif role == "Student":
        st.subheader("🧑‍🎓 Student Login / Sign Up")
        auth_mode = st.radio("Choose Action", ["Sign In", "Sign Up"])
        username = st.text_input("Student Username", key="student_username_input").strip()
        password = st.text_input("Student Password", type="password", key="student_password_input").strip()
        roll_no = st.text_input("Roll Number", key="student_rollno_input").strip() if auth_mode == "Sign Up" else ""
        email = st.text_input("Email", key="student_email_input").strip() if auth_mode == "Sign Up" else ""

        if auth_mode == "Sign Up":
            if st.button("Sign Up"):
                ok, msg = student_signup(username, password, roll_no, email)
                if ok:
                    st.success(msg)
                else:
                    st.error(msg)
        else:
            if st.button("Sign In"):
                ok, msg, roll_no, email = student_signin(username, password)
                if ok:
                    st.session_state.user_role = "student"
                    st.session_state.student_username = username
                    st.session_state.roll_no = roll_no
                    st.session_state.email = email
                    st.success(msg)
                    st.rerun()
                else:
                    st.error("Invalid username or password.")

# Admin Dashboard
if st.session_state.user_role == "admin":
    st.set_page_config(page_title="Admin Dashboard", layout="wide")
    st.sidebar.title("Admin Navigation")
    admin_page = st.sidebar.radio("Go to", ["Change Quiz Questions", "Analytics","Logout"])
    st.title("🛠️ Admin Dashboard")

    if admin_page == "Change Quiz Questions":
        st.header("Upload/Change Quiz Questions")
        uploaded_file = st.file_uploader("Upload Question Bank")
        if uploaded_file:
            result_df = pd.read_csv(uploaded_file,encoding='utf-8')
            st.dataframe(result_df)
            result_df.to_csv("questions.csv", index=False)
            result_df.columns = result_df.columns.str.strip()
            required_cols = {"Question", "Option A", "Option B", "Option C", "Option D", "Answer"}
            if required_cols.issubset(result_df.columns):
                result_df.to_excel(QUESTION_FILE, index=False)
                st.success("✅ Question file uploaded and saved.")
            else:
                st.error("Excel file missing required columns.")

    elif admin_page == "Analytics":
        st.header("Quiz Analytics")
        if os.path.exists(RESULT_FILE):
            result_df = pd.read_excel(RESULT_FILE)
            st.dataframe(result_df)
            st.write("Average Score:", result_df["Score"].mean())
            st.bar_chart(result_df["Score"])
        else:
            st.info("No quiz results found.")
    elif admin_page == "Logout":
        for key in list(st.session_state.keys()):
            del st.session_state[key]
        st.session_state.user_role = None
        st.session_state.student_username = None        
        st.success("Logged out successfully.")   
        st.rerun()
# Student Dashboard
if st.session_state.user_role == "student":
    st.set_page_config(page_title="Student Dashboard", layout="wide")
    st.sidebar.title(f"Welcome, {st.session_state.student_username}")
    student_page = st.sidebar.radio("Go to", ["English to German Translation", "Take Quiz","Transcript Video","Translate German Handwritting", "See Score","Logout"])
    st.title("🎓 Student Dashboard")
    roll_no = st.session_state.get("roll_no","")
    email = st.session_state.get("email", "")
    if student_page == "Logout":
        for key in list(st.session_state.keys()):
            del st.session_state[key]
        st.session_state.user_role = None
        st.session_state.student_username = None
        st.success("Logged out successfully.")
        st.rerun()  # Or st.rerun() if using latest Streamlit
    elif student_page == "English to German Translation":
        st.write("### English to German Translation ")
        st.write("Translate English text to German.")
        tra_score()           
    elif student_page == "Take Quiz":
        st.header("Take Quiz")
        QUESTIONS_PER_PAGE = 10
        TOTAL_QUESTIONS = 50

        # Pagination state
        if "quiz_page" not in st.session_state:
            st.session_state.quiz_page = 0
        if "quiz_answers" not in st.session_state:
            st.session_state.quiz_answers = {}

        roll_no = st.session_state.get("roll_no", "")   
        already_attempted = False
        previous_score = None

        if os.path.exists(RESULT_FILE):
            result_df = pd.read_excel(RESULT_FILE)
            result_df.columns = result_df.columns.str.strip()
            match = result_df[
                (result_df["Roll Number"] == st.session_state.roll_no) | 
                (result_df["Email"] == st.session_state.email)
            ]
            if not match.empty:
                already_attempted = True
                previous_score = match.iloc[-1]["Score"]

        if os.path.exists(QUESTION_FILE):
            if st.session_state.roll_no and st.session_state.email:
                # Add Refresh Quiz button
                if st.button("🔄 Refresh Quiz"):
                    df = pd.read_csv("questions.csv")
                    st.session_state.quiz_questions = df.sample(TOTAL_QUESTIONS).reset_index(drop=True)
                    st.session_state.quiz_page = 0
                    st.success("A new set of questions has been generated!")

                # Generate questions if not already present
                if "quiz_questions" not in st.session_state:
                    df = pd.read_csv("questions.csv")
                    st.session_state.quiz_questions = df.sample(TOTAL_QUESTIONS).reset_index(drop=True)
                quiz_questions = st.session_state.quiz_questions

                # Pagination logic
                page = st.session_state.quiz_page
                start = page * QUESTIONS_PER_PAGE
                end = min(start + QUESTIONS_PER_PAGE, TOTAL_QUESTIONS)
                questions = quiz_questions.iloc[start:end]

                st.subheader(f"📚 Questions {start+1} to {end} of {TOTAL_QUESTIONS}")
                user_answers = st.session_state.quiz_answers

                for i, row in questions.iterrows():
                    q_idx = start + i
                    st.markdown(f"**Q{q_idx+1}: {row['Question']}**")
                    if 'Image' in row and pd.notna(row['Image']) and str(row['Image']).strip() != "":
                        st.image(row['Image'], caption="Question Image", width=300)
                    q_type = row.get("Type", "MCQ")
                    if q_type == "MCQ":
                        options = {
                            "A": row["Option A"],
                            "B": row["Option B"],
                            "C": row["Option C"],
                            "D": row["Option D"]
                        }
                        user_answers[q_idx] = st.radio(
                            label="Your Answer:",
                            options=list(options.keys()),
                            format_func=lambda x: f"{x}. {options[x]}",
                            key=f"quiz_option_{q_idx}"
                        )
                    else:  # Text question
                        cols = st.columns([1, 5])
                        with cols[0]:
                            user_answers[q_idx] = st.text_input(
                                "",
                                key=f"text_answer_{q_idx}",
                                max_chars=20
                            )
                    st.markdown("---")

                # Navigation buttons
                nav_cols = st.columns(3)
                with nav_cols[0]:
                    if page > 0:
                        if st.button("⬅️ Previous Page"):
                            st.session_state.quiz_page -= 1
                            st.rerun()
                with nav_cols[2]:
                    if end < TOTAL_QUESTIONS:
                        if st.button("Next Page ➡️"):
                            st.session_state.quiz_page += 1
                            st.rerun()

                # Submit button only on last page
                if end == TOTAL_QUESTIONS:
                    if st.button("Submit Quiz"):
                        score = 0
                        feedback = []
                        for i, row in quiz_questions.iterrows():
                            correct = str(row["Answer"]).strip().upper()
                            user_ans = user_answers.get(i, "")
                            q_type = row.get("Type", "MCQ")
                            if q_type == "MCQ":
                                is_correct = user_ans.upper() == correct
                                your_answer = f"{user_ans}. {row.get(f'Option {user_ans.upper()}', '')}"
                                correct_answer = f"{correct}. {row.get(f'Option {correct}', '')}"
                            else:
                                is_correct = str(user_ans).strip().lower() == correct.lower()
                                your_answer = user_ans
                                correct_answer = row["Answer"]
                            if is_correct:
                                score += 1
                            feedback.append({
                                "Question": row["Question"],
                                "Your Answer": your_answer,
                                "Correct Answer": correct_answer,
                                "Result": "✅ Correct" if is_correct else "❌ Wrong"
                            })

                        st.success(f"🎯 Your Score: {score} / {len(quiz_questions)}")
                        st.markdown("### Answer Feedback")
                        st.dataframe(pd.DataFrame(feedback))

                        # Prepare new record
                        new_record = {
                            "Roll Number": roll_no,
                            "Email": email,
                            "Score": score,
                            "Date & Time": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                        }

                        # Load or create result DataFrame
                        if os.path.exists(RESULT_FILE):
                            result_df = pd.read_excel(RESULT_FILE)
                            result_df = pd.concat([result_df, pd.DataFrame([new_record])], ignore_index=True)
                        else:
                            result_df = pd.DataFrame([new_record])

                        result_df.to_excel(RESULT_FILE, index=False)
                        st.success("✅ Result recorded successfully.")
                        del st.session_state.quiz_questions
                        del st.session_state.quiz_answers
                        st.session_state.quiz_page = 0
            else:
                st.info("Please enter your Roll Number and Email to start the quiz.")
        else:
            st.warning("⚠️ No question file found. Please contact the admin.")
    elif student_page == "Transcript Video":
        st.header("Transcript Your Video")
    elif student_page == "Translate German Handwritting":
        st.header("Translate German Handwriting")        
    elif student_page == "See Score":
        st.header("See Your Score")
        roll_no = st.session_state.roll_no
        email = st.session_state.email

        # Show quiz scores without Roll Number
        if os.path.exists(RESULT_FILE):
            result_df = pd.read_excel(RESULT_FILE)
            match = result_df[
                (result_df["Roll Number"] == roll_no) | (result_df["Email"] == email)
            ]
            if not match.empty:
                display_df = match.drop(columns=["Roll Number"], errors="ignore")
                st.dataframe(display_df)
            else:
                st.info("No score found for your account.")
        else:
            st.info("No quiz results found yet.")

        st.subheader("Video Transcripts")
        TRANSCRIPT_FILE = "transcripts.xlsx"
        if os.path.exists(TRANSCRIPT_FILE):
            transcript_df = pd.read_excel(TRANSCRIPT_FILE)
            transcript_match = transcript_df[
                (transcript_df["Roll Number"] == roll_no) | (transcript_df["Username"] == st.session_state.student_username)
            ]
            if not transcript_match.empty:
                display_transcript = transcript_match.drop(columns=["Roll Number", "Username"], errors="ignore")
                st.dataframe(display_transcript)
            else:
                st.info("No transcript found for your account.")
        else:
            st.info("No transcript submissions found yet.")

st.markdown("""
<script>
window.addEventListener('blur', function() {
    alert('You switched tabs or minimized the browser! Please stay on the quiz page.');
});
window.addEventListener('beforeunload', function (e) {
    e.preventDefault();
    e.returnValue = '';
});
</script>
""", unsafe_allow_html=True)