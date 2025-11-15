"""Quick Gemini sanity check using the GEMINI_API_KEY environment variable."""

from __future__ import annotations

import os

import google.generativeai as genai


def main() -> None:
    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key:
        raise RuntimeError("GEMINI_API_KEY is not set. Export it before running the test.")

    genai.configure(api_key=api_key)
    model = genai.GenerativeModel("gemini-2.0-flash")

    response = model.generate_content("Write a short summary about AI agents.")
    text = response.text
    if not text and response.candidates:
        parts = response.candidates[0].content.parts  # type: ignore[assignment]
        text = "\n".join(getattr(part, "text", "") for part in parts).strip()

    if not text:
        raise RuntimeError(f"Gemini response did not contain text payload: {response}")

    print(text)


if __name__ == "__main__":
    main()
