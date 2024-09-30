import threading
import time

import panel as pn

from long_task.long_task import MySimulation

# Ensure Panel extensions are loaded
pn.extension()

# Assuming MySimulation class is already defined as shown before


# Panel App
class SimulationApp:
    def __init__(self):
        self.sim = MySimulation()
        self.input1 = pn.widgets.FloatInput(
            name="Input 1", value=1.0, start=0.1, end=10.0, step=0.1
        )
        self.input2 = pn.widgets.FloatInput(
            name="Input 2", value=2.0, start=0.1, end=10.0, step=0.1
        )
        self.duration = pn.widgets.FloatInput(
            name="Duration (s)", value=2.0, start=1.0, end=100.0, step=0.1
        )
        self.start_button = pn.widgets.Button(name="Start", button_type="primary")
        self.stop_button = pn.widgets.Button(name="Stop", button_type="danger")
        self.progress_bar = pn.widgets.Progress(name="Progress", value=0)
        self.result_text = pn.pane.Markdown("")

        # Bind actions
        self.start_button.on_click(self.start_simulation)
        self.stop_button.on_click(self.stop_simulation)

        # Layout
        self.layout = pn.Column(
            pn.Row(self.input1, self.input2),
            pn.Row(self.duration),
            pn.Row(self.start_button, self.stop_button),
            self.progress_bar,
            self.result_text,
        )

    def start_simulation(self, event):
        if not self.sim.alive:
            self.result_text.object = ""
            threading.Thread(target=self.run_simulation).start()

    def run_simulation(self):
        self.sim.start(self.duration.value)

        while self.sim.alive:
            self.progress_bar.value = int(round(self.sim.progress * 100))
            time.sleep(0.1)

        try:
            result = self.sim.result
            self.result_text.object = f"Result: {result}"

        except Exception as e:
            self.result_text.object = f"Error: {str(e)}"

        self.progress_bar.value = int(round(self.sim.progress * 100))

    def stop_simulation(self, event):
        if self.sim.alive:
            self.sim.stop()
            self.result_text.object = "Simulation stopped."


app_instance = SimulationApp()

app = pn.template.BootstrapTemplate(
    title="Template Simulation App",
    main=[app_instance.layout],
)

app.servable()

if __name__ == "__main__":
    # Serve the app on a local Panel server
    pn.serve(app, port=5006)  # You can specify the port if needed
