from backend.app.runtime.background_worker_loop import (
    run_once,
    worker_live_execution_enabled,
)


def main():
    status = run_once()

    if status["worker"] != "background_worker_loop":
        raise AssertionError("Wrong worker name")

    if status["status"] != "running":
        raise AssertionError("Worker status not running")

    if status["jobs_executed"] is not False:
        raise AssertionError("Worker should not execute jobs in foundation mode")

    if status["external_provider_called"] is not False:
        raise AssertionError("Worker should not call providers in foundation mode")

    if worker_live_execution_enabled() is not False:
        raise AssertionError("Worker live execution should be false by default")

    print("BACKGROUND_WORKER_LOOP_TEST_PASSED")
    print(status)


if __name__ == "__main__":
    main()
