from flask import Blueprint, request, jsonify
from supabase import create_client
import os, yaml, re
from dotenv import load_dotenv

load_dotenv(dotenv_path=os.path.join(os.path.dirname(os.path.dirname(__file__)), "..", ".env"))

SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_SERVICE_KEY")

supabase = create_client(SUPABASE_URL, SUPABASE_KEY)
bp = Blueprint("bots", __name__)

@bp.route("/create-bot", methods=["POST"])
def create_bot():
    bot_name = request.form.get("bot_name")
    description = request.form.get("description", "")  # ✅ optional now

    if not bot_name:
        return jsonify({"error": "Missing bot_name"}), 400

    file = request.files.get("file")
    if not file:
        return jsonify({"error": "No file uploaded"}), 400

    # ✅ Validate YAML file content
    yml_content = file.read().decode("utf-8")
    try:
        yaml.safe_load(yml_content)
    except yaml.YAMLError as e:
        return jsonify({"error": f"Invalid YAML: {e}"}), 400

    # ✅ Safe file name
    safe_name = re.sub(r"[^a-zA-Z0-9_-]", "_", bot_name)
    user_id = "default_user"  # later you can use real auth
    storage_path = f"bot-files/{user_id}/{safe_name}.yml"

    # ✅ Upload to Supabase Storage
    try:
        supabase.storage.from_("bot-files").upload(
            storage_path,
            yml_content.encode("utf-8"),
            {"content-type": "text/yaml"},
        )
    except Exception as e:
        return jsonify({"error": f"Failed to upload file: {e}"}), 500

    bot_data = {
        "owner": user_id,
        "name": bot_name,
        "description": description,
        "file_name": file.filename,
        "storage_path": storage_path,
        "yml_content": yml_content,
    }

    try:
        new_bot = supabase.table("bots").insert(bot_data).execute()
        inserted_bot = getattr(new_bot, "data", None)
    except Exception as e:
        return jsonify({"error": f"Failed to create bot: {e}"}), 500

    # ✅ Return as list for frontend consistency
    return jsonify({
        "message": "Bot created successfully",
        "bot": inserted_bot if inserted_bot else [bot_data]
    }), 201
