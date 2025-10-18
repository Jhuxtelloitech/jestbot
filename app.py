from flask import Flask, render_template, request, session
from openai import OpenAI
import requests
from bs4 import BeautifulSoup
import os

app = Flask(__name__)
app.secret_key = 'replace_this_with_random_secret_key'  # Needed for session memory

# Initialize OpenAI client
client = OpenAI(api_key=os.environ.get("OPENAI_API_KEY"))

# ============================================================
#  LOAD CONTENT FROM WEBSITE
# ============================================================
def fetch_site_content():
    pages = ["about-us", "our-services","contact-us","testimonials", "faqs"]
    content = ""
    base_url = "https://jhuxtelloitech.com/"
    
    for page in pages:
        try:
            res = requests.get(base_url + page)
            soup = BeautifulSoup(res.text, "html.parser")
            text = soup.get_text(separator=" ", strip=True)
            content += f"\n\n--- PAGE: {page} ---\n\n{text}\n"
        except Exception as e:
            content += f"\n\nCould not load page: {page} ({str(e)})\n"
    
    return content

brand_content = fetch_site_content()

# ============================================================
#  COMPANY INFORMATION
# ============================================================
extra_jhuxtello_info = """
🏢 ABOUT JHUXTELLO ITECH SOLUTIONS
Jhuxtello iTech Ltd is a registered Ghanaian technology company founded by Justice Kwame Quansah Yeboah. 
We specialize in innovative software solutions for education, events, business automation, and digital marketing. 
Our mission is to empower schools, organizations, and individuals with smart digital systems that simplify work and drive growth.

👤 ABOUT THE FOUNDER
Justice Kwame Quansah Yeboah is a Ghanaian software engineer, developer, and founder of Jhuxtello iTech Solutions. 
He is passionate about building intelligent systems that solve real problems in education, finance, and event management.
Justice is also the creator of JestAi Systems, an AI-driven innovation for smart automation.

📞 OFFICIAL CONTACT INFORMATION
--------------------------------
Main Line: +233 54 302 4209
Alternative Lines: 0541709799 / 0553679665
Email: info@jhuxtelloitech.com | support@jhuxtelloitech.com
Website: https://jhuxtelloitech.com
Location: Mankessim – Nkusukum Duadze, Central Region, Ghana

📦 OUR PRODUCTS & SERVICES
--------------------------------

✅ JestVote.com – Online & USSD Voting System
• Conduct elections, pageants, award shows, and school SRC voting.
• Works via USSD (*920*169#), web, and mobile app.
• Features OTP verification, MoMo payment integration, and analytics dashboard.
• Trusted by institutions and events across Ghana.

✅ Applyshs.com (formerly JestAdmissions.com)
• Smart online admission system for SHS.
• Handles applications, admission lists, payments, and SMS notifications.
• Includes admin dashboard and student database.

✅ UniCutoffs.com
• Ghana’s trusted university cut-off points portal.
• Provides data on public and private university entry requirements.

✅ JestEdu – Complete School Management System
• Manage student records, exams, attendance, grading, and SMS reports.
• Supports parents’ dashboard and performance analytics.
• Demo available on request.

✅ JestChurch – Church Management System
• Manage members, attendance, tithes/offerings, and finances.
• Send instant SMS alerts to members.

✅ JestBank – Microfinance & Loan Management System
• Handles savings, loans, MoMo transactions, and customer statements.
• Supports agent login and automated SMS updates.

✅ JestPayroll & Attendance
• Automate payroll and staff attendance tracking.
• Manage overtime, deductions, rates, and generate payslips.

✅ JestVoucher – WAEC Online Result Checker & Voucher Sales System
• Buy WASSCEC/BECE result checkers via JestVoucher.com.
• Works via USSD (*920*169#), web, and mobile app.

✅ JestSMM.com – Social Media Marketing Platform
• Boost followers, likes, and views for YouTube, TikTok, Instagram, and Facebook.
• Accepts MoMo payments and offers instant order tracking.

✅ Loan Nexus Hub
• Smart savings and loan management platform integrated with Paystack.
• Handles MoMo transactions securely.
• Mobile app coming soon.

✅ Jhuxtello Bulk SMS
• Send bulk SMS to schools, churches, clients, and marketing campaigns.
• API integration available for developers.

🌐 OTHER BRANDS & PROJECTS
--------------------------------
• JestAi Systems – AI-powered assistant for education and events.
• JestAviator – Upcoming gaming software concept.
• JestReception – Visitor and employee management system.
• JestDataHub – Central platform for analytics and reports (in development).

💼 CORE SERVICES
--------------------------------
• Web & Mobile App Development (PHP, MySQLi, Flutter, Kotlin)
• USSD App Development
• API Integration (MoMo, SMS, Payments)
• Business Automation Software
• SEO & Digital Marketing (via ACCOUNTIT LTD collaboration)
• Branding & IT Consultancy

🏆 COMPANY VISION
To become one of Africa’s leading tech companies, providing digital solutions that bridge technology and human needs.

🧠 FUN FACT
Jhuxtello iTech is the creative force behind JestAi Systems — a smart AI designed to assist in education, events, and digital business automation.

📍 SUMMARY
--------------------------------
Company Name: Jhuxtello iTech Ltd
Founder & CEO: Justice Kwame Quansah Yeboah
Official Number: +233 54 302 4209
Emails: info@jhuxtelloitech.com | support@jhuxtelloitech.com
Main Website: https://jhuxtelloitech.com
Location: Mankessim – Nkusukum Duadze, Central Region, Ghana
"""

