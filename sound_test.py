import subprocess

def text_to_speech(text):
    try:
        subprocess.run(["espeak-ng", "-v", "en-us", text], check=True)
    except subprocess.CalledProcessError as e:
        print(f"Error running espeak-ng: {e}")

if __name__ == "__main__":
    text = "Hello, this is a test of text-to-speech using espeak-ng in Python."
    text_to_speech(text)