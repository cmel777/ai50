import csv
import multiprocessing
import sys, threading

sys.setrecursionlimit(10 ** 7)  # max depth of recursion
threading.stack_size(2 ** 27)  # new thread will get stack of such size

names = {}

# Maps person_ids to a dictionary of: name, birth, movies (a set of movie_ids)
people = {}

# Maps movie_ids to a dictionary of: title, year, stars (a set of person_ids)
movies = {}

count_explored = 0

found_neighbours = []

parent_path = set()


class Node:
    def __init__(self, state, least_degree, path):
        self.state = state
        self.least_degree = least_degree
        self.path = path


node = Node(None, None, None)

least_path = 0


def print_people():
    print("People")
    print("*******")
    for item in people.items():
        print(item)


def print_movies():
    print("Movies")
    print("*******")
    for item in movies.items():
        print(item)


def print_foundneighbours(found):
    print("Found Neighbours")
    print("*******")
    for item in found_neighbours:
        print(item)


def print_names():
    print("Name")
    print("*******")
    for item in names.items():
        print(item)
    print("**********************************************")


def print_neighbours(source):
    print("Neighbours for star: " + source)
    for item in neighbors_for_person(source):
        print(item)
    print("**********************************************")


def print_all(source):
    print_people()
    print_movies()
    print_names()
    # print_neighbours(source)


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
    print("Printing data...")

    # source = person_id_for_name(input("Name: "))
    source = person_id_for_name("Tom Cruise")
    print_all(source)
    if source is None:
        sys.exit("Person not found.")
    target = person_id_for_name("Kevin Bacon")
    # target = person_id_for_name(input("Name: "))
    if target is None:
        sys.exit("Person not found.")

    lock = multiprocessing.Lock()
    # Returns the shortest list of (movie_id, person_id) pairs
    shortest_path(source, target, node, parent_path, lock, found_neighbours, people, names, movies)

    if node is None:
        print("Not connected.")
    else:
        if node.path is not None:
            degrees = len(node.path)
            print(f"{degrees} degrees of separation.")
            path = [(None, source)] + node.path
            for i in range(degrees):
                person1 = people[path[i][1]]["name"]
                person2 = people[path[i + 1][1]]["name"]
                movie = movies[path[i + 1][0]]["title"]
                print(f"{i + 1}: {person1} and {person2} starred in {movie}")


def found_in_neighbours(source):
    if str(source) in found_neighbours:
        return False
    else:
        return True


def shortest_path(source, target, node, parent_path, lock, found_neighbours, people, names, movies):
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
    if source is not None:
        if str(source) in found_neighbours:
            print_foundneighbours(found_neighbours)
            return
        else:
            neighbourliness = neighbors_for_person(str(source), people, movies)
            found_neighbours.append(source)
            if parent_path is not None:
                path = set()
                path = parent_path

            Process_jobs = []
            for count, item in enumerate(neighbourliness, start=1):
                path.add((item[0], item[1]))
                parent_path.add((item[0], item[1]))
                print("Source:" + source + " Star:" + item[1] + " Movie:" + item[0])
                if item[1] is not None:
                    p = multiprocessing.Process(target=shortest_path,
                                                args=(item[1], target, node, parent_path, lock, found_neighbours,
                                                      people, names, movies))
                    Process_jobs.append(p)
                    p.start()
                    p.join()
                    if item[1] == target:
                        path.add((item[0], item[1]))
                        degrees = len(path)
                        if node.least_degree is not None:
                            if int(node.least_degree) > degrees:
                                lock.acquire()
                                node.least_degree = degrees
                                node.path = path
                                lock.release()
                                return

    # TODO
    sys.exit()


def neighbors_for_person(person_id, people, movies):
    """x
    Returns (movie_id, person_id) pairs for people
    who starred with a given person.
    """
    # try:
    if person_id not in found_neighbours:
        print("source id inside :" + person_id)
        movie_ids = people[person_id]["movies"]
        neighbors = set()
        for movie_id in movie_ids:
            for id in movies[movie_id]["stars"]:
                if id != person_id:
                    neighbors.add((movie_id, id))
        return neighbors
    # except KeyError as err:
    # print("Person :" + person_id)
    # print("Person :" + print_neighbours(str(person_id)))


"""
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
