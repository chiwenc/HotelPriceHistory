from App import create_app

app = create_app()
from App.plotlydash.dashboard import create_dashboard

app = create_dashboard(app)

if __name__ == "__main__":
    app.run(debug=True, port=5000)