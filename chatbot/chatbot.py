from flask import Blueprint, request, jsonify, render_template
import random
import json
import os


# Create the blueprint
chatbot_bp = Blueprint('chatbot', __name__, template_folder="templates", static_folder="static")

# Load quiz questions from a local JSON file or create default ones
def load_questions():
    try:
        if os.path.exists('quiz_data.json'):
            with open('quiz_data.json', 'r') as f:
                return json.load(f)
        else:
            # Expanded default questions if file doesn't exist
            return {
                "general": [
                    {
                        "question": "What is the capital of France?",
                        "options": ["London", "Berlin", "Paris", "Madrid"],
                        "answer": "Paris",
                        "explanation": "Paris is the capital and most populous city of France."
                    },
                    {
                        "question": "Who wrote 'Romeo and Juliet'?",
                        "options": ["Charles Dickens", "William Shakespeare", "Jane Austen", "Mark Twain"],
                        "answer": "William Shakespeare",
                        "explanation": "William Shakespeare wrote 'Romeo and Juliet' around 1594-1596."
                    },
                    {
                        "question": "What is the chemical symbol for water?",
                        "options": ["Wa", "H2O", "O2H", "HO"],
                        "answer": "H2O",
                        "explanation": "Water consists of two hydrogen atoms bonded to one oxygen atom."
                    },
                    {
                        "question": "Which planet is known as the Red Planet?",
                        "options": ["Venus", "Mars", "Jupiter", "Mercury"],
                        "answer": "Mars",
                        "explanation": "Mars appears reddish due to iron oxide (rust) on its surface."
                    },
                    {
                        "question": "What is the largest ocean on Earth?",
                        "options": ["Atlantic Ocean", "Indian Ocean", "Arctic Ocean", "Pacific Ocean"],
                        "answer": "Pacific Ocean",
                        "explanation": "The Pacific Ocean is the largest and deepest ocean on Earth."
                    }
                ],
                "science": [
                    {
                        "question": "What is the largest planet in our solar system?",
                        "options": ["Earth", "Mars", "Jupiter", "Saturn"],
                        "answer": "Jupiter",
                        "explanation": "Jupiter is the fifth planet from the Sun and the largest in our solar system."
                    },
                    {
                        "question": "What is the hardest natural substance on Earth?",
                        "options": ["Gold", "Iron", "Diamond", "Titanium"],
                        "answer": "Diamond",
                        "explanation": "Diamond is the hardest naturally occurring substance found on Earth."
                    },
                    {
                        "question": "What is the chemical symbol for gold?",
                        "options": ["Go", "Gd", "Au", "Ag"],
                        "answer": "Au",
                        "explanation": "Gold's chemical symbol Au comes from the Latin word for gold, 'aurum'."
                    },
                    {
                        "question": "Which of these is NOT a state of matter?",
                        "options": ["Solid", "Liquid", "Gas", "Mineral"],
                        "answer": "Mineral",
                        "explanation": "The main states of matter are solid, liquid, gas, and plasma. Mineral is a type of solid."
                    },
                    {
                        "question": "What is the closest star to Earth?",
                        "options": ["Proxima Centauri", "The Sun", "Alpha Centauri", "Sirius"],
                        "answer": "The Sun",
                        "explanation": "The Sun is the star at the center of our Solar System and is the closest star to Earth."
                    }
                ],
                "math": [
                    {
                        "question": "What is the value of π (pi) to two decimal places?",
                        "options": ["3.14", "3.15", "3.16", "3.17"],
                        "answer": "3.14",
                        "explanation": "Pi (π) is approximately equal to 3.14159, or 3.14 when rounded to two decimal places."
                    },
                    {
                        "question": "What is the square root of 64?",
                        "options": ["6", "7", "8", "9"],
                        "answer": "8",
                        "explanation": "8 × 8 = 64, so the square root of 64 is 8."
                    },
                    {
                        "question": "What is 7 × 8?",
                        "options": ["54", "56", "58", "62"],
                        "answer": "56",
                        "explanation": "7 multiplied by 8 equals 56."
                    },
                    {
                        "question": "If a triangle has angles of 60°, 60°, and 60°, what type of triangle is it?",
                        "options": ["Scalene", "Isosceles", "Equilateral", "Right"],
                        "answer": "Equilateral",
                        "explanation": "An equilateral triangle has three equal sides and three equal angles of 60°."
                    },
                    {
                        "question": "What is the area of a square with sides of length 5?",
                        "options": ["20", "25", "10", "15"],
                        "answer": "25",
                        "explanation": "The area of a square is calculated by squaring the side length: 5² = 25."
                    }
                ],
                "history": [
                    {
                        "question": "Which ancient civilization built the pyramids of Giza?",
                        "options": ["Romans", "Greeks", "Egyptians", "Mayans"],
                        "answer": "Egyptians",
                        "explanation": "The Great Pyramids of Giza were built by the ancient Egyptians as tombs for pharaohs."
                    },
                    {
                        "question": "In what year did World War II end?",
                        "options": ["1943", "1945", "1947", "1950"],
                        "answer": "1945",
                        "explanation": "World War II ended in 1945 with the surrender of Germany in May and Japan in September."
                    },
                    {
                        "question": "Who was the first person to step on the moon?",
                        "options": ["Buzz Aldrin", "Neil Armstrong", "Yuri Gagarin", "John Glenn"],
                        "answer": "Neil Armstrong",
                        "explanation": "Neil Armstrong was the first person to walk on the moon on July 20, 1969."
                    },
                    {
                        "question": "Which empire was ruled by Genghis Khan?",
                        "options": ["Roman Empire", "Ottoman Empire", "Mongol Empire", "Byzantine Empire"],
                        "answer": "Mongol Empire",
                        "explanation": "Genghis Khan founded and ruled the Mongol Empire, one of the largest empires in history."
                    }
                ]
            }
    except Exception as e:
        print(f"Error loading questions: {e}")
        return {}

