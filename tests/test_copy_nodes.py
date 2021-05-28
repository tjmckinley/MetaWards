
from metawards import Nodes


def test_copy_nodes():
    n1 = Nodes(N=100)

    assert len(n1.label) == 100

    n2 = n1.copy()

    v1 = n1.get_custom("test")

    assert len(v1) == 100

    for i in range(0, 100):
        v1[i] = i + 0.5

    print(v1)

    v2 = n2.get_custom("test")

    assert len(v2) == 100

    for i in range(0, 100):
        assert v2[i] == 0.0
        v2[i] = i * 2.5

    for i in range(0, 100):
        assert v1[i] == i + 0.5

    print(v2)
    print(v1)


if __name__ == "__main__":
    test_copy_nodes()
