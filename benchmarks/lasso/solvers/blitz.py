from benchopt.base import BaseSolver
from benchopt.util import safe_import


with safe_import() as solver_import:
    import blitzl1


class Solver(BaseSolver):
    name = 'Blitz'
    sampling_strategy = 'tolerance'

    install_cmd = 'pip'
    package_name = 'blitzl1'
    package_install = (
        'git+https://github.com/tommoral/blitzl1.git@FIX_python_type_check'
    )

    def set_objective(self, X, y, lmbd):
        self.X, self.y, self.lmbd = X, y, lmbd

        blitzl1.set_use_intercept(False)
        self.problem = blitzl1.LassoProblem(self.X, self.y)

    def run(self, tolerance):
        blitzl1.set_tolerance(tolerance)
        self.coef_ = self.problem.solve(self.lmbd).x

    def get_result(self):
        return self.coef_.flatten()
