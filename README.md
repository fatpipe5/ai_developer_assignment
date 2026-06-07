# Mini AI Ticket Classifier

A simple Python tool that uses a local LLM via [Ollama](https://ollama.com) to analyse support tickets and return structured JSON classifications.

## Requirements

- Python 3.10+
- [Ollama](https://ollama.com) installed and running locally
- The `requests` library

## Setup

**1. Install Ollama**

Download and install Ollama from https://ollama.com, then pull the model:

```bash
ollama pull llama3.2
```

**2. Install Python dependency**

```bash
pip install -r requirements.txt
```

**3. Run the classifier**

```bash
python classifier.py
```

Results are printed to the console and saved to `example_output.json`.

## Example output

```bash
Processing TICKET-001...
  [OK] category=Deployment, priority=critical

Processing TICKET-002...
  [OK] category=Performance, priority=medium

Processing TICKET-003...
  [OK] category=Access Request, priority=low

Processing TICKET-004...
  [OK] category=Billing, priority=high

Processing TICKET-005...
  [OK] category=Performance, priority=high

Done. Results saved to example_output.json
```

## Project Structure

```
classifier.py        # Main script
tickets.json         # Five sample input tickets
example_output.json  # Example output from a real run
README.md
```

## How It Works

1. The script loads five tickets from `tickets.json`.
2. Each ticket is sent to the local Ollama API with a prompt that instructs the model to return a JSON object.
3. The response is parsed, the markdown code blocks are stripped from the response if the model added them.
4. The parsed JSON is validated: all required fields must be present and `priority` must be one of `low`, `medium`, `high`, `critical`.
5. Valid results are saved to `example_output.json`. Errors are printed clearly to the console.





