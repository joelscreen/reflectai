from flask import Flask, render_template, request, jsonify
from groq import Groq
from supabase import Client, create_client
import secrets
import os

app = Flask(__name__)

client = Groq(api_key=os.getenv("GROQ_API_KEY"))

supabase: Client = create_client("https://mndroclcanzxyrntbuzp.supabase.co",
                                 os.getenv("SUPABASE_KEY"))

def create_session(user_id):
    token = secrets.token_hex(32)

    supabase.table("session_tokens").insert({
        "user_id": user_id,
        "session_token": token
    }).execute()

    return token

def get_user_from_session():
    token = request.headers.get("session-token")

    if not token:
        return None

    session = (
        supabase
        .table("session_tokens")
        .select("user_id")
        .eq("session_token", token)
        .execute()
    )

    if len(session.data) == 0:
        return None

    user_id = session.data[0]["user_id"]

    user = (
        supabase
        .table("Users")
        .select("*")
        .eq("id", user_id)
        .execute()
    )

    if len(user.data) == 0:
        return None

    return user.data[0]

@app.route('/register-user', methods=["POST"])
def register_user():
    data = request.get_json()

    name = data["name"]
    loginid = data["loginid"]
    email = data["email"]
    password = data["password"]

    same_user = supabase.table("Users").select("*").or_(f"name.eq.{name},loginid.eq.{loginid},email.eq.{email},password.eq.{password}").execute()

    if len(same_user.data) > 0:
        return jsonify(success=False)

    user_reg = supabase.table("Users").insert({
        "name": name,
        "loginid": loginid,
        "password": password,
        "email": email
    }).execute()

    user = supabase.table("Users").select("*").eq("loginid", loginid).execute()
    
    if len(user.data) == 0:
        return jsonify(success=False)

    user = user.data[0]

    if user["password"] != password:
        return jsonify(success=False)

    token = create_session(user["id"])

    return jsonify(
        success=True,
        session_token=token
    )

@app.route('/core-traits', methods=["POST"])
def core_traits():
    data = request.json
    user_id = data.get("user_id","")
    name = data.get("name", "")
    entries = data.get("entries", "")
    chat_history = data.get("chat_history", "")
    new_report = data.get("new_report", "")

    system_prompt = f"""
                You are Reflect Companion, a helpful AI Assistant built by Joel Mendonca to help users solve their problems.
                The user's name is {name}.
                You must refer the {name}'s diary to understand their personality.
                The diary is in the JSON format, in order for you to know the date and time of entry too.

                Diary: {entries}
                """

    try:
        user = supabase.table("core_traits_and_emotions").select("*").eq("user_id", user_id).execute()
        if user.data != [] and new_report == "false":
            return jsonify({
                "core_traits": user.data[0]["core_traits"],
                "frequent_emotions": user.data[0]["emotions"]
            })
    
        response = client.chat.completions.create(
            model="openai/gpt-oss-20b",
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": "Create a list of core traits that I have and rank them based on their percentage scores. Maximum 10 core traits. Only send the core traits with the percentage ranking, nothing else. Show the ranking numbers before each trait. If there are no entries, say 'No entries found'. The format for each core trait is 'The Core Trait name (here, include only the name of the core trait): percentage'."}
            ]
        )

        emotion_response = client.chat.completions.create(
            model="openai/gpt-oss-20b",
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": "Create a list of frequent emotions that I have and rank them based on their percentage scores. Maximum 10 frequent emotions Only send the frequent emotions with the percentage ranking, nothing else. Show the ranking numbers before each trait. If there are no entries, say 'No entries found'. The format for each frequent emotion is 'The Frequent Emotion name (here, include only the name of the emotion): percentage'."}
            ]
        )
    
        if new_report == "true":
            user_traits = supabase.table("core_traits_and_emotions").update({
                "core_traits": response.choices[0].message.content,
                "emotions": emotion_response.choices[0].message.content
            }).eq("user_id", user_id).execute()
        elif new_report == "false":
            user_traits = supabase.table("core_traits_and_emotions").insert({
                "user_id": user_id,
                "core_traits": response.choices[0].message.content,
                "emotions": emotion_response.choices[0].message.content
            }).execute()
    
        return jsonify({
            "core_traits": response.choices[0].message.content,
            "frequent_emotions": emotion_response.choices[0].message.content
        })
    
    except Exception as e:
        return jsonify({
            "core_traits": f"Error: {str(e)}",
            "frequent_emotions": f"Error: {str(e)}"
        })

