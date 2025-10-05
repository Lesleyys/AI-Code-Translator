# AI-Code-Translator
# AI Code Translator (Streamlit + Vertex AI)

A Streamlit app that:
- Translates source code between languages with Vertex AI (Gemini).
- Suggests optimizations.
- Generates unit tests and UAT test scripts.
- Lets you download results as a ZIP and upload to a GCS bucket.

---

## Prerequisites

- **Python 3.9+** (app was developed on 3.9)
- **pip** and (recommended) **virtualenv**
- **Google Cloud** project with Vertex AI & Cloud Storage enabled
- Authentication via one of:
  - `gcloud auth application-default login` (ADC), **or**
  - a service account key file with the right roles (Vertex AI User, Storage Object Admin or equivalent bucket-scoped role)

> If `streamlit` isn’t found after install, add `~/.local/bin` to your PATH:
> ```
> export PATH="$HOME/.local/bin:$PATH"
> ```

---

## Setup

```bash
# Clone and enter the project
git clone <your-repo-url>
cd Code-Translator

# Create a virtual environment (recommended)
python3 -m venv .venv
source .venv/bin/activate

# Install dependencies
pip install -r requirements.txt
