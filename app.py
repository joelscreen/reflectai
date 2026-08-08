from flask import Flask, render_template, request, jsonify
from groq import Groq
from supabase import Client, create_client
import secrets

app = Flask(__name__)

client = Groq(api_key="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")

supabase: Client = create_client("https://mndroclcanzxyrntbuzp.supabase.co",
                                 "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6Im1uZHJvY2xjYW56eHlybnRidXpwIiwicm9sZSI6InNlcnZpY2Vfcm9sZSIsImlhdCI6MTc4NTE0MDY0MSwiZXhwIjoyMTAwNzE2NjQxfQ.b01d8L2eSmzybtyTa089aMDHctHU5CTgSaPf8HF00Bk")

# Create a list of core traits that I have and rank them based on their percentage scores. Only send the core traits, nothing else. Show the ranking numbers before each trait

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

                Chat History: {chat_history} (the HTML elements where the <p> elements have "margin-left: auto;" is by the user, and the rest is by you)
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
                {"role": "user", "content": "Create a list of core traits that I have and rank them based on their percentage scores. Maximum 10 core traits. Only send the core traits with the percentage ranking, nothing else. Show the ranking numbers before each trait. If there are no entries, say 'No entries found'. The format for each core trait is 'Core Trait: percentage'."}
            ]
        )

        emotion_response = client.chat.completions.create(
            model="openai/gpt-oss-20b",
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": "Create a list of frequent emotions that I have and rank them based on their percentage scores. Maximum 10 frequent emotions Only send the frequent emotions with the percentage ranking, nothing else. Show the ranking numbers before each trait. If there are no entries, say 'No entries found'. The format for each core trait is 'Core Trait: percentage'."}
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
    token = request.headers.get("session-token")
    
    user_auth = supabase.table("Users").select("*").eq("session_token", token).execute()

    if len(user_auth.data) == 0:
        return jsonify(error="unauthorized"), 401

    user_auth = user_auth.data[0]

    user = supabase.table("diary_entries").select("*").eq("user_id", user_auth["id"]).execute()

    return jsonify(
        success=True,
        data=user.data
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

    token = secrets.token_hex(32)

    supabase.table("Users").update({"session_token": token}).eq("id", user["id"]).execute()

    return jsonify(
        success=True,
        session_token=token
    )

@app.route("/logout", methods=["POST"])
def logout():
    token = request.headers.get("session-token")

    supabase.table("Users").update({"session_token": None}).eq("session_token", token).execute()

    return jsonify(success=True)

@app.route('/fetch-user-details')
def fetch_user_details():
    token = request.headers.get("session-token")

    user = supabase.table("Users").select("*").eq("session_token", token).execute()

    if len(user.data) == 0:
        return jsonify(error="unauthorized"), 401

    user = user.data[0]

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