@app.route('/strenghts-weaknesses', methods=["POST"])
def strenghts_weaknesses():
    data = request.json
    user_id = data.get("user_id","")
    name = data.get("name", "")
    entries = data.get("entries", "")
    chat_history = data.get("chat_history", "")
    new_report = data.get("new_report", "")

    system_prompt = f"""
                You are Reflect Companion, a helpful AI Assistant built by Joel Mendonca to help users solve their problems.
                The user's name is {name}.
                You must refer the {name}'s diary to understand their personality.
                The diary is in the JSON format, in order for you to know the date and time of entry too.

                Diary: {entries}
                """

    try:
        user = supabase.table("strenghts_weaknesses").select("*").eq("user_id", user_id).execute()
        if user.data != [] and new_report == "false":
            return jsonify({
                "strenghts": user.data[0]["strenghts"],
                "weaknesses": user.data[0]["weaknesses"]
            })
    
        response = client.chat.completions.create(
            model="openai/gpt-oss-20b",
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": "Create a list of strenghts that I have and rank them based on their percentage scores. Maximum 10 strenghts. Only send the strenghts with the percentage ranking, nothing else. Show the ranking numbers before each strenght. If there are no entries, say 'No entries found'. The format for each strenght is 'The Strenght name (here, include only the name of the strenght): percentage'."}
            ]
        )

        emotion_response = client.chat.completions.create(
            model="openai/gpt-oss-20b",
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": "Create a list of weaknesses that I have and rank them based on their percentage scores. Maximum 10 weaknesses. Only send the weaknesses with the percentage ranking, nothing else. Show the ranking numbers before each weaknesses. If there are no entries, say 'No entries found'. The format for each weakness is 'The Weakness name (here, include only the name of the weakness): percentage'."}
            ]
        )
    
        if new_report == "true":
            user_sw = supabase.table("strenghts_weaknesses").update({
                "strenghts": response.choices[0].message.content,
                "weaknesses": emotion_response.choices[0].message.content
            }).eq("user_id", user_id).execute()
        elif new_report == "false":
            user_sw = supabase.table("strenghts_weaknesses").insert({
                "user_id": user_id,
                "strenghts": response.choices[0].message.content,
                "weaknesses": emotion_response.choices[0].message.content
            }).execute()
    
        return jsonify({
            "strenghts": response.choices[0].message.content,
            "weaknesses": emotion_response.choices[0].message.content
        })
    
    except Exception as e:
        return jsonify({
            "strenghts": f"Error: {str(e)}",
            "weaknesses": f"Error: {str(e)}"
        })

@app.route('/personality-check', methods=["POST"])
def personality_check():
    data = request.json
    user_id = data.get("id","")
    name = data.get("name", "")
    entries = data.get("entries", "")
    new_report = data.get("new_report", "")

    system_prompt = f"""
                You are Reflect Companion, a helpful AI Assistant built by Joel Mendonca to help users solve their problems.
                The user's name is {name}.
                You must refer the {name}'s diary to understand their personality.
                The diary is in the JSON format, in order for you to know the date and time of entry too.

                Diary: {entries}
                """

    try:
        user = supabase.table("personality").select("*").eq("user_id", user_id).execute()
        if user.data != [] and new_report == "false":
            return jsonify({
                "reply": user.data[0]["personality"]
            })

        response = client.chat.completions.create(
            model="openai/gpt-oss-20b",
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": "Submit a 1 paragraph (max 100 words) personality report that explains everything about me, my hobbies, strenghts, weaknesses, etc. Only include the paragraph, no headings."}
            ]
        )

        if new_report == "true":
            user_personality = supabase.table("personality").update({
                "personality": response.choices[0].message.content
            }).eq("user_id", user_id).execute()
        elif new_report == "false":
            user_personality = supabase.table("personality").insert({
                "user_id": user_id,
                "personality": response.choices[0].message.content
            }).execute()

        return jsonify({
            "reply": response.choices[0].message.content
        })

    except Exception as e:
        return jsonify({
            "reply": f"Error: {str(e)}"
        })

