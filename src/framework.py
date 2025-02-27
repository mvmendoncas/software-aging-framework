import argparse
import sys
import time

import pandas as pd
from matplotlib import pyplot as plt

from src.forecasting import Forecasting
from src.monitor import ResourceMonitorProcess


class Framework:
    def __init__(
        self,
        run_monitoring: bool,
        resources_to_predict: list[str],
        monitoring_time_in_seconds: int,
        monitoring_interval_in_seconds: int,
        filename: str,
        model: str,
        save_plot: bool,
        run_in_real_time: bool,
    ):
        self.run_monitoring = run_monitoring
        self.resources = resources_to_predict
        self.monitoring_time_in_seconds = monitoring_time_in_seconds
        self.monitoring_interval_in_seconds = monitoring_interval_in_seconds
        self.filename = filename
        self.model_name = model
        self.save_plot = save_plot
        self.run_in_real_time = run_in_real_time
        self.forecasting = None
        self.monitor_process = None
        if self.run_monitoring:
            self.monitor_process = ResourceMonitorProcess(
                self.monitoring_interval_in_seconds, self.filename
            )

    def run(self):
        if self.run_in_real_time:
            self.__run_real_time()
        else:
            self.__run_experiment()

    def __run_monitoring(self):
        self.monitor_process.start()
        self.__countdown()
        self.__stop()

    def __run_experiment(self):
        if self.run_monitoring:
            self.__run_monitoring()

        dataframe = pd.read_csv(self.filename)

        self.forecasting = Forecasting(dataframe, self.model_name, self.resources)
        self.forecasting.train()
        self.__plot_graph()
        # TODO: add rejuvenation

    def __run_real_time(self):
        ...

    def __stop(self):
        self.monitor_process.terminate()

    def __print_progress_bar(self, current_second, text):
        progress_bar_size = 50
        current_progress = (current_second + 1) / self.monitoring_time_in_seconds
        sys.stdout.write(
            f"\r{text}: [{'=' * int(progress_bar_size * current_progress):{progress_bar_size}s}] "
            f"{current_second + 1}/{self.monitoring_time_in_seconds} seconds"
        )
        sys.stdout.flush()

    def __countdown(self):
        for current_second in range(self.monitoring_time_in_seconds):
            self.__print_progress_bar(current_second, "Monitoring")
            time.sleep(self.monitoring_interval_in_seconds)
        print()

    def __plot_graph(self):
        self.forecasting.model.plot_results()

        if self.save_plot:
            path_to_save = self.filename.replace(".csv", ".png")
            plt.savefig(path_to_save, dpi=300)

        plt.show()


class FrameworkCLI:
    def __init__(self):
        self.parser = argparse.ArgumentParser(
            description="Framework to monitoring and prevent software aging"
        )
        self.parser.add_argument(
            "--model",
            type=str,
            default="h_lstm",
            choices=[
                "ma",
                "h_lstm",
            ],  # TODO: Add support to more models (LSTM, ARIMA, ConvLSTM, etc.)
            help="Model for time series prediction",
        )
        self.parser.add_argument(
            "--run-monitoring",
            action="store_true",
            help="Run the monitoring process",
        )
        self.parser.add_argument(
            "--resources-to-predict",
            type=list[str],
            default=["CPU", "Mem", "Disk"],
            help=(
                "List of resources to predict, all resources are monitored either way. "
                "Available resources: CPU, Mem, Disk"
            ),
        )
        self.parser.add_argument(
            "--monitoring-time-in-seconds",
            type=int,
            default=60,
            help="Time in seconds to monitor the resource usage (only if --run-monitoring is True)",
        )
        self.parser.add_argument(
            "--monitoring-interval-in-seconds",
            type=int,
            default=1,
            help="Interval between each monitoring in seconds (only if --run-monitoring is True)",
        )
        self.parser.add_argument(
            "--filename",
            type=str,
            default="/home/gabriel/Repositories/software-aging-framework/data/real_monitoring.csv",
            help=(
                "Path to save the monitoring data (only if --run-monitoring is True) or "
                "path to read the monitoring data (only if --run-monitoring is False)"
            ),
        )
        self.parser.add_argument(
            "--save-plot",
            action="store_true",
            help="Save the plot as a png file",
        )
        self.parser.add_argument(
            "--run-in-real-time",
            action="store_true",
            help="Run the monitoring and prediction in real time (only if --run-monitoring is True)",
        )
        args = self.parser.parse_args()

        framework = Framework(**vars(args))
        framework.run()
