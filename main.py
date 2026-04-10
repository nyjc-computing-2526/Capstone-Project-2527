import app

capstone = app.create_app()

if __name__ == "__main__":
    capstone.run(debug=True)