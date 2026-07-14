class QueryParser():
    def clean(self, input: str) -> str:
        text = self._strip_input(input)
        text = self._normalize(text)
        text = self._remove_extra_symbols(text)
        text = self._truncate(text)
        return text

    def _normalize(self,text: str) -> str:
        """Collapse runs of spaces/tabs/newlines into single spaces and trim."""
        return " ".join(text.split())

    def _strip_input(self, text: str) -> str:
        #removes trailing/leading whitespace
        return text.strip()

    def _to_lower(self,text: str) -> str:
        return text.lower()

    def _remove_puncuation(self, text: str) -> str:
        import string
        return text.translate(str.maketrans("", "", string.punctuation))

    def _remove_extra_symbols(self,text: str) -> str:
        """Strip emojis / non-printable junk; keep letters, digits, basic punctuation."""
        import re
        return re.sub(r"[^\w\s#.,!?'-]", "", text)

    def _truncate(self, text: str, max_len: int = 1000) -> str:
        """Cap length before sending to the LLM (cost / prompt-injection guard)."""
        return text[:max_len]
    
    def extract_ticket_number(self, message: str) -> str:
        import re
        match = re.search(r"\b(\d{6})\b", message)
        return match.group(1) if match else None
