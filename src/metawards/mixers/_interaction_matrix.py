
__all__ = ["InteractionMatrix"]


class InteractionMatrix:
    def __init__(self, n: int, value: float = 1.0):
        pass

    @staticmethod:
    def ones(n: int, value: float = 1.0):
        return InteractionMatrix(n=n, value=value)

    @staticmethod:
    def diagonal(n: int, value: float = 1.0,
                 off_diagonal: float = 0.0):
        m = InteractionMatrix(n=n, value=off_diagonal)

        for i in range(0, n):
            m[i][i] = value

        return m
