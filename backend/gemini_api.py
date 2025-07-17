import google.generativeai as genai

# Khai báo API Key
genai.configure(api_key="AIzaSyBHEL2J5T4z8XNr4qIaXmwP44kt0Hr5yP8")

# Tạo hàm gọi Gemini
def call_gemini(prompt):
    try:
        model = genai.GenerativeModel(model_name="gemini-2.0-flash")
        response = model.generate_content(prompt)
        return response.text
    except Exception as e:
        print("Gemini API error:", e)
        return "Gemini API error: " + str(e)