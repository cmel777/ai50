import csv
import multiprocessing
import sys

names = {}

# Maps person_ids to a dictionary of: name, birth, movies (a set of movie_ids)
people = {}

# Maps movie_ids to a dictionary of: title, year, stars (a set of person_ids)
movies = {}

count_explored = 0


class ParentPath:
    def __init__(self, parent_path):
        self.parent_path = parent_path


class Node:
    def __init__(self, state, least_degree, path):
        self.state = state
        self.least_degree = least_degree
        self.path = path


node = Node(None, None, None)
parent_path = ParentPath([])

least_path = 0


def print_data():
    print("People")
    print("*******")
    for item in people.items():
        print(item)
    print("Movies")
    print("*******")
    for item in movies.items():
        print(item)
    print("Name")
    print("*******")
    for item in names.items():
        print(item)
    print("**********************************************")
    print("Neighbours")
    for item in neighbors_for_person("129"):
        print(item)
    print("**********************************************")
    print("**********************************************")
    print("**********************************************")


def load_data(directory):
    """
    Load data from CSV files into memory.
    """
    # Load people
    with open(f"{directory}/people.csv", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            people[row["id"]] = {
                "name": row["name"],
                "birth": row["birth"],
                "movies": set()
            }
            if row["name"].lower() not in names:
                names[row["name"].lower()] = {row["id"]}
            else:
                names[row["name"].lower()].add(row["id"])

    # Load movies
    with open(f"{directory}/movies.csv", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            movies[row["id"]] = {
                "title": row["title"],
                "year": row["year"],
                "stars": set()
            }

    # Load stars
    with open(f"{directory}/stars.csv", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            try:
                people[row["person_id"]]["movies"].add(row["movie_id"])
                movies[row["movie_id"]]["stars"].add(row["person_id"])
            except KeyError:
                pass


def main():
    if len(sys.argv) > 2:
        sys.exit("Usage: python degrees.py [directory]")
    directory = sys.argv[1] if len(sys.argv) == 2 else "large"

    # Load data from files into memory
    print("Loading data...")
    load_data(directory)
    print("Data loaded.")
    print_data()

    # source = person_id_for_name(input("Name: "))
    source = person_id_for_name("Tom Cruise")
    if source is None:
        sys.exit("Person not found.")
    target = person_id_for_name("Kevin Bacon")
    # target = person_id_for_name(input("Name: "))
    if target is None:
        sys.exit("Person not found.")

    found_neighbours = []
    lock = multiprocessing.Lock()
    # Returns the shortest list of (movie_id, person_id) pairs
    shortest_path(source, target, node, parent_path, found_neighbours, lock)

    if node is None:
        print("Not connected.")
    else:
        degrees = len(node.path)
        print(f"{degrees} degrees of separation.")
        path = [(None, source)] + node.path
        for i in range(degrees):
            person1 = people[path[i][1]]["name"]
            person2 = people[path[i + 1][1]]["name"]
            movie = movies[path[i + 1][0]]["title"]
            print(f"{i + 1}: {person1} and {person2} starred in {movie}")


def shortest_path(source, target, node, parent_path, found_neighbours, lock):
    """
    Returns the shortest list of (movie_id, person_id) pairs
    that connect the source to the target.
    If no possible path, returns None.
    """

    # If nothing left in frontier, then no path

    # Keep looping until solution found
    # If nothing left in frontier, then no path
    # if frontier.empty():
    # raise Exception("no solution")

    # Add neighbors to frontier
    if source not in found_neighbours:
        path = []
        if parent_path.parent_path is not None:
            path = parent_path.parent_path
        found_neighbours.append(source)
        Process_jobs = []
        for count, item in enumerate(neighbors_for_person(source), start=1):
            parent_path.parent_path = (item[0], item[1])
            p = multiprocessing.Process(target=shortest_path,
                                        args=(item[1], target, node, found_neighbours, parent_path, lock))
            Process_jobs.append(p)
            p.start()
            p.join()
            if (len(neighbors_for_person(source)) - count) == 0:
                print("Last neighbour is : " + item[1] + "for star :" + source)
                return
            if item[1] == target:
                path.append((item[0], item[1]))
                degrees = len(path)
                if int(node.least_degree) > degrees:
                    lock.acquire()
                    node.least_degree = degrees
                    node.path = path
                    lock.release()
                    return

    # TODO
    raise NotImplementedError


def neighbors_for_person(person_id):
    """x
    Returns (movie_id, person_id) pairs for people
    who starred with a given person.
    """
    movie_ids = people[person_id]["movies"]
    neighbors = set()
    for movie_id in movie_ids:
        for id in movies[movie_id]["stars"]:
            if id != person_id:
                neighbors.add((movie_id, id))
    return neighbors


def compute(source, target, node, found_neighbours, parent_path, lock):
    # Add neighbors to frontier
    if source not in found_neighbours:
        path = []
        if parent_path.parent_path is not None:
            path = parent_path.parent_path
        found_neighbours.append(source)
        Process_jobs = []
        for count, item in enumerate(neighbors_for_person(source), start=1):
            parent_path.parent_path = (item[0], item[1])
            p = multiprocessing.Process(target=compute,
                                        args=(item[1], target, node, found_neighbours, parent_path, lock))
            Process_jobs.append(p)
            p.start()
            p.join()
            if (len(neighbors_for_person(source)) - count) == 0:
                print("Last neighbour is : " + item[1] + "for star :" + source)
                return
            if item[1] == target:
                path.append((item[0], item[1]))
                degrees = len(path)
                if int(node.least_degree) > degrees:
                    lock.acquire()
                    node.least_degree = degrees
                    node.path = path
                    lock.release()
                    return

            """
                p = multiprocessing.Process(target=compute, args=(item[1], target, node,))
    Process_jobs.append(p)
    p.start()
    p.join()

            if node.least_degree is not None:
                if node.least_degree > len(path):
                    node = Node(len(path), path)
                    return node

        # node = {len(path), path}
        # return path
        # else:
        # start = Node(None, neighbour[1], None)
        # compute()

        # for neighbour2 in neighbors_for_person(node.parent):


    Process_jobs = []
    for i in range(3):
    p = multiprocessing.Process(target=spawn_process, args=(movie_id, count_explored))
Process_jobs.append(p)
p.start()
p.join()
def spawn_process(movie_id, count_explored):
print('This is process: %s' % movie_id)
# f()
for person_id in movies[movie_id]["stars"]:
"""


def person_id_for_name(name):
    """
    Returns the IMDB id for a person's name,
    resolving ambiguities as needed.
    """
    person_ids = list(names.get(name.lower(), set()))
    if len(person_ids) == 0:
        return None
    elif len(person_ids) > 1:
        print(f"Which '{name}'?")
        for person_id in person_ids:
            person = people[person_id]
            name = person["name"]
            birth = person["birth"]
            print(f"ID: {person_id}, Name: {name}, Birth: {birth}")
        try:
            person_id = input("Intended Person ID: ")
            if person_id in person_ids:
                return person_id
        except ValueError:
            pass
        return None
    else:
        return person_ids[0]


"""
def neighbors_for_person(person_id):

    movie_ids = people[person_id]["movies"]
    neighbors = {}
    for movie_id in movie_ids:
        for p_id in movies[movie_id]["stars"]:
            if p_id != person_id:
                neighbors[[movie_id]] = {[p_id]}
    return neighbors
 for row in reader:
            people[row["id"]] = {
                "name": row["name"],
                "birth": row["birth"],
                "movies": set()
            }
            if row["name"].lower() not in names:
                names[row["name"].lower()] = {row["id"]}
            else:
                names[row["name"].lower()].add(row["id"])
"""
if __name__ == "__main__":
    main()
