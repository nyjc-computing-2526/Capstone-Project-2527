import os

import app

capstone = app.create_app()

if __name__ == "__main__":
    capstone.run(host="0.0.0.0", port=int(os.getenv("PORT", "5000")))
