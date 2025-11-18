import streamlit as st
import random
import time
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime
import json
import os

# Set page configuration FIRST
st.set_page_config(
    page_title="Trivia Quiz",
    page_icon="🎯",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Initialize session state variables
if 'quiz_started' not in st.session_state:
    st.session_state.quiz_started = False
if 'current_question' not in st.session_state:
    st.session_state.current_question = 0
if 'score' not in st.session_state:
    st.session_state.score = 0
if 'user_answers' not in st.session_state:
    st.session_state.user_answers = []
if 'quiz_questions' not in st.session_state:
    st.session_state.quiz_questions = []
if 'show_results' not in st.session_state:
    st.session_state.show_results = False
if 'answer_submitted' not in st.session_state:
    st.session_state.answer_submitted = False
if 'current_user' not in st.session_state:
    st.session_state.current_user = None
if 'users' not in st.session_state:
    st.session_state.users = {}
if 'global_leaderboard' not in st.session_state:
    st.session_state.global_leaderboard = []
if 'selected_theme' not in st.session_state:
    st.session_state.selected_theme = "Light"
if 'start_time' not in st.session_state:
    st.session_state.start_time = None
if 'question_start_time' not in st.session_state:
    st.session_state.question_start_time = None

# Leaderboard file path
LEADERBOARD_FILE = "leaderboard.json"

def load_leaderboard():
    """Load leaderboard data from JSON file"""
    try:
        if os.path.exists(LEADERBOARD_FILE):
            with open(LEADERBOARD_FILE, 'r') as f:
                data = json.load(f)
                return data.get('users', {}), data.get('leaderboard', [])
    except Exception as e:
        st.error(f"Error loading leaderboard: {e}")
    return {}, []

def save_leaderboard():
    """Save leaderboard data to JSON file"""
    try:
        data = {
            'users': st.session_state.users,
            'leaderboard': st.session_state.global_leaderboard,
            'last_updated': datetime.now().isoformat()
        }
        with open(LEADERBOARD_FILE, 'w') as f:
            json.dump(data, f, indent=2)
    except Exception as e:
        st.error(f"Error saving leaderboard: {e}")

def update_leaderboard(username, score_percentage, total_questions, total_time, category):
    """Update leaderboard with new quiz result"""
    # Update user statistics
    if username not in st.session_state.users:
        st.session_state.users[username] = {
            'total_quizzes': 0,
            'total_score': 0,
            'average_score': 0,
            'best_score': 0,
            'total_questions_answered': 0,
            'total_time_spent': 0,
            'first_quiz': datetime.now().isoformat(),
            'last_quiz': datetime.now().isoformat()
        }
    
    user = st.session_state.users[username]
    user['total_quizzes'] += 1
    user['total_score'] += score_percentage
    user['average_score'] = user['total_score'] / user['total_quizzes']
    user['total_questions_answered'] += total_questions
    user['total_time_spent'] += total_time
    user['last_quiz'] = datetime.now().isoformat()
    
    if score_percentage > user['best_score']:
        user['best_score'] = score_percentage
    
    # Create leaderboard entry
    leaderboard_entry = {
        'username': username,
        'score': st.session_state.score,
        'total_questions': total_questions,
        'percentage': score_percentage,
        'time_taken': total_time,
        'category': category,
        'timestamp': datetime.now().isoformat(),
        'date': datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    }
    
    # Add to global leaderboard
    st.session_state.global_leaderboard.append(leaderboard_entry)
    
    # Sort leaderboard by percentage (descending) and time (ascending for same scores)
    st.session_state.global_leaderboard.sort(
        key=lambda x: (-x['percentage'], x['time_taken'])
    )
    
    # Keep only top 50 entries to prevent file from getting too large
    st.session_state.global_leaderboard = st.session_state.global_leaderboard[:50]
    
    # Save to file
    save_leaderboard()

def display_statistics():
    """Display user statistics similar to the screenshot"""
    if not st.session_state.current_user or st.session_state.current_user not in st.session_state.users:
        st.info("Complete a quiz to see your statistics!")
        return
    
    user_stats = st.session_state.users[st.session_state.current_user]
    
    st.header("📊 Your Statistics")
    
    # Create a container for the statistics
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.markdown(f"""
        <div style="background: white; padding: 20px; border-radius: 10px; text-align: center; box-shadow: 0 2px 4px rgba(0,0,0,0.1);">
            <h3 style="color: #2c3e50; margin-bottom: 10px;">Total Quizzes</h3>
            <h1 style="color: #1a1a1a; margin: 0; font-size: 2.5rem;">{user_stats['total_quizzes']}</h1>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        st.markdown(f"""
        <div style="background: white; padding: 20px; border-radius: 10px; text-align: center; box-shadow: 0 2px 4px rgba(0,0,0,0.1);">
            <h3 style="color: #2c3e50; margin-bottom: 10px;">Average Score</h3>
            <h1 style="color: #1a1a1a; margin: 0; font-size: 2.5rem;">{user_stats['average_score']:.1f}%</h1>
        </div>
        """, unsafe_allow_html=True)
    
    with col3:
        st.markdown(f"""
        <div style="background: white; padding: 20px; border-radius: 10px; text-align: center; box-shadow: 0 2px 4px rgba(0,0,0,0.1);">
            <h3 style="color: #2c3e50; margin-bottom: 10px;">Best Score</h3>
            <h1 style="color: #1a1a1a; margin: 0; font-size: 2.5rem;">{user_stats['best_score']:.1f}%</h1>
        </div>
        """, unsafe_allow_html=True)
    
    with col4:
        st.markdown(f"""
        <div style="background: white; padding: 20px; border-radius: 10px; text-align: center; box-shadow: 0 2px 4px rgba(0,0,0,0.1);">
            <h3 style="color: #2c3e50; margin-bottom: 10px;">Questions Answered</h3>
            <h1 style="color: #1a1a1a; margin: 0; font-size: 2.5rem;">{user_stats['total_questions_answered']}</h1>
        </div>
        """, unsafe_allow_html=True)

def display_leaderboard():
    """Display comprehensive leaderboard"""
    st.header("🏆 Global Leaderboard")
    
    if not st.session_state.global_leaderboard:
        st.info("No quiz results yet! Complete a quiz to appear on the leaderboard.")
        return
    
    # Create a DataFrame for easier display
    leaderboard_data = []
    for i, entry in enumerate(st.session_state.global_leaderboard[:20]):  # Show top 20
        leaderboard_data.append({
            'Rank': i + 1,
            'Username': entry['username'],
            'Score': f"{entry['score']}/{entry['total_questions']}",
            'Percentage': f"{entry['percentage']:.1f}%",
            'Time': f"{entry['time_taken']:.1f}s",
            'Category': entry['category'],
            'Date': entry['date']
        })
    
    df = pd.DataFrame(leaderboard_data)
    
    # Display top 3 with medals
    col1, col2, col3 = st.columns(3)
    
    if len(st.session_state.global_leaderboard) >= 1:
        with col1:
            top_user = st.session_state.global_leaderboard[0]
            st.markdown(f"""
            <div style="text-align: center; padding: 20px; background: linear-gradient(135deg, #FFD700 0%, #FFEC8B 100%); 
                        border-radius: 15px; margin: 10px; box-shadow: 0 4px 8px rgba(0,0,0,0.2);">
                <h2>🥇</h2>
                <h3>{top_user['username']}</h3>
                <h4>{top_user['percentage']:.1f}%</h4>
                <p>{top_user['score']}/{top_user['total_questions']}</p>
                <p>{top_user['time_taken']:.1f}s</p>
            </div>
            """, unsafe_allow_html=True)
    
    if len(st.session_state.global_leaderboard) >= 2:
        with col2:
            second_user = st.session_state.global_leaderboard[1]
            st.markdown(f"""
            <div style="text-align: center; padding: 20px; background: linear-gradient(135deg, #C0C0C0 0%, #E8E8E8 100%); 
                        border-radius: 15px; margin: 10px; box-shadow: 0 4px 8px rgba(0,0,0,0.2);">
                <h2>🥈</h2>
                <h3>{second_user['username']}</h3>
                <h4>{second_user['percentage']:.1f}%</h4>
                <p>{second_user['score']}/{second_user['total_questions']}</p>
                <p>{second_user['time_taken']:.1f}s</p>
            </div>
            """, unsafe_allow_html=True)
    
    if len(st.session_state.global_leaderboard) >= 3:
        with col3:
            third_user = st.session_state.global_leaderboard[2]
            st.markdown(f"""
            <div style="text-align: center; padding: 20px; background: linear-gradient(135deg, #CD7F32 0%, #E8B886 100%); 
                        border-radius: 15px; margin: 10px; box-shadow: 0 4px 8px rgba(0,0,0,0.2);">
                <h2>🥉</h2>
                <h3>{third_user['username']}</h3>
                <h4>{third_user['percentage']:.1f}%</h4>
                <p>{third_user['score']}/{third_user['total_questions']}</p>
                <p>{third_user['time_taken']:.1f}s</p>
            </div>
            """, unsafe_allow_html=True)
    
    # Full leaderboard table
    st.subheader("📊 Full Leaderboard")
    st.dataframe(df, use_container_width=True, hide_index=True)
    
    # Display user statistics
    display_statistics()

# Load leaderboard data at startup
if not st.session_state.users and not st.session_state.global_leaderboard:
    st.session_state.users, st.session_state.global_leaderboard = load_leaderboard()

# Apply theme directly without complex functions
if st.session_state.selected_theme == "Light":
    st.markdown("""
    <style>
    .stApp {
        background-color: #FF8C00 !important;
        background: linear-gradient(135deg, #FF8C00 0%, #FFA500 100%) !important;
    }
    </style>
    """, unsafe_allow_html=True)

# Custom CSS with dark text for analytics
st.markdown("""
<style>
    .main-header {
        font-size: 3rem;
        color: white !important;
        text-align: center;
        margin-bottom: 2rem;
        font-weight: bold;
        text-shadow: 2px 2px 4px rgba(0,0,0,0.5);
    }
    .quiz-card {
        background-color: white;
        padding: 2rem;
        border-radius: 15px;
        border-left: 5px solid #FF4B4B;
        margin: 1rem 0;
        box-shadow: 0 4px 6px rgba(0,0,0,0.1);
    }
    .result-box {
        text-align: center;
        padding: 2rem;
        border-radius: 15px;
        margin: 1rem 0;
        border-left: 5px solid #28a745;
        background: white;
        box-shadow: 0 4px 6px rgba(0,0,0,0.1);
    }
    .stat-card {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        padding: 1.5rem;
        border-radius: 10px;
        text-align: center;
        margin: 0.5rem;
        box-shadow: 0 4px 6px rgba(0,0,0,0.1);
    }
    .analytics-card {
        background: white;
        padding: 1.5rem;
        border-radius: 10px;
        margin: 0.5rem 0;
        box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        border-left: 4px solid #4CAF50;
    }
    /* Dark text for all analytics content */
    .analytics-text {
        color: #2c3e50 !important;
    }
    .analytics-title {
        color: #1a1a1a !important;
        font-weight: bold;
    }
    .analytics-label {
        color: #2c3e50 !important;
    }
</style>
""", unsafe_allow_html=True)

# COMPREHENSIVE QUIZ QUESTIONS DATABASE - WITH 1-2 EASY QUESTIONS PER CATEGORY
QUESTIONS = {
    "Science": [
        {
            "question": "What planet is known as the Red Planet?",
            "options": ["Venus", "Mars", "Jupiter", "Saturn"],
            "answer": "Mars",
            "explanation": "Mars appears red due to iron oxide (rust) on its surface.",
            "difficulty": "Easy",
            "type": "multiple_choice"
        },
        {
            "question": "How many bones are in the human body?",
            "options": ["106", "196", "206", "216"],
            "answer": "206",
            "explanation": "Adults have 206 bones, while babies have about 300 that fuse together as they grow.",
            "difficulty": "Medium",
            "type": "multiple_choice"
        },
        {
            "question": "Which element has the highest melting point?",
            "options": ["Tungsten", "Iron", "Platinum", "Gold"],
            "answer": "Tungsten",
            "explanation": "Tungsten has the highest melting point of all elements at 3,422°C (6,192°F).",
            "difficulty": "Hard",
            "type": "multiple_choice"
        },
        {
            "question": "The human brain is composed of approximately 80% water.",
            "options": ["True", "False"],
            "answer": "False",
            "explanation": "The human brain is about 73% water, not 80%.",
            "difficulty": "Medium",
            "type": "true_false"
        }
    ],
    "Geography": [
        {
            "question": "What is the largest ocean on Earth?",
            "options": ["Atlantic Ocean", "Indian Ocean", "Arctic Ocean", "Pacific Ocean"],
            "answer": "Pacific Ocean",
            "explanation": "The Pacific Ocean covers about 63 million square miles.",
            "difficulty": "Easy",
            "type": "multiple_choice"
        },
        {
            "question": "Which country has the largest population in the world?",
            "options": ["India", "United States", "China", "Russia"],
            "answer": "China",
            "explanation": "China has over 1.4 billion people, though India is very close.",
            "difficulty": "Medium",
            "type": "multiple_choice"
        },
        {
            "question": "What is the deepest point in the world's oceans?",
            "options": ["Puerto Rico Trench", "Mariana Trench", "Tonga Trench", "Philippine Trench"],
            "answer": "Mariana Trench",
            "explanation": "The Mariana Trench reaches about 11,034 meters (36,201 feet) deep.",
            "difficulty": "Hard",
            "type": "multiple_choice"
        },
        {
            "question": "Canada has more lakes than all other countries combined.",
            "options": ["True", "False"],
            "answer": "True",
            "explanation": "Canada contains about 60% of the world's lakes.",
            "difficulty": "Medium",
            "type": "true_false"
        }
    ],
    "History": [
        {
            "question": "The ______ Wall was built in ancient China for protection.",
            "answer": "Great",
            "explanation": "The Great Wall of China is over 13,000 miles long.",
            "difficulty": "Easy",
            "type": "fill_blank"
        },
        {
            "question": "In which year did World War II end?",
            "options": ["1944", "1945", "1946", "1947"],
            "answer": "1945",
            "explanation": "World War II ended in September 1945 with Japan's formal surrender.",
            "difficulty": "Medium",
            "type": "multiple_choice"
        },
        {
            "question": "Who was the first female prime minister in the world?",
            "options": ["Indira Gandhi", "Margaret Thatcher", "Sirimavo Bandaranaike", "Golda Meir"],
            "answer": "Sirimavo Bandaranaike",
            "explanation": "Sirimavo Bandaranaike of Sri Lanka became the world's first female prime minister in 1960.",
            "difficulty": "Hard",
            "type": "multiple_choice"
        },
        {
            "question": "The Renaissance began in Italy.",
            "options": ["True", "False"],
            "answer": "True",
            "explanation": "The Renaissance started in Florence, Italy in the 14th century.",
            "difficulty": "Medium",
            "type": "true_false"
        }
    ],
    "Technology": [
        {
            "question": "What does CPU stand for?",
            "options": ["Computer Processing Unit", "Central Processing Unit", "Central Program Utility", "Computer Program Unit"],
            "answer": "Central Processing Unit",
            "explanation": "CPU stands for Central Processing Unit, the primary component of a computer that performs most processing.",
            "difficulty": "Easy",
            "type": "multiple_choice"
        },
        {
            "question": "HTML is a programming language.",
            "options": ["True", "False"],
            "answer": "False",
            "explanation": "HTML is a markup language, not a programming language.",
            "difficulty": "Medium",
            "type": "true_false"
        },
        {
            "question": "The first version of Windows was released in ______.",
            "answer": "1985",
            "explanation": "Windows 1.0 was released on November 20, 1985.",
            "difficulty": "Hard",
            "type": "fill_blank"
        },
        {
            "question": "What was the first computer virus discovered in the wild?",
            "options": ["ILOVEYOU", "Melissa", "Brain", "MyDoom"],
            "answer": "Brain",
            "explanation": "The Brain virus, discovered in 1986, was the first PC virus found in the wild.",
            "difficulty": "Hard",
            "type": "multiple_choice"
        }
    ],
    "Entertainment": [
        {
            "question": "The character Harry Potter has a scar on his forehead.",
            "options": ["True", "False"],
            "answer": "True",
            "explanation": "Harry Potter has a lightning bolt scar on his forehead.",
            "difficulty": "Easy",
            "type": "true_false"
        },
        {
            "question": "Who directed the movie 'Inception'?",
            "options": ["Steven Spielberg", "Christopher Nolan", "James Cameron", "Martin Scorsese"],
            "answer": "Christopher Nolan",
            "explanation": "Christopher Nolan directed Inception in 2010.",
            "difficulty": "Medium",
            "type": "multiple_choice"
        },
        {
            "question": "Which actor has won the most Academy Awards?",
            "options": ["Jack Nicholson", "Daniel Day-Lewis", "Katharine Hepburn", "Meryl Streep"],
            "answer": "Katharine Hepburn",
            "explanation": "Katharine Hepburn won 4 Academy Awards for Best Actress.",
            "difficulty": "Hard",
            "type": "multiple_choice"
        },
        {
            "question": "The Beatles were from ______.",
            "answer": "Liverpool",
            "explanation": "The Beatles originated from Liverpool, England.",
            "difficulty": "Medium",
            "type": "fill_blank"
        }
    ],
    "Sports": [
        {
            "question": "How many players are on a soccer team during a match?",
            "options": ["9", "10", "11", "12"],
            "answer": "11",
            "explanation": "A soccer team has 11 players on the field during a match.",
            "difficulty": "Easy",
            "type": "multiple_choice"
        },
        {
            "question": "Which country won the FIFA World Cup in 2018?",
            "options": ["Germany", "Brazil", "France", "Argentina"],
            "answer": "France",
            "explanation": "France won the 2018 FIFA World Cup in Russia.",
            "difficulty": "Medium",
            "type": "multiple_choice"
        },
        {
            "question": "Who holds the record for most Olympic gold medals?",
            "options": ["Usain Bolt", "Carl Lewis", "Michael Phelps", "Larisa Latynina"],
            "answer": "Michael Phelps",
            "explanation": "Michael Phelps has won 23 Olympic gold medals, the most in history.",
            "difficulty": "Hard",
            "type": "multiple_choice"
        },
        {
            "question": "The first modern Olympics were held in Athens.",
            "options": ["True", "False"],
            "answer": "True",
            "explanation": "The first modern Olympic Games were held in Athens, Greece in 1896.",
            "difficulty": "Medium",
            "type": "true_false"
        }
    ]
}

def start_quiz(category, num_questions, question_types):
    """Start a new quiz with selected settings"""
    if not st.session_state.current_user:
        st.error("Please enter a username first!")
        return False
        
    # Get questions for the selected category and types
    if category == "All":
        all_questions = []
        for cat_questions in QUESTIONS.values():
            all_questions.extend(cat_questions)
    else:
        all_questions = QUESTIONS.get(category, [])
    
    # Filter by selected question types (now includes Easy, Medium, and Hard)
    filtered_questions = [q for q in all_questions if q.get('type', 'multiple_choice') in question_types]
    
    if not filtered_questions:
        st.error(f"No questions available for the selected category and question types!")
        return False
    
    # Set session state
    st.session_state.quiz_started = True
    st.session_state.current_question = 0
    st.session_state.score = 0
    st.session_state.user_answers = []
    st.session_state.show_results = False
    st.session_state.answer_submitted = False
    st.session_state.start_time = time.time()
    st.session_state.question_start_time = time.time()
    st.session_state.quiz_questions = random.sample(
        filtered_questions, 
        min(num_questions, len(filtered_questions))
    )
    st.session_state.quiz_category = category
    
    return True

def display_question():
    """Display the current question"""
    question_data = st.session_state.quiz_questions[st.session_state.current_question]
    question_type = question_data.get('type', 'multiple_choice')
    
    # Progress
    progress = (st.session_state.current_question) / len(st.session_state.quiz_questions)
    st.progress(progress)
    
    col1, col2, col3 = st.columns([2, 1, 1])
    with col1:
        st.write(f"**Question {st.session_state.current_question + 1}/{len(st.session_state.quiz_questions)}**")
    with col2:
        st.write(f"**Score: {st.session_state.score}**")
    with col3:
        difficulty = question_data.get('difficulty', 'Medium')
        if difficulty == "Easy":
            color = "🟢"
        elif difficulty == "Medium":
            color = "🟡"
        else:  # Hard
            color = "🔴"
        st.write(f"**Difficulty:** {color} {difficulty}")
    
    st.write("---")
    
    # Question card
    st.markdown('<div class="quiz-card">', unsafe_allow_html=True)
    
    st.write(f"### {question_data['question']}")
    
    # Display appropriate input based on question type
    user_answer = None
    
    if question_type == "multiple_choice":
        user_answer = st.radio(
            "Choose your answer:",
            question_data["options"],
            key=f"question_{st.session_state.current_question}"
        )
        
    elif question_type == "true_false":
        user_answer = st.radio(
            "True or False?",
            question_data["options"],
            key=f"question_{st.session_state.current_question}"
        )
        
    elif question_type == "fill_blank":
        user_answer = st.text_input(
            "Fill in the blank:",
            key=f"question_{st.session_state.current_question}"
        )
    
    st.markdown('</div>', unsafe_allow_html=True)
    
    # Submit button
    if user_answer and st.button("Submit Answer", type="primary", use_container_width=True):
        check_answer(user_answer, question_data)

def check_answer(user_answer, question_data):
    """Check if the answer is correct and update score"""
    correct_answer = question_data["answer"]
    question_type = question_data.get('type', 'multiple_choice')
    
    # Normalize answers for comparison
    if question_type == "fill_blank":
        user_answer = user_answer.strip().lower()
        correct_answer = correct_answer.lower()
        is_correct = user_answer == correct_answer
    else:
        is_correct = user_answer == correct_answer
    
    # Store user's answer with time tracking
    st.session_state.user_answers.append({
        'question': question_data['question'],
        'user_answer': user_answer,
        'correct_answer': correct_answer,
        'is_correct': is_correct,
        'explanation': question_data.get('explanation', ''),
        'difficulty': question_data.get('difficulty', 'Medium'),
        'category': get_question_category(question_data),
        'type': question_type,
        'time_taken': time.time() - st.session_state.question_start_time
    })
    
    # Update score
    if is_correct:
        st.session_state.score += 1
        st.success("✅ Correct! Well done!")
    else:
        st.error(f"❌ Incorrect! The correct answer was: **{correct_answer}**")
    
    if question_data.get('explanation'):
        st.info(f"💡 **Explanation:** {question_data['explanation']}")
    
    st.session_state.answer_submitted = True

def get_question_category(question_data):
    """Find which category a question belongs to"""
    for category, questions in QUESTIONS.items():
        if any(q['question'] == question_data['question'] for q in questions):
            return category
    return "Unknown"

def show_feedback():
    """Show feedback and navigation"""
    if st.session_state.current_question < len(st.session_state.quiz_questions) - 1:
        if st.button("Next Question →", type="primary", use_container_width=True):
            st.session_state.current_question += 1
            st.session_state.answer_submitted = False
            st.session_state.question_start_time = time.time()
            st.rerun()
    else:
        if st.button("See Final Results 🎊", type="primary", use_container_width=True):
            st.session_state.show_results = True
            st.session_state.quiz_started = False
            st.rerun()

def create_enhanced_analytics():
    """Create comprehensive performance visualization charts with very dark text"""
    if not st.session_state.user_answers:
        return
    
    # Prepare data for visualizations
    df = pd.DataFrame(st.session_state.user_answers)
    df['question_number'] = range(1, len(df) + 1)
    
    # Light color scheme
    light_colors = ['#FF6B6B', '#4ECDC4', '#45B7D1', '#96CEB4', '#FFEAA7', '#DDA0DD', '#98D8C8']
    
    # Apply dark text styling to all analytics
    st.markdown('<div class="analytics-text">', unsafe_allow_html=True)
    
    # Chart 1: Score progression with lighter colors
    st.markdown('<div class="analytics-title">', unsafe_allow_html=True)
    st.subheader("📈 Score Progression Over Time")
    st.markdown('</div>', unsafe_allow_html=True)
    
    df['cumulative_score'] = df['is_correct'].cumsum()
    df['accuracy_rate'] = (df['cumulative_score'] / df['question_number']) * 100
    
    fig_progress = go.Figure()
    
    # Add cumulative score line
    fig_progress.add_trace(go.Scatter(
        x=df['question_number'], 
        y=df['cumulative_score'],
        mode='lines+markers',
        name='Cumulative Score',
        line=dict(color=light_colors[0], width=4),
        marker=dict(size=8, color=light_colors[0])
    ))
    
    # Add accuracy rate line
    fig_progress.add_trace(go.Scatter(
        x=df['question_number'], 
        y=df['accuracy_rate'],
        mode='lines',
        name='Accuracy Rate (%)',
        line=dict(color=light_colors[1], width=3, dash='dash'),
        yaxis='y2'
    ))
    
    fig_progress.update_layout(
        title=dict(
            text='Your Performance Throughout the Quiz',
            font=dict(color='#000000', size=16, family='Arial')  # Very dark black
        ),
        xaxis=dict(
            title=dict(text='Question Number', font=dict(color='#000000', size=14)),  # Very dark black
            tickfont=dict(color='#000000', size=12)  # Very dark black
        ),
        yaxis=dict(
            title=dict(text='Cumulative Score', font=dict(color='#000000', size=14)),  # Very dark black
            tickfont=dict(color='#000000', size=12)  # Very dark black
        ),
        yaxis2=dict(
            title=dict(text='Accuracy Rate (%)', font=dict(color='#000000', size=14)),  # Very dark black
            overlaying='y',
            side='right',
            range=[0, 100],
            tickfont=dict(color='#000000', size=12)  # Very dark black
        ),
        plot_bgcolor='rgba(255,255,255,0.9)',
        paper_bgcolor='rgba(255,255,255,0.9)',
        font=dict(color='#000000', size=12),  # Very dark black
        showlegend=True,
        legend=dict(
            font=dict(color='#000000', size=12)  # Very dark black
        )
    )
    
    st.plotly_chart(fig_progress, use_container_width=True)
    
    # NEW: Performance by Question Type and Difficulty Level Side by Side
    st.markdown('<div class="analytics-title">', unsafe_allow_html=True)
    st.subheader("📊 Performance Analysis")
    st.markdown('</div>', unsafe_allow_html=True)
    
    # Create two columns for side-by-side charts
    col1, col2 = st.columns(2)
    
    with col1:
        # Chart 2: Performance by question type
        st.markdown('<div style="text-align: center; color: #000000; font-weight: bold; margin-bottom: 10px;">🎯 Performance by Question Type</div>', unsafe_allow_html=True)
        
        if 'type' in df.columns:
            type_performance = df.groupby('type').agg({
                'is_correct': ['count', 'mean'],
                'time_taken': 'mean'
            }).round(3)
            type_performance.columns = ['Total Questions', 'Accuracy', 'Avg Time (s)']
            type_performance = type_performance.reset_index()
            type_performance['Question Type'] = type_performance['type'].str.replace('_', ' ').str.title()
            
            fig_type = px.bar(
                type_performance, 
                x='Question Type', 
                y='Accuracy',
                color='Question Type',
                color_discrete_sequence=light_colors
            )
            fig_type.update_layout(
                xaxis=dict(
                    title=dict(text='Question Type', font=dict(color='#000000', size=12)),  # Very dark black
                    tickfont=dict(color='#000000', size=10)  # Very dark black
                ),
                yaxis=dict(
                    title=dict(text='Accuracy', font=dict(color='#000000', size=12)),  # Very dark black
                    tickfont=dict(color='#000000', size=10),  # Very dark black
                    tickformat='.0%', 
                    range=[0, 1]
                ),
                plot_bgcolor='rgba(255,255,255,0.9)',
                paper_bgcolor='rgba(255,255,255,0.9)',
                font=dict(color='#000000', size=10),  # Very dark black
                showlegend=False,
                height=400
            )
            st.plotly_chart(fig_type, use_container_width=True)
    
    with col2:
        # Chart 3: Performance by difficulty
        st.markdown('<div style="text-align: center; color: #000000; font-weight: bold; margin-bottom: 10px;">📈 Performance by Difficulty Level</div>', unsafe_allow_html=True)
        
        if 'difficulty' in df.columns:
            difficulty_performance = df.groupby('difficulty').agg({
                'is_correct': ['count', 'mean'],
                'time_taken': 'mean'
            }).round(3)
            difficulty_performance.columns = ['Total Questions', 'Accuracy', 'Avg Time (s)']
            difficulty_performance = difficulty_performance.reset_index()
            
            fig_difficulty = px.pie(
                difficulty_performance,
                values='Total Questions',
                names='difficulty',
                color='difficulty',
                color_discrete_map={
                    'Easy': '#96CEB4',  # Green for Easy
                    'Medium': light_colors[2],  # Yellow for Medium
                    'Hard': light_colors[4]  # Red for Hard
                }
            )
            fig_difficulty.update_layout(
                plot_bgcolor='rgba(255,255,255,0.9)',
                paper_bgcolor='rgba(255,255,255,0.9)',
                font=dict(color='#000000', size=10),  # Very dark black
                legend=dict(
                    font=dict(color='#000000', size=10)  # Very dark black
                ),
                height=400
            )
            st.plotly_chart(fig_difficulty, use_container_width=True)
    
    # Chart 4: Time analysis
    st.markdown('<div class="analytics-title">', unsafe_allow_html=True)
    st.subheader("⏱️ Time Analysis")
    st.markdown('</div>', unsafe_allow_html=True)
    
    fig_time = px.scatter(
        df, 
        x='question_number', 
        y='time_taken',
        color='is_correct',
        size='time_taken',
        title='Time Spent per Question',
        color_discrete_map={True: light_colors[1], False: light_colors[0]},
        labels={'time_taken': 'Time Taken (seconds)', 'question_number': 'Question Number'}
    )
    fig_time.update_layout(
        title=dict(
            text='Time Spent per Question',
            font=dict(color='#000000', size=16, family='Arial')  # Very dark black
        ),
        xaxis=dict(
            title=dict(text='Question Number', font=dict(color='#000000', size=14)),  # Very dark black
            tickfont=dict(color='#000000', size=12)  # Very dark black
        ),
        yaxis=dict(
            title=dict(text='Time Taken (seconds)', font=dict(color='#000000', size=14)),  # Very dark black
            tickfont=dict(color='#000000', size=12)  # Very dark black
        ),
        plot_bgcolor='rgba(255,255,255,0.9)',
        paper_bgcolor='rgba(255,255,255,0.9)',
        font=dict(color='#000000', size=12),  # Very dark black
        legend=dict(
            title=dict(text='Correct Answer', font=dict(color='#000000', size=12)),  # Very dark black
            font=dict(color='#000000', size=11)  # Very dark black
        )
    )
    st.plotly_chart(fig_time, use_container_width=True)
    
    # Detailed Analytics Table
    st.markdown('<div class="analytics-title">', unsafe_allow_html=True)
    st.subheader("📋 Detailed Performance Breakdown")
    st.markdown('</div>', unsafe_allow_html=True)
    
    # Calculate additional metrics
    total_time = df['time_taken'].sum()
    avg_time_per_question = df['time_taken'].mean()
    fastest_question = df.loc[df['time_taken'].idxmin()]
    slowest_question = df.loc[df['time_taken'].idxmax()]
    
    # Create analytics cards with dark text
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.markdown(f"""
        <div class="analytics-card">
            <h4 style="color: #000000;">⏱️ Time Metrics</h4>
            <p style="color: #000000;"><strong>Total Time:</strong> {total_time:.1f}s</p>
            <p style="color: #000000;"><strong>Avg Time/Question:</strong> {avg_time_per_question:.1f}s</p>
            <p style="color: #000000;"><strong>Fastest:</strong> {fastest_question['time_taken']:.1f}s</p>
            <p style="color: #000000;"><strong>Slowest:</strong> {slowest_question['time_taken']:.1f}s</p>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        accuracy_by_type = df.groupby('type')['is_correct'].mean()
        type_html = "".join([f"<p style='color: #000000;'><strong>{k.replace('_', ' ').title()}:</strong> {v:.1%}</p>" for k, v in accuracy_by_type.items()])
        st.markdown(f"""
        <div class="analytics-card">
            <h4 style="color: #000000;">🎯 Accuracy by Type</h4>
            {type_html}
        </div>
        """, unsafe_allow_html=True)
    
    with col3:
        accuracy_by_difficulty = df.groupby('difficulty')['is_correct'].mean()
        difficulty_html = "".join([f"<p style='color: #000000;'><strong>{k}:</strong> {v:.1%}</p>" for k, v in accuracy_by_difficulty.items()])
        st.markdown(f"""
        <div class="analytics-card">
            <h4 style="color: #000000;">📊 Accuracy by Difficulty</h4>
            {difficulty_html}
        </div>
        """, unsafe_allow_html=True)
    
    with col4:
        category_performance = df.groupby('category')['is_correct'].mean()
        category_html = "".join([f"<p style='color: #000000;'><strong>{k}:</strong> {v:.1%}</p>" for k, v in category_performance.items()])
        st.markdown(f"""
        <div class="analytics-card">
            <h4 style="color: #000000;">🏷️ Accuracy by Category</h4>
            {category_html}
        </div>
        """, unsafe_allow_html=True)
    
    st.markdown('</div>', unsafe_allow_html=True)  # Close analytics-text div

def show_final_results():
    """Display the final results with enhanced analytics"""
    total_questions = len(st.session_state.quiz_questions)
    score_percentage = (st.session_state.score / total_questions) * 100
    total_time = time.time() - st.session_state.start_time
    
    # Update leaderboard
    update_leaderboard(
        st.session_state.current_user,
        score_percentage,
        total_questions,
        total_time,
        st.session_state.quiz_category
    )
    
    # Performance rating
    if score_percentage >= 80:
        rating = "🏆 Quiz Master! Outstanding!"
        color = "#28a745"
    elif score_percentage >= 60:
        rating = "⭐ Great Job! Well done!"
        color = "#17a2b8"
    elif score_percentage >= 40:
        rating = "👍 Good effort! Keep practicing!"
        color = "#ffc107"
    else:
        rating = "📚 Challenging questions! Try again!"
        color = "#dc3545"
    
    st.markdown(f'<div class="result-box">', unsafe_allow_html=True)
    st.header("🎊 Quiz Complete!")
    
    # Key metrics
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric("Final Score", f"{st.session_state.score}/{total_questions}")
    with col2:
        st.metric("Percentage", f"{score_percentage:.1f}%")
    with col3:
        st.metric("Time Taken", f"{total_time:.1f}s")
    with col4:
        questions_per_minute = total_questions / (total_time / 60) if total_time > 0 else 0
        st.metric("Speed", f"{questions_per_minute:.1f} Q/min")
    
    st.subheader(rating)
    st.markdown('</div>', unsafe_allow_html=True)
    
    # Enhanced Analytics Section
    st.markdown('<div class="analytics-text">', unsafe_allow_html=True)
    st.header("📊 Comprehensive Analytics")
    create_enhanced_analytics()
    
    # Quick Statistics Cards
    st.header("📈 Quick Statistics")
    stats_col1, stats_col2, stats_col3, stats_col4 = st.columns(4)
    
    with stats_col1:
        correct_count = sum(1 for ans in st.session_state.user_answers if ans['is_correct'])
        st.markdown(f"""
        <div class="stat-card">
            <h3>✅ Correct</h3>
            <h2>{correct_count}</h2>
        </div>
        """, unsafe_allow_html=True)
    
    with stats_col2:
        incorrect_count = len(st.session_state.user_answers) - correct_count
        st.markdown(f"""
        <div class="stat-card">
            <h3>❌ Incorrect</h3>
            <h2>{incorrect_count}</h2>
        </div>
        """, unsafe_allow_html=True)
    
    with stats_col3:
        easy_count = sum(1 for ans in st.session_state.user_answers if ans.get('difficulty') == 'Easy')
        st.markdown(f"""
        <div class="stat-card">
            <h3>🟢 Easy</h3>
            <h2>{easy_count}</h2>
        </div>
        """, unsafe_allow_html=True)
    
    with stats_col4:
        hard_count = sum(1 for ans in st.session_state.user_answers if ans.get('difficulty') == 'Hard')
        st.markdown(f"""
        <div class="stat-card">
            <h3>🔴 Hard</h3>
            <h2>{hard_count}</h2>
        </div>
        """, unsafe_allow_html=True)
    
    st.markdown('</div>', unsafe_allow_html=True)  # Close analytics-text div
    
    # Display user statistics
    display_statistics()
    
    # Restart button
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        if st.button("🔄 Take Another Quiz", type="primary", use_container_width=True):
            st.session_state.quiz_started = False
            st.session_state.show_results = False
            st.session_state.current_question = 0
            st.session_state.score = 0
            st.session_state.user_answers = []
            st.rerun()

def main():
    # Header
    st.markdown('<h1 class="main-header">Ultimate Trivia Quiz Pro</h1>', unsafe_allow_html=True)
    st.write("### 🎯 Challenge yourself with questions of all difficulty levels!")
    
    # Sidebar - User Profile
    st.sidebar.header("👤 User Profile")
    
    if st.session_state.current_user:
        st.sidebar.success(f"Welcome, **{st.session_state.current_user}**! 🎉")
        if st.sidebar.button("🚪 Logout"):
            st.session_state.current_user = None
            st.rerun()
    else:
        username = st.sidebar.text_input("Enter your username:")
        if st.sidebar.button("🎮 Start Playing", use_container_width=True) and username:
            if username.strip():
                st.session_state.current_user = username.strip()
                st.rerun()
            else:
                st.sidebar.error("Please enter a valid username!")
    
    # Sidebar - Theme Selector
    st.sidebar.header("🎨 Theme")
    theme = st.sidebar.selectbox("Choose Theme", ["Light", "Dark"])
    if theme != st.session_state.selected_theme:
        st.session_state.selected_theme = theme
        st.rerun()
    
    # Sidebar - Leaderboard Preview
    st.sidebar.header("🏆 Leaderboard Preview")
    if st.session_state.global_leaderboard:
        for i, entry in enumerate(st.session_state.global_leaderboard[:3]):
            medal = ["🥇", "🥈", "🥉"][i]
            st.sidebar.write(f"**{medal} {entry['username']}** - {entry['percentage']:.1f}%")
        
        if st.sidebar.button("View Full Leaderboard"):
            st.session_state.show_leaderboard = True
    else:
        st.sidebar.info("No quiz results yet!")
    
    # Show full leaderboard if requested
    if st.session_state.get('show_leaderboard', False):
        display_leaderboard()
        if st.button("← Back to Quiz"):
            st.session_state.show_leaderboard = False
            st.rerun()
        return
    
    # Show results if quiz is complete
    if st.session_state.show_results:
        show_final_results()
    
    # Show quiz if in progress
    elif st.session_state.quiz_started and st.session_state.quiz_questions:
        display_question()
        if st.session_state.answer_submitted:
            show_feedback()
    
    # Show setup screen
    else:
        if not st.session_state.current_user:
            st.warning("👆 Please enter your username in the sidebar to start playing!")
            return
            
        col1, col2 = st.columns([2, 1])
        
        with col1:
            st.header("🎯 Quiz Settings")
            
            # Category selection
            categories = ["All"] + list(QUESTIONS.keys())
            selected_category = st.selectbox("Choose Category", categories)
            
            # Number of questions
            num_questions = st.slider("Number of Questions", 3, 15, 20)
            
            # Question type selection
            st.subheader("Question Types")
            question_types = st.multiselect(
                "Select question types to include:",
                ["multiple_choice", "true_false", "fill_blank"],
                default=["multiple_choice", "true_false", "fill_blank"],
                format_func=lambda x: x.replace('_', ' ').title()
            )
            
            if not question_types:
                st.error("Please select at least one question type!")
            
            # Info about question difficulty
            st.info("🔸 This quiz contains **Easy**, **Medium**, and **Hard** level questions for a balanced challenge!")
            
            # Start quiz button
            if st.button("🚀 Start Quiz", type="primary", use_container_width=True):
                if question_types:
                    if start_quiz(selected_category, num_questions, question_types):
                        st.rerun()
                else:
                    st.error("Please select at least one question type!")
        
        with col2:
            st.header("📊 Question Statistics")
            total_questions = sum(len(questions) for questions in QUESTIONS.values())
            st.write(f"**Total Questions Available:** {total_questions}")
            
            for category, questions in QUESTIONS.items():
                st.write(f"**{category}:** {len(questions)} questions")
            
            # Difficulty breakdown
            st.write("---")
            st.write("**Difficulty Levels:**")
            easy_count = sum(1 for cat in QUESTIONS.values() for q in cat if q.get('difficulty') == 'Easy')
            medium_count = sum(1 for cat in QUESTIONS.values() for q in cat if q.get('difficulty') == 'Medium')
            hard_count = sum(1 for cat in QUESTIONS.values() for q in cat if q.get('difficulty') == 'Hard')
            st.write(f"🟢 **Easy:** {easy_count} questions")
            st.write(f"🟡 **Medium:** {medium_count} questions")
            st.write(f"🔴 **Hard:** {hard_count} questions")
            
            # Display user statistics in the sidebar
            if st.session_state.current_user and st.session_state.users.get(st.session_state.current_user):
                user = st.session_state.users[st.session_state.current_user]
                st.write("---")
                st.write("**Your Stats:**")
                st.write(f"Quizzes Taken: {user.get('total_quizzes', 0)}")
                if user.get('total_quizzes', 0) > 0:
                    st.write(f"Average Score: {user.get('average_score', 0):.1f}%")
                    st.write(f"Best Score: {user.get('best_score', 0):.1f}%")

if __name__ == "__main__":
    main()