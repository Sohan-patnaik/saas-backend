from flask import Flask, request, jsonify
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
from dotenv import load_dotenv
import os
from flask_cors import CORS
from routes.user_profile import update_user_profile
from services.tts_service import get_tts_audio
from routes.createBot import bp as bots_bp
from supabase import create_client
from bots.bots_utils import load_bot, get_bot_response

# --- Load environment variables ---
BACKEND_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
load_dotenv(os.path.join(BACKEND_ROOT, ".env"))

SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_SERVICE_KEY")
supabase = create_client(SUPABASE_URL, SUPABASE_KEY)

# --- Initialize Flask ---
app = Flask(__name__)
CORS(app, resources={r"/*": {"origins": "*"}})

limiter = Limiter(key_func=get_remote_address, default_limits=["20 per minute"])
limiter.init_app(app)

# --- Register blueprints ---
app.register_blueprint(bots_bp)

# --- Routes ---
@app.route("/set_profile", methods=["POST"])
def set_profile():
    data = request.get_json(silent=True) or {}
    name = data.get("name")
    age = data.get("age")
    preference = data.get("preference")
    update_user_profile(name=name, age=age, interests=[preference])
    return jsonify({"success": True, "message": "Profile updated"}), 200


@app.route("/get", methods=["POST"])
@limiter.limit("20 per minute")
def chat():
    """
    Handles chat requests from frontend. Expects JSON:
      { "msg": "hi", "bot_id": "uuid", "audio": false }
    """
    try:
        data = request.get_json(silent=True) or {}
        user_msg = data.get("msg")
        bot_id = data.get("bot_id")
        audio_flag = bool(data.get("audio", False))  # ✅ default false

        if not user_msg or not bot_id:
            return jsonify({"error": "Missing 'msg' or 'bot_id'"}), 400

        # ----- Fetch bot from Supabase -----
        bot_resp = supabase.table("bots").select("*").eq("id", bot_id).single().execute()
        if not bot_resp.data:
            return jsonify({"error": "Bot not found"}), 404

        yml_content = bot_resp.data.get("yml_content", "")
        if not yml_content:
            return jsonify({"error": "Bot has no YAML content"}), 500

        # ----- Generate response -----
        qa_pairs = load_bot(yml_content)
        bot_reply = get_bot_response(user_msg, qa_pairs)

        # ----- Optional TTS -----
        audio_data_uri = None
        if audio_flag and os.getenv("ELEVENLABS_API_KEY"):
            user_ip = get_remote_address()
            audio_data_uri = get_tts_audio(bot_reply, user_ip)

        # ----- Log conversation -----
        supabase.table("conversations").insert({
            "bot_id": bot_id,
            "user_message": user_msg,
            "bot_reply": bot_reply,
        }).execute()

        return jsonify({"response": bot_reply, "audio": audio_data_uri}), 200

    except Exception as e:
        print("Chat route error:", e)
        return jsonify({"error": "Internal server error"}), 500


if __name__ == "__main__":
    app.run(debug=True, port=8000)
