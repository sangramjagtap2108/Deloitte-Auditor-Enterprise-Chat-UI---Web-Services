from flask import Flask, request, jsonify, render_template
import openai

app = Flask(__name__)

# Set up OpenAI API key
openai.api_key = "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"

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
    # Basic keyword-based check for tax relevance
    tax_keywords = ['tax', 'deduction', 'IRS', 'income tax', 'taxation', 'taxpayer', 'tax return', 'tax code', 'tax law', 'tax bracket']
    if not any(keyword.lower() in question.lower() for keyword in tax_keywords):
        return "Please ask a tax-related question."

    response = openai.Completion.create(
      engine="text-davinci-002",
      prompt=question,
      max_tokens=150
    )
    return response.choices[0].text.strip()


if __name__ == "__main__":
    app.run(debug=True)
