import os
import math
from kivy.app import App
from kivy.clock import Clock
from kivy.core.window import Window
from kivy.graphics import Color, RoundedRectangle, Rectangle, PushMatrix, Rotate, PopMatrix, Line, Ellipse
from kivy.uix.image import Image
from kivy.metrics import dp
from kivy.uix.gridlayout import GridLayout
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.button import Button
from kivy.uix.textinput import TextInput
from kivy.uix.screenmanager import ScreenManager, Screen
from kivy.uix.relativelayout import RelativeLayout

Window.size = (380, 810)


LOG_FILE = "operation_log.txt"
class CalculatorScreen(RelativeLayout):
    def __init__(self, log_callback, **kwargs):
        super(CalculatorScreen, self).__init__(**kwargs)
        with self.canvas.before:
            Color(0.2, 0.2, 0.2, 1)
            self.bg_rect = Rectangle(size=(dp(860), dp(560)))
        self.first_input = True
        self.advanced_mode = False
        self.log_callback = log_callback
        self.initial_font_size = dp(64)
        self.min_font_size = dp(20)
        self.font_size_decrement_factor = 1.5
        self.previous_text = ""
        self.error_state = False
        self.ui_layout = BoxLayout(orientation="vertical", size_hint=(1, 1))
        padding_y = (dp(80), 0)
        self.display = TextInput(
            font_size=dp(48), text="", readonly=True, halign="right", multiline=False, size_hint=(1, 0.375),
            padding_y=padding_y
        )
        self.ui_layout.add_widget(self.display)
        self.button_grid = GridLayout(cols=4, size_hint=(1, 0.8), spacing=dp(13),padding=[dp(8), dp(8), dp(17), dp(10)])
        self.basic_buttons = [
            "Adv", "(", ")","/" ,
            "7", "8", "9", "*",
            "4", "5", "6","-" ,
            "1", "2", "3", "+",
            "C", "0", ".", "=",
        ]
        self.advanced_buttons = [
            "sin", "cos", "tan", "check",
            "e", "pi", "exp", "sqrt",
            "^", "mod", "undo", "Back"
        ]

        self.ui_layout.add_widget(self.button_grid)
        self.add_widget(self.ui_layout)
        self.create_buttons(self.basic_buttons)
    def create_buttons(self, buttons):
        self.button_grid.clear_widgets()
        for i, button in enumerate(buttons):

            layout = RelativeLayout(size=(dp(82), dp(82)))
            if i == len(buttons) -1:
                with layout.canvas.before:

                    Color(0, 0, 0, 1)
                    bg = RoundedRectangle(radius=[dp(20)], pos=layout.pos, size=layout.size)

            with layout.canvas.before:
                Color(0, 0, 0, 1)
                bg = RoundedRectangle(radius=[dp(20)], pos=layout.pos, size=layout.size)

            def update_bg(instance, value):
                bg.pos = layout.pos
                bg.size = layout.size
            layout.bind(pos=update_bg, size=update_bg)
            # Create the button
            button_widget = Button(
                text=button,
                font_size=dp(30),
                background_normal="",
                background_color=(0, 0, 0, 0),
                color=self.get_button_color(button),
                size_hint=(1, 1),
                on_press=self.on_button_press
            )
            layout.add_widget(button_widget)
            self.button_grid.add_widget(layout)
    def get_button_color(self, button_text):
        if button_text.isdigit() or button_text == ".":
            return [0.65,0.65, 0.65, 1]
        elif button_text in ["+", "-", "*", "/", "=", "^"]:
            return [0.35, 0.6, 0.8, 1]
        elif button_text in ["C", "Back"]:
            return [0.8, 0.5, 0.5, 1]
        elif button_text == "Adv":
            return [0.6, 0.8, 0.6, 1]
        elif button_text == "check":
            return [0.3, 0.4, 0.2, 1]
        elif button_text in [")", "("]:
            return [0.9, 0.6, 0.4, 1]
        else:
            return [0.2, 0.2, 0.2, 1]
    def adjust_font_size(self):
        text_length = len(self.display.text)
        if text_length > 10:
            new_font_size = self.initial_font_size / (self.font_size_decrement_factor ** (text_length // 10))
            self.display.font_size = max(new_font_size, self.min_font_size)
        else:
            self.display.font_size = self.initial_font_size

    def show_pi(self):

        radius = 150
        duration = 2.0
        center_x, center_y = self.center
        segments = 200


        gradient_radius = min(self.width, self.height) / 2
        steps = 50

        gradient_colors = []
        gradient_circles = []

        with self.canvas.after:
            for i in range(steps):
                alpha = max(0, 0.1 * (1 - i / steps))
                c = Color(1, 1, 1, alpha)
                gradient_colors.append(c)
                r = gradient_radius * (1 - i / steps)
                e = Ellipse(pos=(center_x - r, center_y - r), size=(2 * r, 2 * r))
                gradient_circles.append(e)


        with self.canvas.after:
            trail_color = Color(1, 1, 1, 0.8)
            trail = Line(points=[], width=1.2)

        elapsed = [0]
        with self.canvas.after:
            pi = Image(
                source="images/pi-1327145_1280.png",
                size_hint=(None, None),
                size=(dp(100), dp(100)),
                allow_stretch=True,
                pos_hint={"center_x": 0.5, "center_y": 0.5},
                opacity=1
            )
            self.add_widget(pi)
            Clock.schedule_once(lambda dt: self.remove_widget(pi), 1.5)


        def update(dt):
            elapsed[0] += dt
            progress = min(elapsed[0] / duration, 1.0)
            points = []

            steps_circle = int(segments * progress)
            for i in range(steps_circle + 1):
                angle = (i / segments) * 2 * math.pi
                x = center_x + radius * math.cos(angle)
                y = center_y + radius * math.sin(angle)
                points.extend([x, y])

            trail.points = points

            if progress >= 1.0:
                Clock.unschedule(update)
                fade_out()


        def fade_out():
            fade_time = 0.8
            fade_elapsed = [0]

            def fade(dt):
                fade_elapsed[0] += dt
                alpha = max(0, 1 - fade_elapsed[0] / fade_time)
                trail_color.a = alpha
                for i, c in enumerate(gradient_colors):
                    c.a = alpha * (1 - i / steps)

                if alpha <= 0:
                    Clock.unschedule(fade)
                    self.canvas.after.clear()

            Clock.schedule_interval(fade, 1 / 60)

        Clock.schedule_interval(update, 1 / 60)
    def show_anni(self):
        explosion = Image(
            source="images/scorch_02.png",
            size_hint=(None, None),
            size=(dp(100), dp(100)),
            allow_stretch=True,
            pos_hint={"center_x": 0.5, "center_y": 0.5},
            opacity=1
        )
        self.add_widget(explosion)

        # Add rotation instruction
        with explosion.canvas.before:
            PushMatrix()
            rot = Rotate(angle=0, origin=explosion.center)
        with explosion.canvas.after:
            PopMatrix()

        target_size = dp(1100)
        velocity = dp(120)
        growth = [velocity]

        def animate(dt):
            width, height = explosion.size
            new_size = width + growth[0]
            explosion.size = (new_size, new_size)
            explosion.center = self.center

            growth[0] *= 0.85


            rot.angle = (rot.angle + 0.03) % 360
            rot.origin = explosion.center


            if new_size >= target_size or growth[0] < 1:
                Clock.unschedule(animate)
                explosion.size = (target_size, target_size)
                explosion.center = self.center
                start_slow_pulse()

        def start_slow_pulse():
            slow_growth = [0.5]
            max_pulse = dp(1120)

            def pulse(dt):
                w, h = explosion.size
                if w < max_pulse:
                    explosion.size = (w + slow_growth[0], h + slow_growth[0])
                    explosion.center = self.center
                    slow_growth[0] *= 0.98


                    rot.angle = (rot.angle + 0.02) % 360
                    rot.origin = explosion.center

                else:
                    Clock.unschedule(pulse)
                    Clock.schedule_once(lambda dt: self.remove_widget(explosion), 0.7)

            Clock.schedule_interval(pulse, 1 / 60)

        Clock.schedule_interval(animate, 1 / 60)
        nice = Image(
            source="images/nice.png",
            size_hint=(1, 1),
            pos_hint={"center_x": 0.5, "center_y": 0.5},
            opacity=1
        )
        self.add_widget(nice)
        Clock.schedule_once(lambda dt: self.remove_widget(nice), 1.5)

    def on_button_press(self, instance):
        current = self.display.text
        button_text = instance.text

        if self.first_input:
            self.display.text = ""
            self.first_input = False
        if button_text not in ["C", "Back", "Undo"]:
            self.previous_text = current
        if button_text == "C":
            self.display.text = ""
        elif button_text == "=":

            try:
                current = current.replace("^", "**")
                value = eval(current)
                if isinstance(value, float) and value.is_integer():
                    value = int(value)
                result = str(value)
                self.display.text = result
                self.log_callback(f"{current} = {result}")
                if result == "69":
                    self.show_anni()
                if (isinstance(value, (int, float)) and abs(value - math.pi) < 1e-6):
                    self.show_pi()



            except Exception:
                self.display.text = "Error"
                self.error_state = True
        elif button_text == "Adv":
            self.advanced_mode = True
            self.create_buttons(self.advanced_buttons)
        elif button_text == "Back":
            self.advanced_mode = False
            self.create_buttons(self.basic_buttons)
        elif button_text == "check":
            self.parent.manager.current = "check"
        elif button_text in ["sin", "cos", "tan", "sqrt", "check", "exp", "pi", "e", "mod"]:
            try:
                if button_text == "pi":
                    self.display.text += str(math.pi)
                elif button_text == "e":
                    self.display.text += str(math.e)
                elif button_text == "sqrt":
                    result = str(math.sqrt(eval(current)))
                    self.log_callback(f"sqrt({current}) = {result}")
                    self.display.text = result
                elif button_text == "sin":
                    result = str(math.sin(math.radians(eval(current))))
                    self.log_callback(f"sin({current}) = {result}")
                    self.display.text = result
                elif button_text == "cos":
                    result = str(math.cos(math.radians(eval(current))))
                    self.log_callback(f"cos({current}) = {result}")
                    self.display.text = result
                elif button_text == "tan":
                    result = str(math.tan(math.radians(eval(current))))
                    self.log_callback(f"tan({current}) = {result}")
                    self.display.text = result
                elif button_text == "check":
                    result = str(math.log10(eval(current)))
                    self.log_callback(f"log({current}) = {result}")
                    self.display.text = result
                elif button_text == "exp":
                    result = str(math.exp(eval(current)))
                    self.log_callback(f"exp({current}) = {result}")
                    self.display.text = result
                elif button_text == "mod":
                    self.display.text += "%"
                elif button_text == "undo":
                    self.display.text = self.previous_text
            except Exception:
                self.display.text = "Error"
                self.error_state = True
        else:
            self.display.text += button_text
        self.adjust_font_size()
class LogScreen(BoxLayout):
    def __init__(self, **kwargs):
        super(LogScreen, self).__init__(**kwargs)
        self.orientation = "vertical"
        self.add_widget(TextInput(
            text="Operation Log (Last 10)", readonly=True, font_size=dp(30), halign="center", size_hint=(1, 0.1)
        ))
        self.log_display = TextInput(
            readonly=True, font_size=dp(30), halign="left", size_hint=(1, 0.8)

        )
        self.add_widget(self.log_display)
        back_button = Button(text="Back", size_hint=(1, 0.1), on_press=self.on_back)
        self.add_widget(back_button)
    def on_back(self, instance):
        self.parent.manager.current = "Kalkulator"
    def update_log(self, log_entries):
        self.log_display.text = "\n".join(log_entries)
class CalculatorApp(App):
    def build(self):
        self.sm = ScreenManager()
        self.log_entries = self.load_log()
        calculator_screen = Screen(name="Kalkulator")
        self.calculator_layout = CalculatorScreen(self.add_log_entry)
        calculator_screen.add_widget(self.calculator_layout)
        self.sm.add_widget(calculator_screen)
        log_screen = Screen(name="check")
        self.log_layout = LogScreen()
        log_screen.add_widget(self.log_layout)
        self.sm.add_widget(log_screen)

        return self.sm
    def add_log_entry(self, entry):
        self.log_entries.append(entry)
        if len(self.log_entries) > 10:
            self.log_entries.pop(0)
        self.save_log()
        self.log_layout.update_log(self.log_entries)
    def load_log(self):
        if os.path.exists(LOG_FILE):
            with open(LOG_FILE, "r") as file:
                return file.read().splitlines()
        return []
    def save_log(self):
        with open(LOG_FILE, "w") as file:
            file.write("\n".join(self.log_entries))
if __name__ == "__main__":
    CalculatorApp().run()