# Simple knowledge base for chatbot
knowledge_base = {
    "hello": ["Hello! How can I help you today?", "Hi there! Would you like to learn something new?", "Greetings! How can I assist you with learning?"],
    "how are you": ["I'm doing well, thanks for asking! Would you like to try a quiz?", "I'm great! Ready to help you learn something new today."],
    "name": ["I'm your friendly learning assistant. You can ask me questions or try a quiz!", "I'm a quiz bot designed to help you learn new things."],
    "help": ["I can help you learn through quizzes! Try saying 'quiz me', 'science quiz', 'math quiz', or 'history quiz'. You can also ask me simple questions."],
    "bye": ["Goodbye! Come back anytime to learn more!", "See you later! Hope you learned something new today!"],
    "thank": ["You're welcome! Is there anything else you'd like to learn?", "Happy to help! Would you like another quiz?"],
    "weather": ["I don't have access to real-time weather data, but I can quiz you on weather phenomena if you'd like!"],
    "time": ["I don't have access to the current time, but I can help you learn about timekeeping systems if you're interested!"]
}

# Load quiz data
quiz_data = load_questions()

@chatbot_bp.route('/')
def home():
    return render_template('index.html')

@chatbot_bp.route('/chat', methods=['POST'])
def chat():
    print("Chat endpoint called!")  # Debug statement
    user_message = request.json.get('message', '').strip().lower()
    
    if not user_message:
        return jsonify({'response': "Please ask me a question or try 'quiz me' to start a quiz!"})
    
    # Print for debugging
    print(f"Received message: {user_message}")
    
    # Handle quiz requests
    if "quiz" in user_message:
        category = "general"  # Default category
        
        # Check for specific category request
        categories = ["science", "math", "history", "general"]
        for cat in categories:
            if cat in user_message:
                category = cat
                break
            
        print(f"Quiz category: {category}")
        
        if category in quiz_data and quiz_data[category]:
            question = random.choice(quiz_data[category])
            response = {
                'type': 'quiz',
                'question': question['question'],
                'options': question['options'],
                'answer': question['answer'],
                'explanation': question['explanation']
            }
            return jsonify(response)
        else:
            return jsonify({'response': f"Sorry, I don't have any questions for {category} yet."})
    
    # Handle chat responses from knowledge base
    for key, responses in knowledge_base.items():
        if key in user_message:
            return jsonify({'response': random.choice(responses)})
    
    # Handle factual questions with predefined answers
    if "what is" in user_message or "who is" in user_message or "how does" in user_message:
        # Simple facts about various topics
        facts = [
            "The Earth revolves around the Sun once every 365.25 days.",
            "Water boils at 100 degrees Celsius at sea level.",
            "The human body has 206 bones.",
            "Light travels at approximately 299,792,458 meters per second in a vacuum.",
            "The Great Wall of China is over 13,000 miles long.",
            "I might not have the exact answer, but I'd be happy to quiz you on related topics!",
            "That's an interesting question! Try a quiz to learn more about similar topics."
        ]
        return jsonify({'response': random.choice(facts)})
        
    # Default response
    default_responses = [
        "I can help you learn through quizzes! Try saying 'quiz me', 'science quiz', 'math quiz', or 'history quiz'.",
        "Would you like to test your knowledge? Say 'quiz me' to get started!",
        "I'm here to help you learn! Try asking for a quiz in science, math, history, or general knowledge.",
        "Not sure what you're looking for. Try 'help' to see what I can do."
    ]
    
    return jsonify({'response': random.choice(default_responses)})