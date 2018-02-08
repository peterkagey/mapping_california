""" Utilities for graph coloring regions in a map """

from collections import OrderedDict
import random

def generate_intersections(reader, verbose=False):
    """
    Given cartopy shapereader with a set of multipolygons,
    generate a dictionary where the keys are city names,
    and the values are the names of cities which border the key
    city.

    Parameters
    ----------

    reader: cartopy shapefile reader
        This is the shapefile reader that is expected
        to have a series of OSM multipolygons corresponding
        to different cities.
    verbose: boolean, optional
        Whether to output logging info.

    Returns
    -------
    
    OrderedDict
        The keys are city names, and the values are a list
        of names of cities that intersect it.
        The dictionary will be ordered from most neighbors
        to least neighbors. The intersection calculation
        may not be perfect, as GIS data may not line up
        exactly. However, it should be good enough for
        many purposes.
    """
    intersections = dict()
    for city1 in reader.records():
        name1 = city1.attributes['name']
        if name1 == '' or name1 in intersections:
            continue
        intersections[name1] = []
        for city2 in reader.records():
            name2 = city2.attributes['name']
            if name2 == '' or name1 == name2 or name2 in intersections[name1]:
                continue
            if city1.geometry.intersects(city2.geometry):
                if verbose:
                    print(f'{name1} intersects {name2}')
                intersections[name1].append(name2)
    # Once we have the intersections dictionary, sort them from most to least neighbors
    return OrderedDict((name, intersections[name]) for name in \
                        sorted(intersections, key=lambda k: len(intersections[k]), reverse=True))

def greedy_coloring(neighbors_map, colors):
    """
    Given an ordered dictionary of cities and their neighbors,
    as returned by generate_intersections, as well as a list of
    colors that matplotlib understands, return a dictionary
    of colors assigned to each city.

    This does *not* attempt to solve the four-color problem.
    If it fails to find a mapping, it throws an error.
    You can try again with the same number of colors, or increase
    the number of colors.

    Parameters
    ----------

    neighbors_map: OrderedDict
        A dictionary of city intersections, as computed by
        generate_intersections.

    colors: list
        A list of colors that matplotlib can use.

    Returns
    -------

    dict
        A dictionary with city names as keys, and an assigned
        color for each city.
    """
    colormap = dict()
    # For this each city, try to find a color
    for city, neighbors in neighbors_map.items():
        # loop over the colors
        random.shuffle(colors)
        for color in colors:
            # Check if that color has not been used by one of the neighbors
            for neighbor in neighbors:
                if neighbor in colormap and colormap[neighbor] == color:
                    break
            else:
                colormap[city] = color
                break
        if city not in colormap:
            raise Exception(f'Could not find color for {city}')
    return colormap
