import streamlit as st
from google import genai
from google.genai import types
from openai import OpenAI

NAME_MAPPING = {
    "Gemini-2.5-Flash": "gemini-2.5-flash-preview-04-17",  # gemini-2.5-pro-preview-03-25
    "o4-mini": "o4-mini",
    "gpt-4o": "gpt-4o",
    "gpt-4o-mini-search-preview": "gpt-4o-mini-search-preview",
    "gpt-4o-search-preview": "gpt-4o-search-preview",
}


class Model:
    def __init__(self, model_type):
        self.model_type = model_type

        self.system_prompt = (
            "If you are asked to provide code or LaTeX, embed it in markdown text "
            "such that it is not compiled by the interface."
        )

        self._history = [{"role": "system", "content": self.system_prompt}]
        self._create_client()

    def _create_client(self):
        if self.model_type == "google":
            client = genai.Client()
            self.client = client.chats.create(
                model=st.session_state.selected_model,
                config=types.GenerateContentConfig(
                    system_instruction=self.system_prompt,
                ),
            )
        elif self.model_type == "openai":
            self.client = OpenAI()
        else:
            raise ValueError(f"Model type '{self.model_type}' is not valid.")

    def chat(self, message):
        if self.model_type == "openai":
            return self._openai_chat(message)
        elif self.model_type == "google":
            return self._google_chat(message)

    def _google_chat(self, message):
        answer = self.client.send_message(message)
        self._history = [self._history[0]]
        for element in self.client.get_history():
            text = element.to_json_dict()["parts"][0]["text"]
            role = element.to_json_dict()["role"]
            role = "assistant" if role == "model" else "user"
            self._history.append({"role": role, "content": text})

        return answer.text

    def _openai_chat(self, message):
        self._history.append({"role": "user", "content": message})

        response = self.client.chat.completions.create(
            model=st.session_state.selected_model,
            messages=self._history,
        )
        assistant_reply = response.choices[0].message.content
        self._history.append({"role": "assistant", "content": assistant_reply})

        return assistant_reply

    @property
    def history(self):
        return self._history[1:]
