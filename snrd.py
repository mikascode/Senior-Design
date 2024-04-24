import tkinter as tk
import os
import speech_recognition as sr
import threading
from openai import OpenAI

# Initialize the OpenAI client with your API key
client = OpenAI(api_key="")

interview_questions = {
    "tech": [
        "Can you explain the difference between HTTP and HTTPS?",
        "What is a REST API, and how do you use it?"
    ],
    "hr": [
        "Tell me about a time when you faced a challenging situation and how you handled it.",
        "What are your greatest strengths and weaknesses?"
    ]
}
current_questions = []
question_index = 0
interview_started = False
responses = []  # To store user responses

def generate_response(client, messages):
    completion = client.chat.completions.create(
        model="gpt-3.5-turbo",
        messages=messages
    )
    return completion.choices[0].message

def send_message():
    global question_index, interview_started, current_questions, responses
    user_input = user_input_field.get().strip()
    if user_input == '':
        return
    user_input_field.delete(0, tk.END)
    display_message(user_input, "You")

    if interview_started and question_index < len(current_questions):
        responses.append(user_input)  # Store the response
        if question_index == len(current_questions) - 1:
            end_interview()  # Move to ending the interview if it's the last question
        else:
            question_index += 1
            ask_next_question()
    elif not interview_started and user_input in interview_questions:
        current_questions = interview_questions[user_input]
        interview_started = True
        speak("Let's start the interview.")
        ask_next_question()

def end_interview():
    global interview_started
    for i, response in enumerate(responses):
        question = current_questions[i]
        evaluate_response(response, question)  # Provide feedback for each response
    farewell = "That concludes our mock interview. Best of luck with your real interview!"
    speak(farewell)
    display_message(farewell, "Assistant")
    interview_started = False  # Reset the interview state
    responses.clear()  # Clear responses after feedback

def evaluate_response(response, question):
    job_type = "tech"  # Example placeholder, should dynamically set based on interview type
    prompt = f"How would an interviewer evaluate this response for a {job_type} job to this question: '{question}'\n\n'{response}'"
    feedback = generate_response(client, [{"role": "system", "content": prompt}])
    display_message(feedback, "Feedback")

def display_message(message, speaker):
    chat_history.config(state=tk.NORMAL)
    chat_history.insert(tk.END, f"{speaker}: {message}\n")
    chat_history.config(state=tk.DISABLED)

def speak(text):
    os.system(f'say "{text.replace('"', '\\"')}"')

def recognize_speech():
    recognizer = sr.Recognizer()
    try:
        with sr.Microphone() as source:
            recognizer.adjust_for_ambient_noise(source)
            audio = recognizer.listen(source)
        text = recognizer.recognize_google(audio)
        user_input_field.insert(tk.END, text)
        send_message()
    except sr.UnknownValueError:
        display_message("Could not understand audio", "Error")
    except sr.RequestError as e:
        display_message(f"Could not request results; {e}", "Error")
    except Exception as e:
        display_message(f"An error occurred: {e}", "Error")

def recognize_speech_thread():
    threading.Thread(target=recognize_speech).start()

def start_interview():
    greet = "Hey, it's Digital Coach! What type of interview are you preparing for today? (tech or hr)"
    speak(greet)
    display_message(greet, "Assistant")

def ask_next_question():
    if question_index < len(current_questions):
        question = current_questions[question_index]
        speak(question)
        display_message(question, "Assistant")

# GUI Setup Code
root = tk.Tk()
root.title("Interview Assistant Chatbot")
chat_frame = tk.Frame(root)
chat_frame.pack(padx=10, pady=10)
scrollbar = tk.Scrollbar(chat_frame)
scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
chat_history = tk.Text(chat_frame, wrap=tk.WORD, yscrollcommand=scrollbar.set)
chat_history.pack(expand=True, fill=tk.BOTH)
chat_history.config(state=tk.DISABLED)
scrollbar.config(command=chat_history.yview)
input_frame = tk.Frame(root)
input_frame.pack(padx=10, pady=(0, 10))
user_input_field = tk.Entry(input_frame, width=50)
user_input_field.pack(side=tk.LEFT, padx=(0, 5))
send_button = tk.Button(input_frame, text="Send", command=send_message)
send_button.pack(side=tk.LEFT)
recognize_button = tk.Button(input_frame, text="Speak", command=recognize_speech_thread)
recognize_button.pack(side=tk.LEFT, padx=(5, 0))
root.after(1000, start_interview)
root.mainloop()
