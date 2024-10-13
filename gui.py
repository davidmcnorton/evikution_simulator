# gui.py

from PyQt5.QtCore import QObject, pyqtSignal, Qt
from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QWidget, QPushButton,
    QVBoxLayout, QHBoxLayout, QLabel, QSlider, QGroupBox, QTextEdit
)
from PyQt5.QtGui import QFont, QColor, QPen, QBrush
from PyQt5.QtWidgets import QGraphicsEllipseItem  # Correct Import
import sys
import pyqtgraph as pg
import matplotlib.pyplot as plt
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from simulation import Simulation  # Ensure this module is correctly implemented
import threading
import time
import numpy as np  # Ensure numpy is imported


# Define the Communicate class for signal-slot mechanism
class Communicate(QObject):
    update_map_signal = pyqtSignal(dict)
    update_plot_signal = pyqtSignal(dict)
    update_stats_signal = pyqtSignal(dict)
    log_signal = pyqtSignal(str)


class EvolutionSimulatorGUI(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Evolution Simulator")
        self.setGeometry(100, 100, 1400, 900)  # Increased size for better layout

        # Initialize simulation
        self.simulation = Simulation(initial_population=100, mutation_rate=0.05, generations=50)

        # Initialize history dictionaries
        self.history_predators = {region.name: [] for region in self.simulation.regions}

        # Initialize speed (default value)
        self.speed = 0.002  # Corresponds to speed slider value 50 (0.1 / 50)

        # Setup UI
        self.init_ui()

        # Setup communication signals
        self.communicate = Communicate()
        self.communicate.update_map_signal.connect(self.update_live_map)
        self.communicate.update_plot_signal.connect(self.update_plot)
        self.communicate.update_stats_signal.connect(self.update_statistics)
        self.communicate.log_signal.connect(self.log)

        # Thread control
        self.simulation_thread = None
        self.thread_lock = threading.Lock()

        # Keep track of territory circles to prevent accumulation
        self.territory_circles = []

    def init_ui(self):
        # Main widget
        main_widget = QWidget()
        self.setCentralWidget(main_widget)

        # Main layout
        main_layout = QHBoxLayout()
        main_widget.setLayout(main_layout)

        # Control Panel
        control_panel = QGroupBox("Controls")
        control_layout = QVBoxLayout()
        control_panel.setLayout(control_layout)

        # Start Button
        start_button = QPushButton("Start Simulation")
        start_button.setStyleSheet("""
            QPushButton {
                background-color: #4CAF50;
                color: white;
                font-size: 16px;
                padding: 10px;
                border-radius: 5px;
            }
            QPushButton:hover {
                background-color: #45a049;
            }
        """)
        start_button.clicked.connect(self.start_simulation)
        control_layout.addWidget(start_button)

        # Pause Button
        pause_button = QPushButton("Pause Simulation")
        pause_button.setStyleSheet("""
            QPushButton {
                background-color: #f44336;
                color: white;
                font-size: 16px;
                padding: 10px;
                border-radius: 5px;
            }
            QPushButton:hover {
                background-color: #da190b;
            }
        """)
        pause_button.clicked.connect(self.pause_simulation)
        control_layout.addWidget(pause_button)

        # Reset Button
        reset_button = QPushButton("Reset Simulation")
        reset_button.setStyleSheet("""
            QPushButton {
                background-color: #2196F3;
                color: white;
                font-size: 16px;
                padding: 10px;
                border-radius: 5px;
            }
            QPushButton:hover {
                background-color: #0b7dda;
            }
        """)
        reset_button.clicked.connect(self.reset_simulation)
        control_layout.addWidget(reset_button)

        # Mutation Rate Slider
        mutation_group = QGroupBox("Mutation Rate")
        mutation_layout = QVBoxLayout()
        mutation_group.setLayout(mutation_layout)
        mutation_label = QLabel(f"{int(self.simulation.mutation_rate * 100)}%")
        mutation_label.setAlignment(Qt.AlignCenter)
        mutation_label.setFont(QFont("Arial", 12))
        mutation_layout.addWidget(mutation_label)
        mutation_slider = QSlider(Qt.Horizontal)
        mutation_slider.setMinimum(0)
        mutation_slider.setMaximum(100)
        mutation_slider.setValue(int(self.simulation.mutation_rate * 100))
        mutation_slider.setTickInterval(10)
        mutation_slider.setTickPosition(QSlider.TicksBelow)
        mutation_slider.valueChanged.connect(lambda value: self.change_mutation_rate(value, mutation_label))
        mutation_layout.addWidget(mutation_slider)
        control_layout.addWidget(mutation_group)

        # Generations Slider
        generations_group = QGroupBox("Number of Generations")
        generations_layout = QVBoxLayout()
        generations_group.setLayout(generations_layout)
        generations_label = QLabel(str(self.simulation.generations))
        generations_label.setAlignment(Qt.AlignCenter)
        generations_label.setFont(QFont("Arial", 12))
        generations_layout.addWidget(generations_label)
        generations_slider = QSlider(Qt.Horizontal)
        generations_slider.setMinimum(10)
        generations_slider.setMaximum(500)
        generations_slider.setValue(self.simulation.generations)
        generations_slider.setTickInterval(50)
        generations_slider.setTickPosition(QSlider.TicksBelow)
        generations_slider.valueChanged.connect(lambda value: self.change_generations(value, generations_label))
        generations_layout.addWidget(generations_slider)
        generations_group.setStyleSheet("""
            QGroupBox {
                font-size: 14px;
                font-weight: bold;
            }
        """)
        control_layout.addWidget(generations_group)

        # Speed Adjuster Slider
        speed_group = QGroupBox("Simulation Speed")
        speed_layout = QVBoxLayout()
        speed_group.setLayout(speed_layout)
        speed_label = QLabel("Speed: 50")
        speed_label.setAlignment(Qt.AlignCenter)
        speed_label.setFont(QFont("Arial", 12))
        speed_layout.addWidget(speed_label)
        speed_slider = QSlider(Qt.Horizontal)
        speed_slider.setMinimum(1)   # Slowest
        speed_slider.setMaximum(100) # Fastest
        speed_slider.setValue(50)    # Default speed
        speed_slider.setTickInterval(10)
        speed_slider.setTickPosition(QSlider.TicksBelow)
        speed_slider.valueChanged.connect(lambda value: self.change_speed(value, speed_label))
        speed_layout.addWidget(speed_slider)
        control_layout.addWidget(speed_group)

        # Log Panel
        log_group = QGroupBox("Simulation Logs")
        log_layout = QVBoxLayout()
        log_group.setLayout(log_layout)
        self.log_text = QTextEdit()
        self.log_text.setReadOnly(True)
        self.log_text.setStyleSheet("""
            QTextEdit {
                background-color: #f0f0f0;
                font-family: Consolas;
                font-size: 12px;
            }
        """)
        log_layout.addWidget(self.log_text)
        control_layout.addWidget(log_group)

        # Spacer
        control_layout.addStretch()

        # Plot Area
        plot_area = QGroupBox("Fitness Over Generations")
        plot_layout = QVBoxLayout()
        plot_area.setLayout(plot_layout)
        self.figure, self.ax = plt.subplots()
        self.ax.set_title("Average Fitness")
        self.ax.set_xlabel("Generation")
        self.ax.set_ylabel("Average Fitness")
        self.ax.grid(True)
        self.canvas = FigureCanvas(self.figure)
        plot_layout.addWidget(self.canvas)

        # Live Map Area
        map_area = QGroupBox("Live Map")
        map_layout = QVBoxLayout()
        map_area.setLayout(map_layout)
        self.live_map = pg.PlotWidget(title="Live Map")
        self.live_map.setBackground('w')  # Set white background
        self.live_map.addLegend()
        self.live_map.setLabel('left', 'Y Position')
        self.live_map.setLabel('bottom', 'X Position')
        map_layout.addWidget(self.live_map)

        # Add Control and Visualization Panels to Main Layout
        main_layout.addWidget(control_panel, 1)
        visualization_layout = QVBoxLayout()
        visualization_layout.addWidget(plot_area, 2)
        visualization_layout.addWidget(map_area, 3)
        main_layout.addLayout(visualization_layout, 3)

    def draw_circle(self, x, y, radius, pen_color='b'):
        """
        Draws a dashed circle on the live map representing a territory.

        :param x: X-coordinate of the center.
        :param y: Y-coordinate of the center.
        :param radius: Radius of the territory.
        :param pen_color: Color of the territory circle.
        """
        # Create an ellipse item
        territory_circle = QGraphicsEllipseItem(x - radius, y - radius, radius * 2, radius * 2)
        
        # Set pen with dashed line style
        pen = QPen(QColor(pen_color))
        pen.setWidth(1)
        pen.setStyle(Qt.DashLine)
        territory_circle.setPen(pen)
        
        # Set semi-transparent brush
        brush = QBrush(QColor(0, 0, 255, 50))  # Semi-transparent blue
        territory_circle.setBrush(brush)
        
        # Add the ellipse to the live_map's scene
        self.live_map.scene().addItem(territory_circle)
        
        # Keep track of territory circles to remove them later
        self.territory_circles.append(territory_circle)

    def start_simulation(self):
        with self.thread_lock:
            if self.simulation_thread is None or not self.simulation_thread.is_alive():
                self.running = True
                # Reset histories to prevent accumulation from previous runs
                for region in self.simulation.regions:
                    self.simulation.history[region.name] = []
                    self.history_predators[region.name] = []

                # Clear existing territory circles
                for circle in self.territory_circles:
                    self.live_map.scene().removeItem(circle)
                self.territory_circles.clear()

                # Start simulation thread
                self.simulation_thread = threading.Thread(target=self.run_simulation)
                self.simulation_thread.start()
                self.log("Simulation started.")
            else:
                self.log("Simulation is already running.")

    def pause_simulation(self):
        with self.thread_lock:
            if hasattr(self, 'running') and self.running:
                self.running = False
                if self.simulation_thread is not None:
                    self.simulation_thread.join()
                    self.simulation_thread = None
                self.log("Simulation paused.")
            else:
                self.log("No active simulation to pause.")

    def reset_simulation(self):
        with self.thread_lock:
            # Stop simulation if running
            if hasattr(self, 'running') and self.running:
                self.running = False
                if self.simulation_thread is not None:
                    self.simulation_thread.join()
                    self.simulation_thread = None
                self.log("Simulation stopped for reset.")

            # Reset simulation parameters
            # Re-initialize the simulation object
            self.simulation = Simulation(
                initial_population=100,
                mutation_rate=self.simulation.mutation_rate,
                generations=self.simulation.generations
            )

            # Reset histories
            for region in self.simulation.regions:
                self.simulation.history[region.name] = []
                self.history_predators[region.name] = []

            # Clear territories
            for circle in self.territory_circles:
                self.live_map.scene().removeItem(circle)
            self.territory_circles.clear()

            # Clear plots and logs
            self.ax.clear()
            self.canvas.draw()
            self.live_map.clear()
            self.log_text.clear()
            self.log("Simulation reset.")

    def run_simulation(self):
        for gen in range(self.simulation.generations):
            if not self.running:
                break
            self.simulation.run()
            # Update history_predators
            for region in self.simulation.regions:
                self.history_predators[region.name].append(region.calculate_average_predator_fitness())

            # Prepare stats
            stats = {
                'generation': gen + 1,
                'regions': {
                    region.name: {
                        'animal_fitness': region.calculate_average_fitness(),
                        'predator_fitness': region.calculate_average_predator_fitness()
                    }
                    for region in self.simulation.regions
                }
            }

            # Emit signals to update GUI
            self.communicate.update_stats_signal.emit(stats)
            self.communicate.update_plot_signal.emit(stats)

            # Gather positions for live map
            positions_animals = {}
            positions_plants = {}
            positions_predators = {}
            for region in self.simulation.regions:
                positions_animals[region.name] = [(animal.x, animal.y) for animal in region.animals]
                positions_plants[region.name] = [(plant.x, plant.y) for plant in region.plants]
                positions_predators[region.name] = [(predator.x, predator.y) for predator in region.predators]
            map_data = {
                'plants': positions_plants,
                'animals': positions_animals,
                'predators': positions_predators
            }
            self.communicate.update_map_signal.emit(map_data)

            # Log each generation
            for region in self.simulation.regions:
                animal_fitness = stats['regions'][region.name]['animal_fitness']
                predator_fitness = stats['regions'][region.name]['predator_fitness']
                resources = region.environment.resources
                log_message = (
                    f"Generation {gen + 1} - Region {region.name}: "
                    f"Avg Animal Fitness = {animal_fitness:.2f}, "
                    f"Avg Predator Fitness = {predator_fitness:.2f}, "
                    f"Resources = {resources:.2f}"
                )
                self.communicate.log_signal.emit(log_message)

            # Adjust simulation speed
            time.sleep(self.speed)  # Controlled by speed adjuster

        self.running = False
        self.simulation_thread = None
        self.communicate.log_signal.emit("Simulation completed.")

    def update_plot(self, stats):
        """
        Updates the Matplotlib plot with new data.
        """
        current_gen = stats['generation']
        self.ax.clear()
        self.ax.set_title("Average Fitness Over Generations")
        self.ax.set_xlabel("Generation")
        self.ax.set_ylabel("Average Fitness")
        self.ax.grid(True)
        for region in self.simulation.regions:
            animal_fitness = self.simulation.history[region.name]
            predator_fitness = self.history_predators[region.name]
            # Ensure that the x-axis matches the y-axis data length
            self.ax.plot(
                range(1, len(animal_fitness) + 1),
                animal_fitness,
                label=f"{region.name} Animals",
                linestyle='-',
                marker='o'
            )
            self.ax.plot(
                range(1, len(predator_fitness) + 1),
                predator_fitness,
                label=f"{region.name} Predators",
                linestyle='--',
                marker='x'
            )
        self.ax.legend()
        self.canvas.draw()

    def update_live_map(self, map_data):
        """
        Updates the live map with new positions of lifeforms and their territories.
        """
        # Clear existing lifeforms but retain territories
        # To retain territories, we first remove only lifeforms
        # However, since territories are separate items tracked in self.territory_circles,
        # we clear the map and redraw territories
        self.live_map.clear()

        colors = {'plants': 'green', 'animals': 'blue', 'predators': 'red'}
        symbols = {'plants': 'o', 'animals': 'o', 'predators': 'x'}

        for lifeform_type, regions in map_data.items():
            for region_name, positions in regions.items():
                if positions:
                    x, y = zip(*positions)
                    self.live_map.plot(
                        x, y,
                        pen=None,
                        symbol=symbols[lifeform_type],
                        symbolBrush=colors[lifeform_type],
                        symbolSize=8,
                        name=f"{region_name} {lifeform_type}"
                    )

                    # Draw territories
                    region = next((r for r in self.simulation.regions if r.name == region_name), None)
                    if region:
                        if lifeform_type == 'animals':
                            for animal in region.animals:
                                self.draw_circle(animal.x, animal.y, animal.territory, pen_color='blue')
                        elif lifeform_type == 'predators':
                            for predator in region.predators:
                                self.draw_circle(predator.x, predator.y, predator.territory, pen_color='red')
        self.live_map.addLegend()

    def update_statistics(self, stats):
        """
        Updates the statistics panel with new data.
        """
        # Placeholder for future detailed statistics display
        pass

    def log(self, message):
        """
        Logs messages to the log panel.
        """
        current_text = self.log_text.toPlainText()
        new_text = current_text + message + "\n"
        self.log_text.setPlainText(new_text)
        # Auto-scroll to the bottom
        self.log_text.verticalScrollBar().setValue(self.log_text.verticalScrollBar().maximum())

    def change_mutation_rate(self, value, label):
        """
        Changes the mutation rate based on the slider value and updates the label.
        """
        mutation_rate = value / 100.0
        self.simulation.mutation_rate = mutation_rate
        for region in self.simulation.regions:
            region.mutation_rate = mutation_rate
        label.setText(f"{value}%")
        self.log(f"Mutation rate set to {mutation_rate}")

    def change_generations(self, value, label):
        """
        Changes the number of generations based on the slider value and updates the label.
        """
        self.simulation.generations = value
        label.setText(str(value))
        self.log(f"Generations set to {value}")

    def change_speed(self, value, label):
        """
        Changes the simulation speed based on the slider value and updates the label.
        Higher value means faster simulation (shorter sleep duration).
        """
        # Map slider value (1-100) to sleep duration (0.1 to 0.001 seconds)
        # Using inverse relationship: speed = 100 -> sleep = 0.001, speed = 1 -> sleep = 0.1
        self.speed = 0.1 / value
        label.setText(f"Speed: {value}")
        self.log(f"Simulation speed set to {value}")

    def closeEvent(self, event):
        """
        Handle the window close event to ensure threads are properly terminated.
        """
        with self.thread_lock:
            if hasattr(self, 'running') and self.running:
                self.running = False
                if self.simulation_thread is not None:
                    self.simulation_thread.join()
        event.accept()


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = EvolutionSimulatorGUI()
    window.show()
    sys.exit(app.exec_())
















