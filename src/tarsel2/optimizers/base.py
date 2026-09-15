class BaseMatrixOptimizer:
    """Interface shared by every coverage-matrix optimizer."""

    name = "base"

    def apply(self, df):
        raise NotImplementedError
