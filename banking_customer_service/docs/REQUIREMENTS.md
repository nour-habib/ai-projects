# Banking Customer Support AI Agent — Capstone Requirements

Multi-agent GenAI assistant for banking customer support. Classifies incoming
messages, produces personalized responses, and tracks support tickets.

## Part 1 — Multi-Agent Design

### 1. Classifier Agent
- **Input:** unstructured user message.
- **Task:** categorize into exactly one of:
  - `Positive Feedback`
  - `Negative Feedback`
  - `Query`
- Route to the matching downstream agent.

### 2. Feedback Handler Agent
Triggered when input is classified as feedback.

- **Positive Feedback:** generate a warm, personalized thank-you via an LLM.
  - Format: `Thank you for your kind words, [CustomerName]! We're delighted to assist you.`
- **Negative Feedback:**
  - Generate a unique **6-digit** ticket number.
  - INSERT a new **unresolved** ticket into DB table `support_tickets`.
  - Return an empathetic message:
    - Format: `We apologize for the inconvenience. A new ticket #[TicketNumber] has been generated, and our team will follow up shortly.`

### 3. Query Handler Agent
Triggered when input is classified as a query.

- Extract the ticket number from the user message.
- Query the `support_tickets` database.
- Return ticket status:
  - Format: `Your ticket #[TicketNumber] is currently marked as: [Status].`

### Sample Flows
- `"Thanks for sorting out my net banking login issue."` → Classifier → Positive Feedback Handler
- `"My debit card replacement still hasn't arrived."` → Classifier → Negative Feedback Handler (new ticket)
- `"Could you check the status of ticket 650932?"` → Classifier → Query Handler

## Part 2 — LLMOps (Evaluation, Logging, Interface)

### 7. Model Evaluation
- Assess response quality: feedback accuracy, empathy level, clarity of status updates.
- QA-based scoring + test case coverage for classification logic.
- Evaluate agent routing success rate.

### 8. Streamlit UI
- Accept user input and simulate agent routing.
- Display classification, response, and database interaction.
- View historical queries and logs.
- Test scenarios for each agent role.

### 9. Logs & Debugging View
- Show prompt traces, classification output, and ticket actions.
- Maintain logs of ticket IDs and agent success/failure rate.
- Optionally integrate user feedback into an agent improvement loop.

## Notes
- Default to the latest Claude models (e.g. `claude-opus-4-8`) unless specified otherwise.
