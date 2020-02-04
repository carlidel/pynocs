import pandas as pd
import numpy as np

from .engine_wrapper import engine_wrapper
from .engine_wrapper import ostream_redirect

class nocs_tools(object):
    """Simple wrapper for... the engine wrapper"""
    def __init__(self, grid_size, random_seed):
        """Initiate the wrapper wrapper
        
        Parameters
        ----------
        object : self
            self
        grid_size : unsigned int
            fineness of the grid
        random_seed : bool
            do you want a random engine? If False seed 42 will be set for the randomic parts of the simulation.
        """        
        self.engine = engine_wrapper(grid_size, random_seed)
        self.time = 0.0
        self.lines = []

    def add_basic_xline(self, position):
        """Add a basic barrier to the simulation (i.e. elastic collision)
        
        Parameters
        ----------
        position : float
            x coordinate of the barrier (must be [0, 1])
        """        
        self.engine.add_basic_xline(position)
        self.lines.append(position)

    def add_fixed_xline(self, position, temperature):
        """Add a fixed barrier to the simulation (i.e. collisions reset energy to a given temperature value)
        
        Parameters
        ----------
        position : float
            x coordinate of the barrier (must be [0, 1])
        temperature: float
            value at which energy of colliding molecules is resetted
        """        
        self.engine.add_fixed_xline(position, temperature)
        self.lines.append(position)

    def add_random_xline(self, position, temperature):
        """Add a random barrier to the simulation (i.e. collisions reset energy to a random value extracted by a random exponential distribution centered at the temperature value) [TO BE CHECKED!!! ASK BEFOR USING!!!]
        
        Parameters
        ----------
        position : float
            x coordinate of the barrier (must be [0, 1])
        temperature: float
            characteristic value of the distribution
        """
        self.engine.add_random_xline(position, temperature)
        self.lines.append(position)

    def add_multiplicative_xline(self, position, elasticity):
        """Add a multiplicative barrier to the simulation (i.e. collisions multiply energy of colliding molecule with an elasticity value)
        
        Parameters
        ----------
        position : float
            x coordinate of the barrier (must be [0, 1])
        elasticity: float
            multiplicative factor for colliding molecules
        """
        self.engine.add_multiplicative_xline(position, elasticity)
        self.lines.append(position)

    def add_sphere(self, x, y, radius, mass, vx, vy, tracking):
        """Add a rigid sphere to the simulation
        
        Parameters
        ----------
        x : float
            x position of cdm
        y : float
            y position of cdm
        radius : float
            radius of the sphere
        mass : float
            mass of the sphere
        vx : float
            x velocity of the sphere
        vy : foat
            y velocity of the sphere
        tracking : bool
            do you want this particle tracked in its events?
        
        Returns
        -------
        unsigned int
            id of the particle in the engine
        """        
        molecule_id = self.engine.add_molecule(
            float(x), float(y),
            [0.0], [0.0],
            [float(radius)], [float(mass)],
            float(vx), float(vy),
            0.0, 0.0,
            tracking
        )
        return molecule_id

    def run(self, time_interval):
        """run the simulation for a given interval of time
        
        Parameters
        ----------
        time_interval : float
            interval of time
        """        
        with ostream_redirect(stdout=True, stderr=True):
            self.engine.run(time_interval)
        self.time += time_interval

    def get_simulation_photo(self):
        """get complete picture of the simulation (molecules are not ordered!)
        
        Returns
        -------
        dataframe
            dataframe with all the informations about molecules
        """        
        data = self.engine.get_sim_photo()
        df = pd.DataFrame(data, columns=['time', 'mass', 'radius', 'energy', 'x', 'y', 'v_x', 'v_y'])
        return df

    def get_tracking_data(self):
        """get history log of all the tracked molecules
        
        Returns
        -------
        dataframe
            dataframe with all the informations about tracked molecules
        """        
        data = self.engine.get_tracking_data()
        df = pd.DataFrame(data, columns=['id', 'type', 'time', 'mass', 'energy', 'x', 'y', 'v_x', 'v_y'])
        return df

    def load_simulation_photo(self, df, tracking_lambda=lambda x:False):
        """Use a simulation photo to rebuild a new simulation!
        
        Parameters
        ----------
        df : dataframe
            a dataframe obtained with the method get_simulation_photo()
        tracking_lambda : lambda, optional
            since the tracking information is lost in this passage, you can rebuild it by passing a lambda function with the desired behaviour implemented, this lambda takes as argument a tuple containing the following data: tuple('index', 'mass', 'radius', 'energy', 'x', 'y', 'v_x', 'v_y'), by default lambda tuple : False
        """        
        for index, row in df.iterrows():
            self.add_sphere(row['x'], row['y'], row['radius'], row['mass'], row['v_x'], row['v_y'], tracking_lambda(
                (index, row['x'], row['y'], row['radius'], row['mass'], row['v_x'], row['v_y'])))

    def get_xline_positions(self):
        """Return the list of positions of xlines in a list
        
        Returns
        -------
        list
            list of x coordinates
        """        
        return self.lines                
