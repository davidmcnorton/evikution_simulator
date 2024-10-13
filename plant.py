# plant.py

import numpy as np
from lifeform import Lifeform
from traits import Trait

class Plant(Lifeform):
    def __init__(self, traits, environment, mutation_rate=0.05):
        """
        Initializes a Plant lifeform.

        :param traits: List of Trait objects.
        :param environment: Environment object where the plant resides.
        :param mutation_rate: Probability of gene mutation during reproduction.
        """
        super().__init__(traits=traits, environment=environment, mutation_rate=mutation_rate)
        self.resource_value = self.calculate_resource_value()

    def calculate_resource_value(self):
        """
        Calculates the resource value provided by the plant based on traits.

        :return: Resource value as a float.
        """
        # Example: Resource value based on traits like size and camouflage
        resource = 10  # Base resource value
        offset = 0
        for trait in self.traits:
            genes = self.genome[offset:offset + trait.gene_length]
            expressed = trait.express(genes)
            if trait.name == "Size":
                resource += expressed * 5  # Size contributes to resource
            elif trait.name == "Camouflage":
                resource += expressed * 2  # Camouflage affects visibility
            offset += trait.gene_length
        return resource

    def regenerate(self):
        """
        Regenerates the plant's resources based on environmental factors.
        """
        # Example: Plants can regenerate resources if environmental resources are sufficient
        regeneration_rate = 0.1  # 10% regeneration per generation
        self.resource_value += self.environment.resources * regeneration_rate
        self.resource_value = min(self.resource_value, 100)  # Cap at 100

    def reproduce(self):
        """
        Plants reproduce by cloning themselves with potential mutations.

        :return: New Plant object if reproduction occurs, else None.
        """
        reproduction_threshold = 80  # Example threshold
        if self.resource_value >= reproduction_threshold:
            self.resource_value /= 2  # Split resources with offspring
            # Create offspring with potential mutations
            offspring_traits = self.mutate_traits()
            return Plant(traits=offspring_traits, environment=self.environment, mutation_rate=self.mutation_rate)
        return None


