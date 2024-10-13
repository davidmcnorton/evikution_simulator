# animal.py

import numpy as np
from lifeform import Lifeform
from traits import Trait
from plant import Plant
import random

class Animal(Lifeform):
    def __init__(self, traits, environment, mutation_rate=0.05):
        """
        Initializes an Animal lifeform.

        :param traits: List of Trait objects.
        :param environment: Environment object where the animal resides.
        :param mutation_rate: Probability of gene mutation during reproduction.
        """
        super().__init__(traits=traits, environment=environment, mutation_rate=mutation_rate)
        self.energy = self.calculate_initial_energy()
        self.alive = True
        self.territory = self.establish_territory()

    def calculate_initial_energy(self):
        """
        Calculates the initial energy of the animal based on traits.

        :return: Initial energy as a float.
        """
        # Example: Energy based on traits like speed, size, and territoriality
        energy = 50  # Base energy
        offset = 0
        for trait in self.traits:
            genes = self.genome[offset:offset + trait.gene_length]
            expressed = trait.express(genes)
            if trait.name == "Speed":
                energy += expressed * 2  # Speed contributes to energy
            elif trait.name == "Size":
                energy += expressed * 3  # Size contributes more
            elif trait.name == "Territoriality":
                energy += expressed * 5  # Territoriality contributes significantly
            offset += trait.gene_length
        return energy

    def establish_territory(self):
        """
        Establishes a territory for the animal based on its Territoriality trait.

        :return: Territory radius as a float.
        """
        territoriality = self.get_trait_value("Territoriality")
        territory_radius = 10 + (territoriality * 5)  # Base radius + bonus
        return territory_radius

    def move(self):
        """
        Updates the animal's position based on its speed trait and territorial behavior.
        """
        # Movement is influenced by the Speed trait
        speed = self.get_trait_value("Speed")
        movement_range = speed * 2  # Movement range scales with speed
        # Move within territory
        angle = random.uniform(0, 2 * np.pi)
        dx = movement_range * np.cos(angle)
        dy = movement_range * np.sin(angle)
        new_x = self.x + dx
        new_y = self.y + dy
        # Ensure the animal stays within its territory
        distance_from_territory_center = np.hypot(new_x - self.territory_center[0], new_y - self.territory_center[1])
        if distance_from_territory_center <= self.territory:
            self.x = np.clip(new_x, 0, 100)
            self.y = np.clip(new_y, 0, 100)
        else:
            # Stay within territory
            self.x = np.clip(self.territory_center[0] + (self.territory * np.cos(angle)), 0, 100)
            self.y = np.clip(self.territory_center[1] + (self.territory * np.sin(angle)), 0, 100)
        # Energy expenditure for movement
        self.energy -= speed * 0.5  # Adjust energy cost as needed
        if self.energy <= 0:
            self.alive = False

    def get_trait_value(self, trait_name):
        """
        Retrieves the expressed value of a specific trait.

        :param trait_name: Name of the trait.
        :return: Expressed value of the trait.
        """
        offset = 0
        for trait in self.traits:
            genes = self.genome[offset:offset + trait.gene_length]
            expressed = trait.express(genes)
            if trait.name == trait_name:
                return expressed
            offset += trait.gene_length
        return 0  # Default if trait not found

    def consume_plant(self, plant):
        """
        Consumes a plant to gain energy.

        :param plant: Plant object to consume.
        """
        if isinstance(plant, Plant):
            self.energy += plant.resource_value
            # Optionally, remove or reduce plant's resource value
            plant.resource_value -= 10  # Example: Consuming reduces plant's resources
            if plant.resource_value <= 0:
                self.environment.remove_plant(plant)

    def reproduce(self):
        """
        Determines whether the animal reproduces based on its energy.

        :return: New Animal object if reproduction occurs, else None.
        """
        reproduction_threshold = 100  # Example threshold
        if self.energy >= reproduction_threshold:
            self.energy /= 2  # Split energy with offspring
            # Create offspring with potential mutations
            offspring_traits = self.mutate_traits()
            return Animal(traits=offspring_traits, environment=self.environment, mutation_rate=self.mutation_rate)
        return None








