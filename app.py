from flask import Flask, request, render_template_string
import os
import yt_dlp
from pydub import AudioSegment
import zipfile
import smtplib
from email.message import EmailMessage
from email_validator import validate_email, EmailNotValidError
from dotenv import load_dotenv

load_dotenv()
app = Flask(__name__)

# ==============================
# HTML FORM
# ==============================

HTML = """
<!doctype html>
<title>Mashup Generator</title>
<h2>Mashup Generator</h2>
<form method="post">
Singer Name: <input type="text" name="singer" required><br><br>
# of Videos (>10): <input type="number" name="videos" required><br><br>
Duration in seconds (>20): <input type="number" name="duration" required><br><br>
Email: <input type="email" name="email" required><br><br>
<input type="submit" value="Generate Mashup">
</form>
"""

# ==============================
# DOWNLOAD VIDEOS
# ==============================

def download_videos(singer, n):
    os.makedirs("downloads", exist_ok=True)

    ydl_opts = {
        'format': 'bestaudio/best',
        'outtmpl': 'downloads/%(title)s.%(ext)s',
        'quiet': True
    }

    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        ydl.download([f"ytsearch{n}:{singer} songs"])


# ==============================
# CUT + MERGE
# ==============================

def create_mashup(duration, output_file):
    final_audio = AudioSegment.empty()

    for file in os.listdir("downloads"):
        if file.endswith((".webm", ".m4a", ".mp4")):
            audio = AudioSegment.from_file(os.path.join("downloads", file))
            clipped = audio[:duration * 1000]
            final_audio += clipped

    final_audio.export(output_file, format="mp3")


# ==============================
# SEND EMAIL
# ==============================

def send_email(receiver_email, zip_file):

    sender_email = os.environ.get("EMAIL_USER")
    sender_password = os.environ.get("EMAIL_PASS") # Gmail App Password

    msg = EmailMessage()
    msg["Subject"] = "Your Mashup File"
    msg["From"] = sender_email
    msg["To"] = receiver_email
    msg.set_content("Your mashup file is attached. Enjoy!")

    with open(zip_file, "rb") as f:
        msg.add_attachment(
            f.read(),
            maintype="application",
            subtype="zip",
            filename=zip_file
        )

    with smtplib.SMTP_SSL("smtp.gmail.com", 465) as server:
        server.login(sender_email, sender_password)
        server.send_message(msg)


# ==============================
# ROUTE
# ==============================

@app.route("/", methods=["GET", "POST"])
def index():
    if request.method == "POST":

        try:
            singer = request.form["singer"]
            videos = int(request.form["videos"])
            duration = int(request.form["duration"])
            email = request.form["email"]

            # Email validation
            validate_email(email)

            if videos <= 10:
                return "Number of videos must be greater than 10"

            if duration <= 20:
                return "Duration must be greater than 20 seconds"

            # Clean old files
            if os.path.exists("downloads"):
                for f in os.listdir("downloads"):
                    os.remove(os.path.join("downloads", f))

            # Step 1: Download
            download_videos(singer, videos)

            # Step 2: Create mashup
            output_mp3 = "mashup.mp3"
            create_mashup(duration, output_mp3)

            # Step 3: Zip file
            zip_name = "mashup.zip"
            with zipfile.ZipFile(zip_name, 'w') as zipf:
                zipf.write(output_mp3)

            # Step 4: Send email
            send_email(email, zip_name)

            return "Mashup generated and sent to your email successfully!"

        except EmailNotValidError:
            return "Invalid Email Address"

        except Exception as e:
            return f"Error occurred: {str(e)}"

    return render_template_string(HTML)


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
