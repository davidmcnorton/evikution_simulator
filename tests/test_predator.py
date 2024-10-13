# tests/test_predator.py

import unittest
import numpy as np
from predator import Predator
from traits import Trait
from environment import Environment
from animal import Animal


class TestPredator(unittest.TestCase):
    def setUp(self):
        self.environment = Environment(name="TestRegion", resources=100)
        self.traits = [
            Trait(name="Speed", gene_length=2, dominance="dominant"),
            Trait(name="Size", gene_length=2, dominance="recessive"),
            Trait(name="Camouflage", gene_length=2, dominance="co-dominant")
        ]
        self.predator = Predator(traits=self.traits, environment=self.environment)

    def test_genome_initialization(self):
        self.assertIsNotNone(self.predator.genome)
        self.assertEqual(len(self.predator.genome), sum(trait.gene_length for trait in self.predator.traits))
        self.assertTrue(np.all(np.isin(self.predator.genome, [0, 1])))

    def test_initial_energy(self):
        expected_energy = 60  # Base energy
        # Calculate based on traits
        offset = 0
        for trait in self.traits:
            genes = self.predator.genome[offset:offset + trait.gene_length]
            expressed = trait.express(genes)
            if trait.name == "Speed":
                expected_energy += expressed * 3
            elif trait.name == "Size":
                expected_energy += expressed * 4
            offset += trait.gene_length
        self.assertAlmostEqual(self.predator.energy, expected_energy)

    def test_move_method(self):
        old_x, old_y = self.predator.x, self.predator.y
        self.predator.move()
        # Predator should have moved based on speed
        speed = self.predator.get_trait_value("Speed")
        movement_range = speed * 3
        self.assertNotEqual(self.predator.x, old_x)
        self.assertNotEqual(self.predator.y, old_y)
        self.assertTrue(0 <= self.predator.x <= 100)
        self.assertTrue(0 <= self.predator.y <= 100)
        # Energy should have decreased
        expected_energy = self.predator.calculate_initial_energy() - speed * 0.7
        self.assertAlmostEqual(self.predator.energy, expected_energy)

    def test_hunt_successful(self):
        # Create an animal within hunting range
        animal = Animal(traits=self.traits, environment=self.environment)
        animal.x = self.predator.x + 3  # Within hunting radius of 5
        animal.y = self.predator.y + 3
        animal_speed = animal.get_trait_value("Speed")
        animal_size = animal.get_trait_value("Size")
        # Ensure predator is faster and larger
        self.predator.traits[0].express = lambda genes: 2  # Speed
        self.predator.traits[1].express = lambda genes: 2  # Size
        animal.traits[0].express = lambda genes: 1  # Speed
        animal.traits[1].express = lambda genes: 1  # Size
        success = self.predator.attempt_hunt(animal)
        self.assertTrue(success)

    def test_hunt_unsuccessful(self):
        # Create an animal outside hunting range
        animal = Animal(traits=self.traits, environment=self.environment)
        animal.x = self.predator.x + 10  # Outside hunting radius of 5
        animal.y = self.predator.y + 10
        success = self.predator.attempt_hunt(animal)
        self.assertFalse(success)

    def test_consume_animal(self):
        animal = Animal(traits=self.traits, environment=self.environment)
        animal.fitness = 50
        self.predator.consume_animal(animal)
        self.assertEqual(self.predator.energy, 60 + 50)  # Base energy + animal fitness
        self.assertFalse(animal.alive)

    def test_reproduce(self):
        # Set predator's energy above reproduction threshold
        self.predator.energy = 200
        offspring = self.predator.reproduce()
        self.assertIsNotNone(offspring)
        self.assertIsInstance(offspring, Predator)
        self.assertEqual(self.predator.energy, 100)  # Energy split

    def test_no_reproduce_due_to_low_energy(self):
        # Set predator's energy below reproduction threshold
        self.predator.energy = 100
        offspring = self.predator.reproduce()
        self.assertIsNone(offspring)

    def test_mutate_genome(self):
        original_genome = self.predator.genome.copy()
        mutated_genome = self.predator.mutate_genome(original_genome)
        # With a mutation rate of 0.05, expect some genes to have flipped
        num_mutations = np.sum(original_genome != mutated_genome)
        self.assertTrue(0 <= num_mutations <= len(original_genome))


if __name__ == '__main__':
    unittest.main()
