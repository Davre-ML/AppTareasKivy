import os
from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.textinput import TextInput
from kivy.uix.button import Button
from kivy.uix.label import Label
from kivy.properties import StringProperty, BooleanProperty
from kivy.uix.scrollview import ScrollView
from kivy.metrics import dp
from kivy.core.window import Window # Para configurar el color de fondo de la ventana

# Definir colores para fácil acceso
BG_COLOR = (1, 1, 1, 1) # Blanco (R, G, B, A)
FG_COLOR = (0, 0, 0, 1) # Negro

# Definición de un Widget de Tarea individual
class TaskWidget(BoxLayout):
    task_text = StringProperty('')
    is_completed = BooleanProperty(False)

    def __init__(self, text, completed=False, **kwargs):
        super().__init__(**kwargs)
        self.task_text = text
        self.is_completed = completed
        self.orientation = 'horizontal'
        self.size_hint_y = None
        self.height = dp(55) # Altura fija para cada tarea, un poco más grande
        self.spacing = dp(5) # Espacio entre elementos dentro del widget de tarea
        self.padding = [dp(5), dp(5)] # Padding dentro del widget de tarea
        self.background_color = BG_COLOR # Fondo blanco para el frame de la tarea

        # Configurar el fondo del BoxLayout del widget de tarea
        # Kivy BoxLayout no tiene background_color directamente, se usa Canvas
        with self.canvas.before:
            from kivy.graphics import Color, Rectangle
            self.rect_color = Color(*self.background_color)
            self.rect = Rectangle(size=self.size, pos=self.pos)
        self.bind(pos=self._update_rect, size=self._update_rect)

        # Botón para marcar la tarea como completada
        self.complete_button = Button(
            text='◻️', # Cuadrado vacío
            size_hint_x=None,
            width=dp(50),
            font_size='20sp',
            background_normal='', # Eliminar el fondo predeterminado
            background_color=FG_COLOR, # Fondo negro para el botón
            color=BG_COLOR, # Texto blanco para el botón
            bold=True
        )
        self.complete_button.bind(on_release=self.toggle_completion)
        self.add_widget(self.complete_button)

        # Etiqueta para el texto de la tarea
        self.task_label = Label(
            text=self.task_text,
            halign='left',
            valign='middle',
            text_size=(self.width - dp(120), None), # Ajusta el ancho para el texto (ancho total - botones)
            size_hint_x=1,
            color=FG_COLOR, # Texto negro
            markup=True # Habilitar markup para tachado
        )
        # Vincular el tamaño del label al tamaño del widget padre para ajustar text_size
        self.bind(width=self._update_label_text_size)
        self.add_widget(self.task_label)

        # Botón para eliminar la tarea
        self.delete_button = Button(
            text='X',
            size_hint_x=None,
            width=dp(50),
            font_size='20sp',
            background_normal='',
            background_color=(0.8, 0.2, 0.2, 1), # Rojo suave
            color=BG_COLOR, # Texto blanco
            bold=True
        )
        self.delete_button.bind(on_release=self.delete_task)
        self.add_widget(self.delete_button)

        # Inicializar la UI según el estado de completado
        self._update_ui_for_completion()

    def _update_rect(self, instance, value):
        self.rect.pos = instance.pos
        self.rect.size = instance.size

    def _update_label_text_size(self, instance, value):
        # Actualiza text_size de la etiqueta cuando el ancho del TaskWidget cambia
        self.task_label.text_size = (self.width - dp(120), None)

    def toggle_completion(self, instance):
        self.is_completed = not self.is_completed
        self._update_ui_for_completion()
        # Notificar a la aplicación principal para guardar el estado
        App.get_running_app().save_tasks()

    def _update_ui_for_completion(self):
        if self.is_completed:
            self.complete_button.text = '✅' # Marca de verificación
            self.task_label.color = (0.5, 0.5, 0.5, 1) # Gris para texto completado
            self.task_label.text = f'[s]{self.task_text}[/s]' # Tachado
            self.background_color = (0.95, 0.95, 0.95, 1) # Fondo ligeramente gris
        else:
            self.complete_button.text = '◻️' # Cuadrado vacío
            self.task_label.color = FG_COLOR # Negro para texto pendiente
            self.task_label.text = self.task_text # Sin tachado
            self.background_color = BG_COLOR # Fondo blanco
        self.rect_color.rgba = self.background_color # Actualizar el color del rectángulo de fondo

    def delete_task(self, instance):
        # Kivy no tiene messagebox.askyesno directamente en el widget,
        # así que lo manejamos en el App.
        # Pedir confirmación a través de un método en la App principal
        App.get_running_app().confirm_delete_task(self)