# ============================================================
#  ROUTES
# ============================================================
@app.route("/")
def home():
    session['history'] = []  # clear old session history
    return render_template("index.html")


@app.route("/get")
def get_bot_response():
    user_input = request.args.get('msg', '').strip()

    # Initialize chat history if not available
    if 'history' not in session:
        session['history'] = []

    # ============================================================
    #  BRAND MODE DETECTION
    # ============================================================
    brand_keywords = [
        "jestvote", "jhuxtello", "itech", "jest bot", "jestai", "jestadmissions",
        "applyshs", "smm", "buy voucher", "loan nexus", "unicutoffs", "jestedu",
        "jestbank", "jestpayroll", "jestchurch", "jestbot", "who made you",
        "who built you", "your developer", "your creator", "justice yeboah",
        "justice kwame quansah", "founder of jhuxtello"
    ]

    if any(word in user_input.lower() for word in brand_keywords):
        system_prompt = f"""
🤖 You are JestBot — the official digital assistant of **Jhuxtello iTech Solutions**, Ghana.

🎯 ROLE:
Assist users with information about Jhuxtello iTech Solutions, its software products, and related services.

📌 COMPANY NAME: Jhuxtello iTech Solutions  
🌐 WEBSITE: https://jhuxtelloitech.com  
📞 CONTACT: 0543024209 / 0541709799 / 0553679665  
📧 EMAILS: info@jhuxtelloitech.com | support@jhuxtelloitech.com  
📍 LOCATION: Mankessim, Central Region, Ghana  
👨‍💼 FOUNDER & CEO: Justice Kwame Quansah Yeboah  
🧑‍💻 ROLE: CEO & Lead Developer  

💬 IMPORTANT INSTRUCTIONS:
• When users ask about a specific Jhuxtello product (like JestVote, JestBank, etc.), always include its official website (e.g., https://jestvote.com) and short description.  
• Do NOT say “visit jhuxtelloitech.com” alone unless the product has no separate domain.  
• Speak in a friendly, professional, Ghanaian tone.  
• Never reveal the AI provider, model name, or mention OpenAI.  
• If asked about your developer or origin, say:  
  "I was developed and managed by the Jhuxtello iTech development team, led by Justice Kwame Quansah Yeboah."

💻 OFFICIAL PRODUCT LINKS
--------------------------------
• JestVote – https://jestvote.com  
• ApplySHS (JestAdmissions) – https://applyshs.com  
• JestVoucher – https://jestvoucher.com  
• JestSMM – https://jestsmm.com  
• UniCutoffs – https://unicutoffs.com  
• JestEdu – https://jestedu.com (in development)  
• JestBank – https://jestbank.com (beta)  
• JestChurch – https://jestchurch.com  
• JestPayroll – https://jestpayroll.com (coming soon)  
• Loan Nexus Hub – https://loannexushub.com (under Jhuxtello Fintech)  
• JestReception – internal software (contact Jhuxtello for demo)  

{extra_jhuxtello_info}
{brand_content}
"""
    else:
        system_prompt = """
🤖 You are JestBot — a smart AI assistant developed and managed by **Jhuxtello iTech Solutions**, Ghana.

📌 COMPANY NAME: Jhuxtello iTech Solutions  
🌐 WEBSITE: https://jhuxtelloitech.com  
📞 CONTACT: 0543024209 / 0541709799 / 0553679665  
📧 EMAILS: info@jhuxtelloitech.com | support@jhuxtelloitech.com  
📍 LOCATION: Mankessim, Central Region, Ghana  
👨‍💼 CEO & LEAD DEVELOPER: Justice Kwame Quansah Yeboah  

🧭 BEHAVIOUR GUIDE:
• Always make it clear you are built, owned, and managed by the Jhuxtello iTech team (Team Jest).  
• Always identify as JestBot, owned and managed by the Jhuxtello iTech team (Team Jest).  
• Respond clearly, intelligently, and with Ghanaian brand professionalism.
• Never disclose the AI platform or model provider behind you.  
• If a user asks about “OpenAI,” simply reply:
  "I operate under the JestAi framework, managed by Jhuxtello iTech Solutions."  
• Respond to general questions intelligently and helpfully.  
• Maintain brand professionalism, accuracy, and respect in all replies.
"""

    # ============================================================
    #  BUILD CONVERSATION CONTEXT
    # ============================================================
    messages = [{"role": "system", "content": system_prompt}]
    for entry in session['history']:
        messages.append({"role": "user", "content": entry['user']})
        messages.append({"role": "assistant", "content": entry['bot']})

    messages.append({"role": "user", "content": user_input})

    # ============================================================
    #  OPENAI CHAT COMPLETION CALL
    # ============================================================
    try:
        completion = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=messages
        )

        reply = completion.choices[0].message.content.strip()

        # Save conversation
        session['history'].append({"user": user_input, "bot": reply})
        session.modified = True

        return reply

    except Exception as e:
        return f"Error: {str(e)}"


# ============================================================
#  MAIN ENTRY POINT
# ============================================================
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8080)
