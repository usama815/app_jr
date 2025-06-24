from flask import Flask, request

app=Flask(__name__)
@app.route("/callback")
def callback():
    code=request.args.get("code")
    state=request.args.get("state")
    return f"Code: {code}<br>, State: {state}<br><br>"
if __name__ == "__main__":
    app.run(debug=True, port=8000)
    # Use port 5000 to avoid conflicts with other services
    # If you want to use a different port, change the port number here
    # and in the OAuth2 configuration of your application.