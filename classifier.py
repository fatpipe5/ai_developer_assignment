import json
import re
import requests

OLLAMA_URL = "http://localhost:11434/api/generate"
MODEL = "llama3.2"

PROMPT_TEMPLATE = """You are a support ticket classifier. Analyse the ticket below and return a JSON object with exactly these fields:

- category: a short label for the type of issue (e.g. "Deployment", "Performance", "Access Request", "Billing", "Infrastructure")
- priority: one of exactly these values: low, medium, high, critical
- summary: one sentence describing the problem
- recommended_action: one sentence on what should be done next

Return only the raw JSON object. Do not include any explanation, markdown, or code fences.

Ticket:
{ticket_text}
"""

REQUIRED_FIELDS = {"category", "priority", "summary", "recommended_action"}
VALID_PRIORITIES = {"low", "medium", "high", "critical"}


def call_ollama(ticket_text: str) -> str:
    payload = {
        "model": MODEL,
        "prompt": PROMPT_TEMPLATE.format(ticket_text=ticket_text),
        "stream": False,
    }
    response = requests.post(OLLAMA_URL, json=payload, timeout=60)
    response.raise_for_status()
    return response.json()["response"]


def extract_json(raw: str) -> dict:
    match = re.search(r"```(?:json)?\s*(\{.*?\})\s*```", raw, re.DOTALL)     #strip markdown code blocks if the model added them
    if match:
        raw = match.group(1)


    match = re.search(r"\{.*\}", raw, re.DOTALL) #try to find a bare JSON object
    if match:
        raw = match.group(0)

    return json.loads(raw)


def validate(data: dict) -> list[str]:
    errors = []
    missing = REQUIRED_FIELDS - data.keys()
    if missing:
        errors.append(f"Missing fields: {', '.join(missing)}")
    if "priority" in data and data["priority"] not in VALID_PRIORITIES:
        errors.append(f"Invalid priority '{data['priority']}'. Must be one of: {', '.join(VALID_PRIORITIES)}")
    return errors


def process_tickets(tickets: list[dict]) -> list[dict]:
    results = []
    for ticket in tickets:
        ticket_id = ticket["id"]
        print(f"\nProcessing {ticket_id}...")

        try:
            raw = call_ollama(ticket["text"])
            data = extract_json(raw)
            errors = validate(data)

            if errors:
                print(f"  [VALIDATION ERROR] {ticket_id}: {'; '.join(errors)}")
                results.append({"ticket_id": ticket_id, "error": errors, "raw_response": raw})
            else:
                print(f"  [OK] category={data['category']}, priority={data['priority']}")
                results.append({"ticket_id": ticket_id, "result": data})

        except requests.exceptions.ConnectionError:
            print(f"  [ERROR] Could not connect to Ollama at {OLLAMA_URL}. Is it running?")
            results.append({"ticket_id": ticket_id, "error": "Ollama not reachable"})
        except json.JSONDecodeError as e:
            print(f"  [ERROR] Could not parse JSON from model response: {e}")
            results.append({"ticket_id": ticket_id, "error": f"JSON parse error: {e}", "raw_response": raw})
        except Exception as e:
            print(f"  [ERROR] Unexpected error: {e}")
            results.append({"ticket_id": ticket_id, "error": str(e)})

    return results


def main():
    with open("tickets.json") as f:
        tickets = json.load(f)

    results = process_tickets(tickets)

    output_path = "example_output.json"
    with open(output_path, "w") as f:
        json.dump(results, f, indent=2)

    print(f"\nDone. Results saved to {output_path}")


if __name__ == "__main__":
    main()
