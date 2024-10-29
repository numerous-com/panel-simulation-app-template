import threading
import time
import plotly.graph_objects as go
import panel as pn
from long_task.long_task import MySimulation

# Ensure Panel extensions are loaded
pn.extension()

# Assuming MySimulation class is already defined as shown before


# Panel App
class SimulationApp:
    def __init__(self):
        self.sim = MySimulation()
        self.input1 = pn.widgets.FloatInput(name='Input 1', value=1.0, start=0, end=10.0, step=0.1, format='0[.]0')
        self.input2 = pn.widgets.FloatInput(name='Input 2', value=0.0, start=-5, end=5.0, step=0.1, format='0[.]0')
        self.duration = pn.widgets.FloatSlider(
            name='Duration (s)', 
            value=5.0, 
            start=0.1, 
            end=10.0, 
            step=0.1,
            format='0[.]0',
        )
        self.start_button = pn.widgets.Button(name='Start', button_type='primary', stylesheets=['button { border-radius: 0 !important; background-color: black !important; border-color: black !important; }'])
        self.stop_button = pn.widgets.Button(name='Stop', button_type='danger', stylesheets=['button { border-radius: 0 !important; }'])
        self.progress_bar = pn.widgets.Progress(name='Progress', value=0)
        self.result_text = pn.pane.Markdown("")
        self.plot_pane = pn.pane.Plotly(height=300)
        
        # Bind actions
        self.start_button.on_click(self.start_simulation)
        self.stop_button.on_click(self.stop_simulation)

        # Layout
        inputs_card = pn.Card(
            pn.Column(pn.Row(self.input1, self.input2), pn.Row(self.duration)),
            title='Simulation Parameters',
            styles={
                'border': '1px solid #ddd',
                'border-radius': '4px',
                'padding': '10px',
                'margin-bottom': '10px'
            }
        )

        controls_card = pn.Card(
            pn.Column(
                pn.Row(self.start_button, self.stop_button),
                pn.Column("Progress: ", self.progress_bar),
                self.result_text,
                self.plot_pane
            ),
            title='Simulation Controls',
            styles={
                'border': '1px solid #ddd',
                'border-radius': '4px',
                'padding': '10px',
                'margin-bottom': '10px'
            }
        )

        # Update main layout
        self.layout = pn.Column(
            inputs_card,
            controls_card
        )

        # Add list of controls to manage
        self.input_controls = [self.input1, self.input2, self.duration, self.start_button]

    def start_simulation(self, event):
        if not self.sim.alive:
            self.result_text.object = ""
            # Disable inputs
            for control in self.input_controls:
                control.disabled = True
            threading.Thread(target=self.run_simulation).start()

    def run_simulation(self):       
        
        self.sim.start(self.duration.value, self.input1.value, self.input2.value)

        while self.sim.alive:
            self.progress_bar.value = int(round(self.sim.progress * 100))
            time.sleep(0.1)

        try:
            results = self.sim.result
            self.result_text.object = f"Result: {results[0]}"
            t, y = results[1], results[2]
            
            # Create Plotly figure
            fig = go.Figure()
            fig.add_trace(
                go.Scatter(
                    x=t,
                    y=y,
                    mode='lines',
                    name='Simulation'
                )
            )
            
            # Update layout
            fig.update_layout(
                title='Simulation Results',
                height=300,
                margin=dict(l=50, r=20, t=40, b=50),
                showlegend=False,
                template='plotly_white'
            )
            print("!")
            
            self.plot_pane.object = fig
            
        except Exception as e:
            self.result_text.object = f"Error: {str(e)}"
            self.plot_pane.object = None  # Clear plot on error
        finally:
            # Re-enable inputs when simulation ends
            for control in self.input_controls:
                control.disabled = False

        self.progress_bar.value = int(round(self.sim.progress * 100))

    def stop_simulation(self, event):
        if self.sim.alive:
            self.sim.stop()
            self.result_text.object = "Simulation stopped."
            self.plot_pane.object = None  # Clear plot when stopped
            # Re-enable inputs when stopped
            for control in self.input_controls:
                control.disabled = False

app_instance = SimulationApp()

app = pn.template.BootstrapTemplate(
    title="Template Simulation App",
    header_background="#333333",  # Dark gray color
    main=[app_instance.layout],
)

app.servable()

if __name__ == "__main__":
    # Serve the app on a local Panel server
    pn.serve(app, port=5006)  # You can specify the port if needed
