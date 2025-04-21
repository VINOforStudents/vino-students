# Vino Students - AI-Powered Document Assistant

## Overview

The current version is an intelligent document assistant that uses Google's Gemini 1.5 Pro to analyze and respond to questions about educational frameworks and user-provided documents. Built with ChromaDB for vector storage and LangChain for seamless AI integration.

## Features


- 📚 Document Processing: Handles PDF and text documents
- 💬 Interactive Chat Interface: Natural conversation with context awareness
- 🔄 Vector Storage: Efficient document retrieval using ChromaDB
- 📤 User Uploads: Support for custom document uploads
- 🤖 Powered by Gemini 1.5 Pro: Advanced language understanding

## Quick Start

### Prerequisites


- Python 3.8+
- Google API Key

### Installation


**1. Clone the repository:**

```bash
git clone https://github.com/yourusername/vino-students.git
cd vino-students
```

**2.. Install uv(if not installed):**

uv offers several advantages:

* Faster package installation
* Better dependency resolution
* Built-in venv management
* Written in Rust for improved performance
* Compatible with existing Python tooling
* The rest of the README can remain the same.


```bash
pip install uv
```

**3.. Initialize uv & install dependencies**
```bash
uv init
uv sync
```

**4. Set up environment variables:**

Create a `.env` file in the root directory:
```
GOOGLE_API_KEY=your_api_key_here
```

### Usage

1. (Optional) Run the CLI application:

```bash
uvicorn APIendpoint:app --reload
```

2. Run the GUI application:

```bash
reflex run
```

3. Open the web-gui on localhost:3000 (stated in terminal)

4.  Available commands:

- `/upload [filepath]` - Upload a new document
- `/list` - Show uploaded documents
- `/process` - Process all files in uploads directory
- Type `exit` to quit


## Project Structure

```
vino-students/
├── main.py           # Main application for CLI
├── documents/        # Core framework documents
├── user_uploads/     # User document storage
├── chromadb/         # Vector database storage
├── vino_students/    # Reflex based GUI application
└── docs/             # Extended documentation
```


## Documentation

- [Architecture & Design](docs/architecture/README.md)
- [Development Process](docs/process/development.md)
- [Technical Details](docs/technical/README.md)

## Contributing

Please read [CONTRIBUTING.md](CONTRIBUTING.md) for contribution guidelines.

## License


This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.