@app.route('/advice', methods=["POST"])
def advice():
    data = request.json
    user_id = data.get("id","")
    name = data.get("name", "")
    entries = data.get("entries", "")
    new_report = data.get("new_report", "")

    system_prompt = f"""
                You are Reflect Companion, a helpful AI Assistant built by Joel Mendonca to help users solve their problems.
                The user's name is {name}.
                You must refer the {name}'s diary to understand their personality.
                The diary is in the JSON format, in order for you to know the date and time of entry too.

                Diary: {entries}
                """

    try:
        user = supabase.table("advice").select("*").eq("user_id", user_id).execute()
        if user.data != [] and new_report == "false":
            return jsonify({
                "reply": user.data[0]["advice"]
            })

        response = client.chat.completions.create(
            model="openai/gpt-oss-20b",
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": "Give me some advice based on my diary entries. Maximum 300 words. Try to include only 1-2 diary writing advice, with a total of 5-6 advices"}
            ]
        )

        if new_report == "true":
            user_advice = supabase.table("advice").update({
                "advice": response.choices[0].message.content
            }).eq("user_id", user_id).execute()
        elif new_report == "false":
            user_advice = supabase.table("advice").insert({
                "user_id": user_id,
                "advice": response.choices[0].message.content
            }).execute()

        return jsonify({
            "reply": response.choices[0].message.content
        })

    except Exception as e:
        return jsonify({
            "reply": f"Error: {str(e)}"
        })

@app.route('/get-chat-history', methods=["POST"])
def get_chat_history():
    data = request.json
    user_id = data.get("user_id", "")

    user = supabase.table("chatbot").select("*").eq("user_id", user_id).execute()

    return jsonify({"data": user.data})

@app.route("/load-chat", methods=["POST"])
def load_chat():
    data = request.json

    user_id = data["user_id"]
    chat_id = data["chat_id"]

    chat = (
        supabase.table("chatbot")
        .select("conversation")
        .eq("user_id", user_id)
        .eq("id", chat_id)
        .execute()
    )

    if len(chat.data) == 0:
        return jsonify({
            "success": False
        }), 404

    return jsonify({
        "success": True,
        "conversation": chat.data[0]["conversation"]
    })

@app.route('/reflect-companion', methods=["POST"])
def reflect_comp():
    data = request.json
    user_id = data.get("user_id","")
    name = data.get("name", "")
    entries = data.get("entries", "")
    message = data.get("message", "")
    chat_history = data.get("chat_history", "")
    chat_id = data.get("chat_id", "")

    system_prompt = f"""
                You are Reflect Companion, a helpful AI Assistant built by Joel Mendonca to help users solve their problems.
                Joel Mendonca has built you.
                The user's name is {name}.
                You must refer the {name}'s diary to understand their personality.
                The diary is in the JSON format, in order for you to know the date and time of entry too.
                Solve their problems based on their personality, so that you appear comforting rather than disturbing to the user.
                Always think in a positive mindset, and request the user to do so too.
                If possible, try to help the user connect with previous experiences in order for them to learn from their mistakes.
                Always answer using Markdown formatting.
                Do not output HTML or CSS.

                Chat History: {chat_history} (the HTML elements where the <p> elements have "margin-left: auto;" is by the user, and the rest is by you)
                (If the chat history is not empty, then that means the user has been chatting with you before. If that's the case, then avoid repeating "i've been looking at your diary and chat history" and all)
                Diary: {entries}
                """

    try:
        response = client.chat.completions.create(
            model="openai/gpt-oss-20b",
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": message}
            ]
        )
        chat_history += f"""
                        <p style="margin-left: auto;
                        width: fit-content;
                        background-color: #4d4a4a;
                        padding: 10px;
                        border-radius: 8px;">{message}</p>
                        <p class="ai-message">{response.choices[0].message.content}</p>
                        """

        name_response = client.chat.completions.create(
                    model="openai/gpt-oss-20b",
                    messages=[
                        {"role": "system", "content": "The user will send an HTML styled chat history. The HTML elements where the <p> elements have 'margin-left: auto;' is by the user, and the rest is by you. Your job is to create a small 3-4 word title name for the initial question by the user. Don't include text decorations like **'s"},
                        {"role": "user", "content": chat_history}
                    ]
                )

        if not chat_id:
            history = supabase.table("chatbot").insert({
                "user_id": user_id,
                "conversation": chat_history,
                "name": name_response.choices[0].message.content
            }).execute()

            chat_id = history.data[0]["id"]

        else:
            history = (
                supabase.table("chatbot")
                .update({
                    "conversation": chat_history
                })
                .eq("id", chat_id)
                .execute()
            )

        return jsonify({
            "reply": response.choices[0].message.content,
            "chat_id": chat_id,
            "name": name_response.choices[0].message.content if history.data else None
        })

    except Exception as e:
        return jsonify({
            "reply": f"Error: {str(e)}"
        })

