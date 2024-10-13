# simulation.py

import numpy as np
import random
from region import Region
from environment import Environment
from lifeform import Lifeform
from plant import Plant
from animal import Animal
from predator import Predator
import copy  # Import copy for deep copying traits

class Simulation:
    def __init__(self, initial_population=100, mutation_rate=0.05, generations=50):
        """
        Initializes the Simulation with specified parameters.

        :param initial_population: Number of lifeforms per region at the start.
        :param mutation_rate: Probability of gene mutation during reproduction.
        :param generations: Total number of generations to simulate.
        """
        self.initial_population = initial_population
        self.mutation_rate = mutation_rate
        self.generations = generations
        self.regions = self.create_regions()
        self.history = {region.name: [] for region in self.regions}
        self.history_predators = {region.name: [] for region in self.regions}  # Separate history for predators

    def create_regions(self):
        """
        Creates multiple regions with distinct environments.

        :return: List of Region objects.
        """
        regions = []
        # Example: Creating four regions with different resource levels
        environments = [
            Environment(name="North", resources=100),
            Environment(name="South", resources=80),
            Environment(name="East", resources=60),
            Environment(name="West", resources=40)
        ]
        for env in environments:
            region = Region(name=env.name, environment=env, initial_population=self.initial_population, mutation_rate=self.mutation_rate)
            regions.append(region)
        return regions

    def run(self):
        """
        Runs one generation of the simulation across all regions.
        """
        for region in self.regions:
            region.simulate_generation()
            avg_fitness = region.calculate_average_fitness()
            avg_predator_fitness = region.calculate_average_predator_fitness()
            self.history[region.name].append(avg_fitness)
            self.history_predators[region.name].append(avg_predator_fitness)









