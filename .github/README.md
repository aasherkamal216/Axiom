# Axiom - A Docs Expert Agent

Axiom is AI Agent specialized in modern AI frameworks, libraries and tools. It can assist in creating AI Agents, RAG systems, chatbots, authentication mechanisms, and even full-stack development. It is built with LangGraph, MCP Docs Server, Chainlit and Gemini, designed to help users create different projects using natural language instructions.

![AxiomAgent](/public/axiom.png)

## Features

- 🤖 Interactive chat interface
- 📚 Access to multiple documentation sources
- 🎨 Support for image processing and analysis
- 📈 Use images and graphs to create production-ready code
- 🛠️ Customizable model settings (temperature, model version)
- 🌐 Docker support for containerized deployment

## Documentation Sources

Axiom used `llms.txt` of the given documentations and fetches content based on the URLs in `llms.txt`.
The agent has access to following documentations:
- LangGraph Python
- CrewAI
- Model Context Protocol (MCP)
- Chainlit
- FastHTML
- Supabase
- Pinecone
- Composio
- Clerk Auth
- Stack Auth
- Mem0
- Zep

## Prerequisites

*   UV package manager
*   Python 3.11+
*   Docker (optional): If you intend to use the `Dockerfile`, you'll need Docker installed.

## Installation

1. Clone the repository:
```bash
git clone https://github.com/aasherkamal216/Axiom.git
cd Axiom
```

2. Create and Activate Virtual Environment:
```bash
uv venv
.venv\Scripts\activate # For Windows
source .venv/bin/activate # for Mac
```

3. Install dependencies:
```bash
uv sync
```

4. Set up environment variables:
```bash
cp .env.example .env
```
Add your API keys in `.env` file. 

## Usage
### Run the application:
- First run the MCP Doc server:
```bash
uv run mcpdoc --yaml docs_config.yaml --transport sse --port 8082 --host localhost
```
- Then run chainlit interface:
```bash
uv run chainlit run app.py -w
```

The application will be available at `http://localhost:8000`.

### Building the Docker image (Optional)
Alternatively, you can use Docker to run the application:
```bash
docker build -t axiom .
docker run -p 7860:7860 -p 8082:8082 axiom
```

## Adding More Docs
You can add more documentations in `docs_config.yaml` file. Any documentation with a `llms.txt` file can be added to the list.
