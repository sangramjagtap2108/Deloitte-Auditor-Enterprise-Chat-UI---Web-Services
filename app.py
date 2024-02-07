from flask import Flask, request, jsonify, render_template
import redis
import openai
import hashlib

app = Flask(__name__)
redis_client = redis.Redis(host='localhost', port=6379, db=0, decode_responses=True)

# Set up OpenAI API key
openai.api_key = "Enter your openai api key here"

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/ask', methods=['POST'])
def ask_question():
    # Get the question from the user
    question = request.json.get('question')
    
    # Get response from OpenAI API
    response = get_openai_response(question)
    
    return jsonify({"answer": response})

def get_openai_response(question):
    # Normalize the question to ensure consistency in caching
    normalized_question = question.lower().strip()
    question_hash = hashlib.sha256(normalized_question.encode('utf-8')).hexdigest()
    cache_key = f"openai_response:{question_hash}"
    
    # Try to get the response from Redis cache
    cached_response = redis_client.get(cache_key)
    if cached_response:
        print("Serving from cache:", cache_key)
        return cached_response 
    
     # If not in cache, fetch the response from OpenAI
    print("Fetching new response from OpenAI for:", cache_key) 
    prompt = f"Determine if the following question is related to tax, and if so, provide a detailed answer. If not, respond with 'This question is not related to tax.'\n\nQuestion: {question}"
    
    response = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        messages=[
            {"role": "system", "content": "You are a knowledgeable assistant capable of answering tax-related questions. For non-tax-related questions, simply state that the question is not related to tax."},
            {"role": "user", "content": prompt}
        ]
    )
    
    # Extracting and returning the response text
    if response.choices and len(response.choices) > 0:
        answer = response.choices[0].message['content'].strip()
        # Cache the response with an expiration time (e.g., 24 hours = 86400 seconds)
        redis_client.setex(cache_key, 86400, answer)
        return answer
    else:
        return "I'm sorry, I couldn't process your request."

if __name__ == "__main__":
    app.run(debug=True)


# On redis CLI -
# To search for Keys
# KEYS openai_response:*

# To Check Cached Responses
# GET <KEY>

