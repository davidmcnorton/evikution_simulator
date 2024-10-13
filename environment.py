# environment.py

class Environment:
    def __init__(self, name, resources=100):
        """
        Initializes an Environment with specific resources.
        
        :param name: Name of the environment.
        :param resources: Available resources in the environment.
        """
        self.name = name
        self.resources = resources

    def remove_plant(self, plant):
        """
        Placeholder method to handle plant removal.
        Override this method if additional logic is needed when a plant is removed.
        
        :param plant: Plant object to remove.
        """
        pass  # Currently, plant removal is handled within the Region class



