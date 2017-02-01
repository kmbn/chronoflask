# Chronoflask
A minimalist diary/journal application made with Python 3, Flask, and TinyDB and inspired by Warren Ellis's Chronofile Minimal and Buckminster Fuller's Dymaxion Chronofile.
Add new entries (with or witout hashtags) in a single input field. Each entry is stored with a UTC timestamp.
View recent entries (in reverse chronological order), view all entries for a single day (in chronological order), view a single entry, view all entries associated with a tag, and view a list of tags.
Chronoflask is private by default.

## Setup
1. `cd path/to/chronoflask`
2. Optional: set up a virtual environment using virtualenv.
3. Install the required packages: `pip install -r requirements.txt`
4. Set the secret key for session encryption: `export SECRET_KEY=<your_secret_key_here>` (if you're just testing, the length of the string doesn't matter).
5. Enable `export DEBUG=1` or disable `export DEBUG=0` debug mode for the built-in server (enabling debugging is recommended for testing; if you plan to run the app on a production server, though, debugging should be disabled).
6. Optional: in order to enable password reset emails, you'll need to export the following: `export MAIL_SERVER=<your.email.server>`, `export MAIL_USERNAME=<your@email.username>` and `export MAIL_PASSWORD=<your_password>`. If you don't do this, the app will crash if you try to reset your password.
7. `python app/chronoflask.py` (or `python3 app/chronoflask.py` if you have a separate Python 3 installation). Chronoflask is made for Python 3, but it should work with Python 2.

## Usage
After completing the setup steps, open a browser and navigate to `http://localhost:5000/`. The first time you run the app you'l need to register; the current version of the app is intended to be single-user, so it is only possible to create one account.
Use the entry form to post brief notes, thoughts, observations, etc.
Any `#hashtags` in the entry will be detected and added to a list of tags for that entry. Any `#hashtags` at the end of the entry will will be stripped from the entry text to improve presentation (they'll be added to the tag list beforehand, though).
You can change the name of the chronofile and/or author in the `Admin` section, as well as change your email address and/or password.