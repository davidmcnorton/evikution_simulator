# lifeform.py

import numpy as np
import uuid
from traits import Trait

class Lifeform:
    def __init__(self, traits, environment, mutation_rate=0.05):
        """
        Initializes a Lifeform with specific traits and environmental context.

        :param traits: List of Trait objects.
        :param environment: Environment object where the lifeform resides.
        :param mutation_rate: Probability of gene mutation during reproduction.
        """
        self.id = uuid.uuid4()  # Unique identifier for each lifeform
        self.traits = traits  # List of Trait instances
        self.environment = environment  # Reference to the Environment object
        self.genome = self.random_genome()  # Numpy array representing the genome
        self.fitness = self.evaluate_fitness()  # Initial fitness evaluation
        self.x = np.random.uniform(0, 100)  # Random initial x-position
        self.y = np.random.uniform(0, 100)  # Random initial y-position
        self.mutation_rate = mutation_rate  # Mutation rate inherited from Region
        self.territory_center = (self.x, self.y)  # Initial territory center

    def random_genome(self):
        """
        Generates a random genome based on the traits.

        :return: Numpy array representing the genome.
        """
        genome = []
        for trait in self.traits:
            genes = np.random.randint(0, 2, size=trait.gene_length)
            genome.extend(genes)
        return np.array(genome)

    def evaluate_fitness(self):
        """
        Evaluates the fitness of the lifeform based on its traits and environment.

        :return: Fitness score as a float.
        """
        fitness = 0
        offset = 0
        for trait in self.traits:
            genes = self.genome[offset:offset + trait.gene_length]
            expressed = trait.express(genes)
            fitness += expressed
            offset += trait.gene_length
        # Example: Fitness is scaled by environmental resources
        fitness *= (self.environment.resources / 100)
        return fitness

    def mutate_traits(self):
        """
        Applies mutations to the lifeform's traits based on the mutation rate.

        :return: List of Trait objects with potential mutations.
        """
        mutated_traits = []
        for trait in self.traits:
            # Create a copy of the trait's genes to avoid mutating the original trait
            mutated_genes = trait.genes.copy()
            # Apply mutation based on mutation_rate
            for i in range(len(mutated_genes)):
                if np.random.rand() < self.mutation_rate:
                    mutated_genes[i] = 1 - mutated_genes[i]  # Flip gene
            # Create a new Trait instance with mutated genes
            mutated_trait = Trait(
                name=trait.name,
                gene_length=trait.gene_length,
                dominance=trait.dominance
            )
            mutated_trait.genes = mutated_genes
            mutated_traits.append(mutated_trait)
        return mutated_traits

    def get_traits_summary(self):
        """
        Returns a summary of the lifeform's traits.

        :return: String summarizing the traits.
        """
        summary = []
        offset = 0  # Initialize offset to 0
        for trait in self.traits:
            genes = self.genome[offset:offset + trait.gene_length]
            expressed_value = trait.express(genes)
            summary.append(f"{trait.name}: {expressed_value}")
            offset += trait.gene_length
        return ", ".join(summary)









