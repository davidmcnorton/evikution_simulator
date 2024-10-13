# region.py

import numpy as np
from lifeform import Lifeform
from traits import Trait
from plant import Plant
from animal import Animal
from predator import Predator
import copy  # Import copy for deep copying traits

class Region:
    def __init__(self, name, environment, initial_population=100, mutation_rate=0.05):
        """
        Initializes a Region with a specific environment and population.

        :param name: Name of the region.
        :param environment: Environment object associated with the region.
        :param initial_population: Number of lifeforms to initialize in the region.
        :param mutation_rate: Probability of gene mutation during reproduction.
        """
        self.name = name
        self.environment = environment
        self.mutation_rate = mutation_rate  # Correctly assigned here
        self.traits = self.define_traits()
        # Initialize lifeforms: plants, animals, and predators
        self.plants = self.initialize_plants(initial_population // 3)
        self.animals = self.initialize_animals(initial_population // 3)
        self.predators = self.initialize_predators(initial_population // 3)

    def define_traits(self):
        """
        Defines the traits for lifeforms in this region.

        :return: List of Trait objects.
        """
        return [
            Trait(name="Speed", gene_length=2, dominance="dominant"),
            Trait(name="Size", gene_length=2, dominance="recessive"),
            Trait(name="Camouflage", gene_length=2, dominance="co-dominant"),
            Trait(name="HuntingSkill", gene_length=2, dominance="dominant"),
            Trait(name="Territoriality", gene_length=2, dominance="dominant"),  # New trait
            Trait(name="Stealth", gene_length=2, dominance="dominant"),        # New trait
            Trait(name="Aggressiveness", gene_length=2, dominance="dominant")  # New trait
        ]

    def initialize_plants(self, count):
        """
        Initializes the plant population.

        :param count: Number of plants to create.
        :return: List of Plant objects.
        """
        return [
            Plant(
                traits=copy.deepcopy(self.traits),
                environment=self.environment,
                mutation_rate=self.mutation_rate
            )
            for _ in range(count)
        ]

    def initialize_animals(self, count):
        """
        Initializes the animal population.

        :param count: Number of animals to create.
        :return: List of Animal objects.
        """
        return [
            Animal(
                traits=copy.deepcopy(self.traits),
                environment=self.environment,
                mutation_rate=self.mutation_rate
            )
            for _ in range(count)
        ]

    def initialize_predators(self, count):
        """
        Initializes the predator population.

        :param count: Number of predators to create.
        :return: List of Predator objects.
        """
        return [
            Predator(
                traits=copy.deepcopy(self.traits),
                environment=self.environment,
                mutation_rate=self.mutation_rate
            )
            for _ in range(count)
        ]

    def simulate_generation(self):
        """
        Simulates one generation within the region.
        """
        # Simulate plant regeneration
        self.regenerate_plants()

        # Simulate animal actions
        for animal in self.animals:
            if not animal.alive:
                continue
            animal.move()
            # Animal attempts to consume nearby plants
            plant = self.find_nearby_plant(animal)
            if plant:
                animal.consume_plant(plant)
            # Check if animal can reproduce
            offspring = animal.reproduce()
            if offspring:
                self.animals.append(offspring)

        # Simulate predator actions
        for predator in self.predators:
            if not predator.alive:
                continue
            predator.move()
            # Predator attempts to consume nearby animals
            prey = self.find_nearby_animal(predator)
            if prey:
                predator.consume_animal(prey)
            # Check if predator can reproduce
            offspring = predator.reproduce()
            if offspring:
                self.predators.append(offspring)

        # Remove dead animals and predators
        self.animals = [animal for animal in self.animals if animal.alive]
        self.predators = [predator for predator in self.predators if predator.alive]

        # Remove depleted plants
        self.plants = [plant for plant in self.plants if plant.resource_value > 0]

        # Optionally, limit population sizes
        self.limit_population()

    def regenerate_plants(self):
        """
        Regenerates plants based on environmental resources.
        """
        for plant in self.plants:
            plant.regenerate()

    def find_nearby_plant(self, animal):
        """
        Finds a plant near the animal for consumption.

        :param animal: Animal object.
        :return: Plant object if found, else None.
        """
        search_radius = 5  # Define how far the animal can search for plants
        # Shuffle plants to introduce randomness in selection
        shuffled_plants = self.plants.copy()
        np.random.shuffle(shuffled_plants)
        for plant in shuffled_plants:
            distance = np.hypot(animal.x - plant.x, animal.y - plant.y)
            if distance <= search_radius:
                return plant
        return None

    def find_nearby_animal(self, predator):
        """
        Finds an animal near the predator for consumption.

        :param predator: Predator object.
        :return: Animal object if found, else None.
        """
        search_radius = 5  # Define how far the predator can search for animals
        shuffled_animals = self.animals.copy()
        np.random.shuffle(shuffled_animals)
        for animal in shuffled_animals:
            distance = np.hypot(predator.x - animal.x, predator.y - animal.y)
            if distance <= search_radius:
                return animal
        return None

    def remove_plant(self, plant):
        """
        Removes a plant from the region.

        :param plant: Plant object to remove.
        """
        if plant in self.plants:
            self.plants.remove(plant)

    def limit_population(self):
        """
        Limits the population sizes to prevent uncontrolled growth.
        """
        max_plants = 200
        max_animals = 150
        max_predators = 100  # Define a cap for predators
        if len(self.plants) > max_plants:
            self.plants = self.plants[:max_plants]
        if len(self.animals) > max_animals:
            self.animals = self.animals[:max_animals]
        if len(self.predators) > max_predators:
            self.predators = self.predators[:max_predators]

    def calculate_average_fitness(self):
        """
        Calculates the average fitness of the animal population in the region.

        :return: Average fitness as a float.
        """
        if not self.animals:
            return 0
        total_fitness = sum(animal.fitness for animal in self.animals)
        return total_fitness / len(self.animals)

    def calculate_average_predator_fitness(self):
        """
        Calculates the average fitness of the predator population in the region.

        :return: Average fitness as a float.
        """
        if not self.predators:
            return 0
        total_fitness = sum(predator.fitness for predator in self.predators)
        return total_fitness / len(self.predators)




   






