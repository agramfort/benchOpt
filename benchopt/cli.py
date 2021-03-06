import click

from benchopt import run_benchmark


from benchopt.util import filter_solvers
from benchopt.util import _run_bash_in_env, create_venv
from benchopt.util import check_benchmarks, get_all_benchmarks
from benchopt.util import list_benchmark_solvers, install_solvers


from benchopt.config import get_benchmark_setting


CONTEXT_SETTINGS = dict(help_option_names=['-h', '--help'])


@click.group(context_settings=CONTEXT_SETTINGS)
def main():
    """Command-line interface to benchOpt"""
    pass


@main.command()
@click.argument('benchmarks', nargs=-1)
@click.option('--repetition', '-n', default=1, type=int)
@click.option('--solver', '-s', 'solver_names', multiple=True, type=str)
@click.option('--force-solver', '-f', 'forced_solvers',
              multiple=True, type=str)
@click.option('--max-samples', default=1000, show_default=True, type=int,
              help='Maximal number of iteration for each solver')
def run(benchmarks, solver_names, forced_solvers, max_samples, repetition):
    """Run benchmark."""

    all_benchmarks = get_all_benchmarks()
    if benchmarks == 'all':
        benchmarks = all_benchmarks

    check_benchmarks(benchmarks, all_benchmarks)

    for benchmark in benchmarks:
        run_benchmark(benchmark, solver_names, forced_solvers,
                      max_samples=max_samples, n_rep=repetition)


@main.command()
@click.argument('benchmarks', nargs=-1)
@click.option('--recreate', '-r', is_flag=True)
@click.option('--repetition', '-n', default=1, type=int)
@click.option('--solver', '-s', 'solver_names', multiple=True, type=str)
@click.option('--force-solver', '-f', 'forced_solvers',
              multiple=True, type=str)
@click.option('--max-samples', default=1000, show_default=True, type=int,
              help='Maximal number of iteration for each solver')
def bench(benchmarks, solver_names, forced_solvers, max_samples, recreate,
          repetition):
    """Run benchmark."""

    all_benchmarks = get_all_benchmarks()
    if benchmarks == ():
        benchmarks = all_benchmarks

    check_benchmarks(benchmarks, all_benchmarks)

    return_code = {}
    for benchmark in benchmarks:
        # Run the benchmark in a separate venv where the solvers
        # will be installed

        # Create the virtual env
        create_venv(benchmark, recreate=recreate)

        # Get the solvers and install them
        solvers = list_benchmark_solvers(benchmark)
        exclude = get_benchmark_setting(benchmark, 'exclude_solvers')
        solvers = filter_solvers(solvers, solver_names=solver_names,
                                 forced_solvers=forced_solvers,
                                 exclude=exclude)
        install_solvers(solvers=solvers, forced_solvers=forced_solvers,
                        env_name=benchmark)

        solvers_option = ' '.join(['-s '+s for s in solver_names])
        forced_solvers_option = ' '.join(['-f '+s for s in forced_solvers])
        cmd = (
            f"benchopt run --max-samples {max_samples} -n {repetition} "
            f"{solvers_option} {forced_solvers_option} {benchmark}"
        )
        exit_code = _run_bash_in_env(cmd, env_name=benchmark,
                                     capture_stdout=False)
        return_code[benchmark] = exit_code


def start():
    main()


if __name__ == '__main__':
    start()
