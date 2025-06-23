from flask import Flask, render_template, request, session
from openai import OpenAI
import requests
from bs4 import BeautifulSoup
import os


app = Flask(__name__)
app.secret_key = 'replace_this_with_random_secret_key'  # Needed for session memory

client = OpenAI(
    api_key=os.environ.get("OPENAI_API_KEY")
)

# 🔍 Load content from your website
def fetch_site_content():
    pages = ["about-us", "our-services", "faqs"]
    content = ""
    base_url = "https://jhuxtelloitech.com/"
    
    for page in pages:
        try:
            res = requests.get(base_url + page)
            soup = BeautifulSoup(res.text, "html.parser")
            text = soup.get_text(separator=" ", strip=True)
            content += f"\n\n--- PAGE: {page} ---\n\n{text}\n"
        except:
            content += f"\n\nCould not load page: {page}\n"
    
    return content

brand_content = fetch_site_content()

# ✅ Company info for brand-aware answers
extra_jhuxtello_info = """
📌 ABOUT JHUXTELLO ITECH SOLUTIONS
Jhuxtello iTech Ltd is a Ghana-based digital agency founded by Justice Kwame Quansah Yeboah. We specialize in smart software solutions for events, education, business automation, and digital services.

📦 OUR SOFTWARE PRODUCTS & SERVICES
✅ JestVote.com – Online & USSD Voting System
• Host award shows, elections, pageants, school SRC voting, and more
• Supports USSD *920*169#, OTP verification & Mobile Money payments
• Trusted by institutions across Ghana

✅ JestAdmissions.com – SHS Online Admission Portal
• Manage online student admissions with ease
• Integrated with payments, SMS, and admin dashboard

✅ UniCutoffs.com – University Cut-off Points Platform
• Ghana’s trusted hub for public and private university admissions data

✅ JestEdu – Complete School Management System
• Student info, attendance, exams, SMS, parent reports, and more
(Demo available on request)

✅ JestChurch – Church Management System
• Member management, tithes/offerings, SMS alerts, attendance & finances

✅ JestBank – Microfinance & Loan Management System
• Manage savings, loans, statements, Momo transactions & customers

✅ JestPayroll & Attendance
• Automate staff salary, overtime, deductions, and generate payslips

✅ JestVoucher – Online Result Checker & Voucher Sales System
• Sell WAEC/BECE result checkers online-Jestadmissions.com/buy
• Generate vouchers and track sales easily

✅ JestSMM.com – Boost Likes, Followers, and Views
• Social media marketing for Instagram, YouTube, TikTok, Facebook
• Accepts Mobile Money payments

✅ Loan Nexus Hub
• Smart loan and savings platform with MoMo integration via Paystack
(Coming soon: mobile app)

✅ Jhuxtello Bulk SMS
• Send bulk SMS to schools, churches, clients, or for campaigns
(API integration available)

📍 LOCATION:
Mankessim – Nkusukum Duadze, Central Region, Ghana

📞 CONTACT:
📱 0541709799 / 0553679665
🌐 Website: https://jhuxtelloitech.com

🧠 FUN FACT
Jhuxtello is also the creator of JestAi, a smart AI-powered solution for education and events automation.
"""

@app.route("/")
def home():
    # Clear old session history when visiting home
    session['history'] = []
    return render_template("index.html")

@app.route("/get")
def get_bot_response():
    user_input = request.args.get('msg').strip()

    # Initialize chat history if not available
    if 'history' not in session:
        session['history'] = []

    # Decide the mode: brand vs general
    if any(word in user_input.lower() for word in [
        "jestvote", "jhuxtello", "itech", "jest bot", "jestadmissions", "smm", "buy voucher",
        "loan nexus", "unicutoffs", "jestedu", "jestbank", "jestpayroll", "jestchurch"
    ]):
        system_prompt = f"""
You are JestBot, official assistant for Jhuxtello iTech Solutions, based in Ghana.

You MUST always use this information when answering questions related to Jhuxtello iTech:

📌 COMPANY NAME: Jhuxtello iTech Solutions  
🌐 OFFICIAL WEBSITE: https://jhuxtelloitech.com  
📞 CONTACT: 0541709799 / 0553679665  
📍 LOCATION: Mankessim, Central Region, Ghana  
👨‍💼 FOUNDER & CEO: Justice Kwame Quansah Yeboah  
🧑‍💻 ROLE: CEO and Lead Developer

{extra_jhuxtello_info}
{brand_content}

If asked something not directly in this data, use your general intelligence to help, but relate answers to this company when appropriate.
"""
    else:
        system_prompt = "You are JestBot, a smart, helpful AI assistant like ChatGPT. Answer clearly and professionally."

    # Construct full conversation
    messages = [{"role": "system", "content": system_prompt}]
    for entry in session['history']:
        messages.append({"role": "user", "content": entry['user']})
        messages.append({"role": "assistant", "content": entry['bot']})

    messages.append({"role": "user", "content": user_input})

    try:
        completion = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=messages
        )

        reply = completion.choices[0].message.content.strip()

        # Save to session history
        session['history'].append({"user": user_input, "bot": reply})
        session.modified = True  # Required for session update

        return reply

    except Exception as e:
        return f"Error: {str(e)}"

if __name__ == "__main__":
    app.run(debug=True)
