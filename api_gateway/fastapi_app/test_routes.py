from main import app
print("Total routes:", len(app.routes))
for r in app.routes:
    if hasattr(r, "path"):
        print(r.path)
