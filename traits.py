# traits.py

import numpy as np  # Ensure NumPy is imported

class Trait:
    def __init__(self, name, gene_length=2, dominance="dominant"):
        """
        Initializes a Trait with specific parameters.

        :param name: Name of the trait.
        :param gene_length: Number of genes defining the trait.
        :param dominance: Dominance type ("dominant", "recessive", "co-dominant").
        """
        self.name = name
        self.gene_length = gene_length
        self.dominance = dominance
        self.genes = self.random_genes()

    def random_genes(self):
        """
        Generates random genes for the trait.

        :return: Numpy array of genes.
        """
        return np.random.randint(0, 2, size=self.gene_length)

    def express(self, genes):
        """
        Determines the expression of the trait based on the genes.

        :param genes: Numpy array representing the genes.
        :return: Expressed trait value.
        """
        if self.dominance == "dominant":
            return 1 if np.any(genes == 1) else 0
        elif self.dominance == "recessive":
            return 1 if np.all(genes == 1) else 0
        elif self.dominance == "co-dominant":
            return sum(genes) / len(genes)
        else:
            raise ValueError("Invalid dominance type.")
