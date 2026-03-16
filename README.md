# Satair Feedback Prototype

This prototype was developed to demonstrate how customer feedback can be integrated into the Satair Market platform. The interface includes a feedback modal where users can submit comments directly from the page, and a parts search feature for browsing aircraft parts.

## Run locally (VERY IMPORTANT)

The prototype works directly in the browser and temporarily stores feedback in the browser’s local storage.

If you want to see the fully developed prototype, start the backend server.

```bash
python3 server.py
```

Then open the prototype in your browser:

```plaintext
http://localhost:3000
```

## Features

- **Feedback Collection**: Submit structured feedback that gets saved locally or to disk.
- **Parts Search**: Search for aircraft parts by part number, name, or description. Results are displayed in a grid with details.
- **Browse All Parts**: View the entire parts catalog without searching.

## Data storage

When the server is running:
- Feedback submissions are saved in: `feedback/feedback.txt`
- Aircraft parts are stored in: `parts.db` 

## Notes

* The app must be accessed via `http://localhost:3000` for feedback to be saved and to see the UI properly.
* If you open `index.html` directly (file://), feedback will not be stored and you may not see the website properly.
