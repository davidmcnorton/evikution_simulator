# predator.py

import numpy as np
from lifeform import Lifeform
from traits import Trait
from animal import Animal  # Import Animal to resolve NameError
import random

class Predator(Lifeform):
    def __init__(self, traits, environment, mutation_rate=0.05):
        """
        Initializes a Predator lifeform.

        :param traits: List of Trait objects.
        :param environment: Environment object where the predator resides.
        :param mutation_rate: Probability of gene mutation during reproduction.
        """
        super().__init__(traits=traits, environment=environment, mutation_rate=mutation_rate)
        self.energy = self.calculate_initial_energy()
        self.alive = True
        self.territory = self.establish_territory()

    def calculate_initial_energy(self):
        """
        Calculates the initial energy of the predator based on traits.

        :return: Initial energy as a float.
        """
        # Example: Energy based on traits like hunting skill, speed, size, aggressiveness
        energy = 60  # Base energy
        offset = 0
        for trait in self.traits:
            genes = self.genome[offset:offset + trait.gene_length]
            expressed = trait.express(genes)
            if trait.name == "HuntingSkill":
                energy += expressed * 5  # HuntingSkill contributes to energy
            elif trait.name == "Speed":
                energy += expressed * 3  # Speed contributes to energy
            elif trait.name == "Size":
                energy += expressed * 4  # Size contributes more
            elif trait.name == "Aggressiveness":
                energy += expressed * 2  # Aggressiveness contributes to energy
            offset += trait.gene_length
        return energy

    def establish_territory(self):
        """
        Establishes a territory for the predator based on its Territoriality trait.

        :return: Territory radius as a float.
        """
        territoriality = self.get_trait_value("Territoriality")
        territory_radius = 15 + (territoriality * 5)  # Base radius + bonus
        return territory_radius

    def move(self):
        """
        Updates the predator's position based on its speed, stealth traits, and territorial behavior.
        """
        # Movement is influenced by the Speed and Stealth traits
        speed = self.get_trait_value("Speed")
        stealth = self.get_trait_value("Stealth")
        movement_range = speed * 3  # Predators can move faster
        # Move within territory, influenced by stealth
        angle = random.uniform(0, 2 * np.pi)
        dx = movement_range * np.cos(angle) * stealth
        dy = movement_range * np.sin(angle) * stealth
        new_x = self.x + dx
        new_y = self.y + dy
        # Ensure the predator stays within its territory
        distance_from_territory_center = np.hypot(new_x - self.territory_center[0], new_y - self.territory_center[1])
        if distance_from_territory_center <= self.territory:
            self.x = np.clip(new_x, 0, 100)
            self.y = np.clip(new_y, 0, 100)
        else:
            # Stay within territory
            self.x = np.clip(self.territory_center[0] + (self.territory * np.cos(angle)), 0, 100)
            self.y = np.clip(self.territory_center[1] + (self.territory * np.sin(angle)), 0, 100)
        # Energy expenditure for movement
        self.energy -= speed * 0.7  # Adjust energy cost as needed
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

    def consume_animal(self, animal):
        """
        Consumes an animal to gain energy, influenced by aggressiveness and stealth.

        :param animal: Animal object to consume.
        """
        if isinstance(animal, Animal):
            aggressiveness = self.get_trait_value("Aggressiveness")
            stealth = self.get_trait_value("Stealth")
            success_chance = 0.5 + (aggressiveness * 0.1)  # Base 50% chance
            success_chance *= stealth  # Higher stealth increases success
            if random.random() < success_chance:
                self.energy += animal.fitness
                animal.alive = False

    def reproduce(self):
        """
        Determines whether the predator reproduces based on its energy.

        :return: New Predator object if reproduction occurs, else None.
        """
        reproduction_threshold = 150  # Example threshold
        if self.energy >= reproduction_threshold:
            self.energy /= 2  # Split energy with offspring
            # Create offspring with potential mutations
            offspring_traits = self.mutate_traits()
            return Predator(traits=offspring_traits, environment=self.environment, mutation_rate=self.mutation_rate)
        return None








