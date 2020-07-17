
from metawards import Wards

import os

script_dir = os.path.dirname(__file__)

main_json = os.path.join(script_dir, "data", "main.json.bz2")
students_json = os.path.join(script_dir, "data", "students.json.bz2")
teachers_json = os.path.join(script_dir, "data", "teachers.json.bz2")


def test_harmonise():
    main = Wards.from_json(main_json)
    students = Wards.from_json(students_json)
    teachers = Wards.from_json(teachers_json)

    overall, subnets = Wards.harmonise([main, students, teachers])

    print(overall)
    print(subnets)

    total_pop = total_workers = total_players = 0

    assert len(subnets) == 3

    for subnet in subnets:
        total_pop += subnet.population()
        total_workers += subnet.num_workers()
        total_players += subnet.num_players()

    assert overall.population() == total_pop
    assert overall.num_workers() == total_workers
    assert overall.num_players() == total_players


if __name__ == "__main__":
    test_harmonise()
