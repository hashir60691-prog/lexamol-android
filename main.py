import json
import threading
import urllib.request
import urllib.error

from kivy.app import App
from kivy.clock import Clock
from kivy.metrics import dp
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.label import Label
from kivy.uix.textinput import TextInput
from kivy.uix.button import Button
from kivy.uix.scrollview import ScrollView
from kivy.core.window import Window
from kivy.utils import get_color_from_hex


API_URL = "http://127.0.0.1:8080/v1/chat/completions"

Window.clearcolor = get_color_from_hex("#070D18")


class LexamolApp(App):

    def build(self):
        self.title = "LEXAMOL AI"
        self.history = []

        root = BoxLayout(
            orientation="vertical",
            padding=dp(12),
            spacing=dp(10)
        )

        # Header
        header = BoxLayout(
            orientation="vertical",
            size_hint_y=None,
            height=dp(75)
        )

        title = Label(
            text="[b]LEXAMOL AI[/b]",
            markup=True,
            font_size="26sp",
            color=get_color_from_hex("#28DFFF"),
            halign="left"
        )

        subtitle = Label(
            text="PERSONAL AI ASSISTANT",
            font_size="11sp",
            color=get_color_from_hex("#8BA8BC"),
            halign="left"
        )

        header.add_widget(title)
        header.add_widget(subtitle)
        root.add_widget(header)

        # Chat area
        self.scroll = ScrollView()

        self.chat_box = BoxLayout(
            orientation="vertical",
            size_hint_y=None,
            spacing=dp(12),
            padding=dp(8)
        )

        self.chat_box.bind(
            minimum_height=self.chat_box.setter("height")
        )

        self.scroll.add_widget(self.chat_box)
        root.add_widget(self.scroll)

        self.add_message(
            "LEXAMOL",
            "Hello! Njan Lexamol aanu. Ennodu samsarikkam!"
        )

        # Status
        self.status = Label(
            text="● READY",
            size_hint_y=None,
            height=dp(25),
            color=get_color_from_hex("#42E6AA")
        )

        root.add_widget(self.status)

        # Input area
        bottom = BoxLayout(
            size_hint_y=None,
            height=dp(55),
            spacing=dp(8)
        )

        self.message_input = TextInput(
            hint_text="Ask Lexamol anything...",
            multiline=False,
            background_color=get_color_from_hex("#142235"),
            foreground_color=(1, 1, 1, 1),
            cursor_color=get_color_from_hex("#28DFFF"),
            hint_text_color=(0.6, 0.7, 0.8, 1),
            padding=dp(12)
        )

        self.message_input.bind(
            on_text_validate=self.send_message
        )

        send_button = Button(
            text="SEND",
            size_hint_x=None,
            width=dp(85),
            background_normal="",
            background_color=get_color_from_hex("#087FAD"),
            color=(1, 1, 1, 1)
        )

        send_button.bind(on_press=self.send_message)

        bottom.add_widget(self.message_input)
        bottom.add_widget(send_button)

        root.add_widget(bottom)

        return root

    def add_message(self, sender, message):

        color = (
            "#28DFFF" if sender == "LEXAMOL"
            else "#42E6AA"
        )

        label = Label(
            text=f"[b][color={color}]{sender}[/color][/b]\n{message}",
            markup=True,
            size_hint_y=None,
            halign="left",
            valign="middle",
            color=(0.9, 0.95, 1, 1),
            padding=(dp(10), dp(10))
        )

        label.bind(
            width=lambda instance, width:
            setattr(instance, "text_size", (width, None))
        )

        label.bind(
            texture_size=lambda instance, size:
            setattr(instance, "height", size[1] + dp(20))
        )

        self.chat_box.add_widget(label)

        Clock.schedule_once(
            lambda dt: setattr(
                self.scroll,
                "scroll_y",
                0
            ),
            0.1
        )

    def send_message(self, *args):

        message = self.message_input.text.strip()

        if not message:
            return

        self.message_input.text = ""

        self.add_message("YOU", message)

        self.history.append({
            "role": "user",
            "content": message
        })

        self.status.text = "● LEXAMOL THINKING..."

        self.send_button_lock = True

        threading.Thread(
            target=self.ask_gemma,
            daemon=True
        ).start()

    def ask_gemma(self):

        try:
            payload = {
                "model": "gemma",
                "messages": self.history,
                "temperature": 0.7,
                "max_tokens": 512,
                "stream": False
            }

            data = json.dumps(payload).encode("utf-8")

            request = urllib.request.Request(
                API_URL,
                data=data,
                headers={
                    "Content-Type": "application/json"
                },
                method="POST"
            )

            with urllib.request.urlopen(
                request,
                timeout=120
            ) as response:

                result = json.loads(
                    response.read().decode("utf-8")
                )

            answer = result["choices"][0]["message"]["content"]

            self.history.append({
                "role": "assistant",
                "content": answer
            })

            Clock.schedule_once(
                lambda dt: self.show_answer(answer)
            )

        except Exception as error:

            error_message = (
                "Gemma server connect aayilla.\n"
                "Termux-il server running aano enn check cheyyuka.\n\n"
                + str(error)
            )

            Clock.schedule_once(
                lambda dt: self.show_error(error_message)
            )

    def show_answer(self, answer):

        self.add_message("LEXAMOL", answer)
        self.status.text = "● ONLINE"

    def show_error(self, error):

        self.add_message("SYSTEM", error)
        self.status.text = "● CONNECTION ERROR"


if __name__ == "__main__":
    LexamolApp().run()
