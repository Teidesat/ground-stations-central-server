# TESTING

## How to Use pytest in the Project
Prerequisites:

Docker Containers:
Ensure your Docker containers are running. If not, start them using:

    docker-compose up -d


Access the Container:

Via Terminal:
Run the following command to enter the container:

        docker exec -it ground-station-central-server bash

Replace ground-station-central-server with your container name if different.

Via Docker Desktop:
Open Docker Desktop, navigate to the container, and click the "Terminal" button to access the shell.

## Running Tests with pytest:

Once inside the container, navigate to the project directory (if necessary) and run:
    pytest

This executes all test files in the project (files matching test_*.py or *_test.py).

### Common pytest Arguments:

-v (Verbose Mode):
Displays detailed test results, including names of individual tests.

    pytest -v

Example output:

    test_calculation.py::test_add PASSED
    test_calculation.py::test_subtract FAILED

-k <expression> (Filter Tests by Keyword):
Runs only tests whose names match the given expression.
This executes tests with "add" or "multiply" in their names.

     pytest -k "add or multiply"


-x (Stop on First Failure):
Exits immediately if any test fails.
Useful for debugging critical failures early.

    pytest -x


Combining Flags:
Mix flags for granular control. For example:

    pytest -v -k "validation" -x

This runs verbose tests matching "validation" and stops at the first failure.

Example Workflow:

Start the containers:

    docker-compose up -d

Enter the container:

    docker exec -it ground-station-central-server bash

Run all tests with verbosity:

    pytest -v

Debug a specific test:

    pytest -v -k "test_api_response" -x