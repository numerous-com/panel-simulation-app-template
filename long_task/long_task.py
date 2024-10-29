import multiprocessing
import time
import traceback


class Task:
    def __init__(self, stop_message="Process was forcefully terminated."):
        self._process = None
        self._progress = multiprocessing.Value("d", 0.0)  # Shared progress value
        self._result_queue = multiprocessing.Queue()
        self._exception_queue = multiprocessing.Queue()
        self._return_value = None
        self._exception = None
        self.stop_message = stop_message

    def _run_wrapper(self, *args, **kwargs):
        try:
            result = self.run(*args, **kwargs)
            self._result_queue.put(result)
        except Exception as e:
            self._exception_queue.put((e, traceback.format_exc()))
        finally:
            self._progress.value = 1.0  # Mark as complete

    def run(self, *args, **kwargs):
        """Override this method in subclasses to define the simulation."""
        raise NotImplementedError("The run method must be implemented by the subclass.")

    def start(self, *args, **kwargs):
        if self._process is None or not self._process.is_alive():
            self._progress.value = 0.0
            self._return_value = None
            self._exception = None
            self._process = multiprocessing.Process(
                target=self._run_wrapper, args=args, kwargs=kwargs
            )
            self._process.start()

    def stop(self):
        if self._process and self._process.is_alive():
            self._process.terminate()
            self._process.join()  # Ensure process is terminated
            self._exception = RuntimeError(self.stop_message)

    def join(self):
        if self._process:
            self._process.join()

    @property
    def alive(self):
        return self._process.is_alive() if self._process else False

    @property
    def progress(self):
        return self._progress.value

    @property
    def result(self):
        if self._process is not None:
            self._process.join()  # Wait for process to finish

        if self._exception is not None:
            raise self._exception

        if not self._result_queue.empty():
            self._return_value = self._result_queue.get()

        if not self._exception_queue.empty():
            exc, tb = self._exception_queue.get()
            raise RuntimeError(f"Exception in process:\n{tb}") from exc

        return self._return_value

    @property
    def exception(self):
        if not self._exception_queue.empty():
            exc, tb = self._exception_queue.get()
            return exc
        return None


# Example subclass implementation
class MySimulation(Task):
    def __init__(self):
        super().__init__(stop_message="Simulation was stopped.")

    def run(self, duration, input1:float, input2:float):

        y = input1
        power = input2
        result = []
        t = []

        for i in range(int(duration * 10)):
            # Pseudocode for a simulation

            loss = y * 0.01
            dy = power/10 - loss
            
            y += dy

            result.append(y)
            t.append(i/10)

            if self._progress.value >= 1.0:
                break
            self._progress.value = i / (duration * 10)
            time.sleep(0.01)

        
        return "Simulation complete!", t, result


# Example usage
if __name__ == "__main__":
    sim = MySimulation()
    sim.start(5)  # Run simulation for 5 seconds
    while sim.alive:
        print(f"Progress: {sim.progress:.2%}")
        if sim.progress > 0.5:
            print("Stopping the simulation!")
            sim.stop()
        time.sleep(0.5)

    print(f"Result: {sim.result}")