@app.route('/insert-diary-entry', methods=["POST"])
def insert_diary_entry():
    data = request.get_json()

    id = data["id"]
    title = data["title"]
    content = data["content"]

    user = supabase.table("Users").select("*").eq("id", id).execute()

    if len(user.data) == 0:
        return jsonify(success=False)

    user = user.data[0]

    supabase.table("diary_entries").insert([
        {"user_id": id, "title": title, "content": content}
    ]).execute()

    return jsonify(
        success=True
    )

@app.route('/fetch-diary-entry', methods=["POST"])
def fetch_diary_entry():

    user = get_user_from_session()

    if user is None:
        return jsonify(error="unauthorized"), 401

    diary = (
        supabase
        .table("diary_entries")
        .select("*")
        .eq("user_id", user["id"])
        .execute()
    )

    return jsonify(
        success=True,
        data=diary.data
    )

@app.route('/delete-diary-entry', methods=["POST"])
def delete_diary_entry():
    token = request.headers.get("session-token")

    user = supabase.table("Users").select("*").eq("session_token", token).execute()

    if len(user.data) == 0:
        return jsonify(error="unauthorized"), 401

    user = user.data[0]

    data = request.get_json()
    id = data["id"]

    user = supabase.table("diary_entries").delete().eq("id", data["id"]).execute()

    return jsonify(
        success=True,
        data=user.data
    )

@app.route('/check-user-login', methods=["POST"])
def check_user_login():
    data = request.get_json()

    loginid = data["loginid"]
    password = data["password"]

    user = supabase.table("Users").select("*").eq("loginid", loginid).execute()

    if len(user.data) == 0:
        return jsonify(success=False)

    user = user.data[0]

    if user["password"] != password:
        return jsonify(success=False)

    token = create_session(user["id"])

    return jsonify(
        success=True,
        session_token=token
    )

@app.route("/logout", methods=["POST"])
def logout():
    token = request.headers.get("session-token")

    if not token:
        return jsonify(success=True)

    supabase.table("session_tokens").delete().eq(
        "session_token", token
    ).execute()

    return jsonify(success=True)

@app.route('/fetch-user-details')
def fetch_user_details():
    user = get_user_from_session()

    if user is None:
        return jsonify(error="unauthorized"), 401

    return jsonify(
        id=user["id"],
        name=user["name"],
        email=user["email"]
    )

@app.route('/login')
def login():
    return render_template('login/login.html')

@app.route('/register')
def register():
    return render_template('login/register.html')

@app.route('/chatbot')
def chatbot():
    return render_template('main/chatbot.html')

@app.route('/')
def main_page():
    return render_template('main/index.html')

if __name__ == "__main__":
    app.run(host="0.0.0.0", debug=True)