# Clase principal de la aplicación
class TaskApp(App):
    def build(self):
        # Establecer el color de fondo de la ventana de Kivy
        Window.clearcolor = BG_COLOR

        # Layout principal: un BoxLayout vertical
        main_layout = BoxLayout(orientation='vertical', padding=dp(15), spacing=dp(10))
        main_layout.canvas.before.clear() # Limpiar el canvas predeterminado del BoxLayout
        with main_layout.canvas.before:
            from kivy.graphics import Color, Rectangle
            Color(*BG_COLOR)
            self.main_rect = Rectangle(size=main_layout.size, pos=main_layout.pos)
        main_layout.bind(pos=self._update_main_rect, size=self._update_main_rect)

        # Título de la aplicación
        title_label = Label(
            text="Mis Tareas",
            font_size='30sp',
            bold=True,
            color=FG_COLOR, # Texto negro
            size_hint_y=None,
            height=dp(50)
        )
        main_layout.add_widget(title_label)

        # 1. Sección para añadir nueva tarea
        add_task_layout = BoxLayout(orientation='horizontal', size_hint_y=None, height=dp(50), spacing=dp(5))

        self.new_task_input = TextInput(
            hint_text='Nueva tarea...',
            multiline=False,
            size_hint_x=1,
            font_size='18sp',
            background_normal='', # Eliminar el fondo predeterminado
            background_color=BG_COLOR, # Fondo blanco
            foreground_color=FG_COLOR, # Texto negro
            cursor_color=FG_COLOR, # Cursor negro
            padding=[dp(10), dp(10), dp(10), dp(10)] # Padding para el texto
        )
        add_task_layout.add_widget(self.new_task_input)

        add_button = Button(
            text='Añadir',
            size_hint_x=None,
            width=dp(120),
            font_size='18sp',
            background_normal='',
            background_color=FG_COLOR, # Fondo negro para el botón
            color=BG_COLOR, # Texto blanco para el botón
            bold=True
        )
        add_button.bind(on_release=self.add_task)
        add_task_layout.add_widget(add_button)

        main_layout.add_widget(add_task_layout)

        # 2. Área de visualización de tareas (con scroll)
        self.task_list_container = BoxLayout(orientation='vertical', spacing=dp(8), size_hint_y=None)
        # Necesario para que el ScrollView sepa el tamaño total de su contenido
        self.task_list_container.bind(minimum_height=self.task_list_container.setter('height'))

        scroll_view = ScrollView(do_scroll_x=False) # No permitir scroll horizontal
        scroll_view.add_widget(self.task_list_container)
        main_layout.add_widget(scroll_view)

        # Cargar algunas tareas de ejemplo al inicio
        self.load_tasks()

        return main_layout

    def _update_main_rect(self, instance, value):
        self.main_rect.pos = instance.pos
        self.main_rect.size = instance.size

    def add_task(self, instance):
        task_text = self.new_task_input.text.strip()
        if task_text:
            task_widget = TaskWidget(text=task_text)
            self.task_list_container.add_widget(task_widget)
            self.new_task_input.text = '' # Limpiar el input
            self.save_tasks() # Guardar el estado de las tareas
        else:
            # En Kivy, no usamos messagebox.showwarning directamente en el código de la app
            # sino que creamos un Popup o un Label temporal.
            # Para este ejemplo, simplemente no haremos nada si el texto está vacío.
            pass

    def confirm_delete_task(self, task_widget_to_delete):
        # Kivy no tiene un messagebox nativo como Tkinter.
        # Para una confirmación, se usaría un Popup.
        # Por simplicidad en este ejemplo, eliminaremos directamente.
        # En una app real, aquí iría un Popup para confirmar.
        self.remove_task_widget(task_widget_to_delete)

    def remove_task_widget(self, task_widget):
        self.task_list_container.remove_widget(task_widget)
        self.save_tasks() # Guardar el estado de las tareas

    def load_tasks(self):
        # Simulación de carga de tareas (podrías usar JSON, CSV, una base de datos real)
        # En una app real, leerías de un archivo o DB.
        # Para este ejemplo, solo cargaremos tareas de ejemplo.
        example_tasks = [
            {"text": "Comprar leche", "completed": False},
            {"text": "Estudiar Kivy", "completed": True},
            {"text": "Hacer ejercicio", "completed": False},
            {"text": "Planificar el fin de semana", "completed": False},
            {"text": "Llamar a mamá", "completed": True},
            {"text": "Preparar la cena", "completed": False},
            {"text": "Regar las plantas", "completed": False},
            {"text": "Revisar el correo", "completed": True},
            {"text": "Pagar las facturas", "completed": False},
            {"text": "Organizar el escritorio", "completed": False}
        ]
        for task_data in example_tasks:
            task_widget = TaskWidget(text=task_data["text"], completed=task_data["completed"])
            self.task_list_container.add_widget(task_widget)

    def save_tasks(self):
        # Simulación de guardado de tareas
        # En una app real, guardarías el estado de todas las tareas a un archivo o DB
        tasks_to_save = []
        for widget in self.task_list_container.children:
            # Kivy children están en orden inverso, así que iteramos y luego invertimos si es necesario
            if isinstance(widget, TaskWidget):
                tasks_to_save.append({
                    "text": widget.task_text,
                    "completed": widget.is_completed
                })
        # Las tareas se añaden al final, pero Kivy las muestra en orden inverso en children.
        # Si quieres el orden de adición, invierte la lista.
        tasks_to_save.reverse()
        print("Tareas guardadas (simulado):", tasks_to_save)

    def on_stop(self):
        # Opcional: Guarda las tareas cuando la aplicación se cierra
        self.save_tasks()


if __name__ == '__main__':
    TaskApp().run()
