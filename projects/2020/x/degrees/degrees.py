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
    def __init__(self, found, least_degree, path):
        self.found = found
        self.least_degree = least_degree
        self.path = path


node = Node(0, 100, None)

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


"""
def print_foundneighbours():
    print("Print Neighbours")
    print("*******")
    for item in found_neighbours:
        print(item)
    print("***End Print Neighbours****")
"""


def print_names():
    print("Name")
    print("*******")
    for item in names.items():
        print(item)
    print("**********************************************")


def print_neighbours(source):
    print("Neighbours for star: " + source)
    for item in neighbors_for_person(source, people, movies):
        print(item)
    print("**********************************************")


def print_all(source):
    print_people()
    print_movies()
    print_names()
    print_neighbours(source)


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
    target = person_id_for_name("Tom Hanks")
    # target = person_id_for_name(input("Name: "))
    if target is None:
        sys.exit("Person not found.")

    lock = multiprocessing.Lock()
    count = 0
    # Returns the shortest list of (movie_id, person_id) pairs
    shortest_path(source, source, target, node, parent_path, lock, found_neighbours, people, names, movies, count)
    # print_degrees(source, node, people, movies)


def print_degrees_dup(source, node, people, movies):
    if node is None:
        print("Not connected.")
    else:
        if node.path is not None:
            degrees = len(node.path)
            path = [(None, source)] + node.path
            for i in range(degrees):
                person1 = people[path[i][1]]["name"]
                person2 = people[path[i + 1][1]]["name"]
                movie = movies[path[i + 1][0]]["title"]
                print(f"{i + 1}: {person1} and {person2} starred in {movie}")


def print_degrees(source, node, people, movies):
    if node is None:
        print("Not connected.")
    else:
        if node.path is not None:
            degrees = len(node.path)
            print("\nAnswer Start *************")
            print(f"{degrees} degrees of separation.")
            path = [(None, source)] + node.path
            for i in range(degrees):
                person1 = people[path[i][1]]["name"]
                person2 = people[path[i + 1][1]]["name"]
                movie = movies[path[i + 1][0]]["title"]
                print(f"{i + 1}: {person1} and {person2} starred in {movie}")
            print("\nAnswer End *************")


def neighbors_for_person(person_id, people, movies):
    """x
    Returns (movie_id, person_id) pairs for people
    who starred with a given person.
    """
    # try:
    if person_id not in found_neighbours:
        # print("source id inside :" + person_id)
        movie_ids = people[person_id]["movies"]
        neighbors = set()
        for movie_id in movie_ids:
            for id in movies[movie_id]["stars"]:
                if id != person_id:
                    neighbors.add((movie_id, id))

        list_of_items = list(neighbors)

        return neighbors


def by_name(ele):
    return ele[1]


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


def shortest_path(source, int_source, target, node, parent_path, lock, found_neighbours, people, names, movies, count):
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

    if node.found == 1:
        print(" This is thread :" + str(count) + "is finishing")
        sys.exit(0)


    star = 0
    print(" This is thread :" + str(count) + "\n")
    if count > 0 and parent_path is None:
        return

    path = set()
    path = parent_path
    print("Parent path : " + str(parent_path))
    print("Path outside : " + str(path))
    print("Parent path outside : " + str(parent_path))
    # Add neighbors to frontier
    if int_source is not None:
        if str(int_source) in str(found_neighbours):
            # do nothing
            print("\n\n****************************************************")
            print(int_source + " is found in " + str(found_neighbours))
            print("Exit cause its found")
            print("****************************************************\n\n")
            sys.exit()
        else:
            print("Printing found neighbours array : " + str(int_source) + " is :" + str(found_neighbours))
            neighbourliness = sorted(neighbors_for_person(str(int_source), people, movies), key=by_name)
            print("Printing parsing star :" + str(int_source))
            print("Printing neighbourliness :" + str(neighbourliness))
            found_neighbours.append(int_source)
            print("Printing found neighbours array after adding: " + str(int_source) + " is :" + str(found_neighbours))
            Process_jobs = []
            for count, item in enumerate(neighbourliness, start=1):
                if str(item[1]) not in str(found_neighbours):
                    path.add((item[0], item[1]))
                    #parent_path.add((item[0], item[1]))
                    print("Source: " + source + " Target:" + target + " Parsing Star:" + int_source + " Next Star:" +
                          item[
                              1] + " Movie:" + item[0])
                    print("Path before call : " + str(path))
                    print("Parent path before call : " + str(parent_path)+"\n\n")
                    if item[1] is not None:
                        star = item[1]
                        if item[1] == target:
                            print("\n\n\n*******************************************")
                            # print("Item: " + item[1] + " Equal to Target :" + target)
                            # print("Source: " + source + " Target:" + target + " Parsing Star:" + int_source + " Add Star:" + item[1] + " Movie:" + item[0])
                            # path.remove()
                            # parent_path.remove()
                            # print("PATH")
                            # print(path)
                            # print("PARENT_PATH")
                            # print(parent_path)

                            degrees = len(path)
                            print("DEGREE")
                            print(degrees)
                            print("OLD DEGREE")
                            print(node.least_degree)
                            print("*************************************************\n\n")
                            if degrees is not None:
                                if node.least_degree is None:
                                    node.least_degree = degrees
                                    print("Degree change to new lower: " + str(degrees))
                                if int(node.least_degree) > degrees:
                                    lock.acquire()
                                    node.least_degree = degrees
                                    node.path = list(path)
                                    print_degrees(source, node, people, movies)
                                    lock.release()
                                    node.found = 1
                                    #path.pop()
                                    #parent_path.pop()
                                    #if len(path) == 0:
                                        #star = source
                                        #print("Star " + star)

                                    #print("Path after pop : " + str(path))
                                    #if len(path) == 0:
                                        #return
                                    sys.exit(0)
                    count = count + 1
                    parent_path = set()
                    parent_path = path
                    p = multiprocessing.Process(target=shortest_path,
                                                args=(
                                                    source, star, target, node, parent_path, lock, found_neighbours,
                                                    people, names, movies, count))
                    Process_jobs.append(p)
                    p.start()
                    p.join()
    # TODO
    sys.exit()


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("degrees new degrees is :" + node.least_degree)
        print("END")
        sys.exit(0)