# Unittests and Integration Tests

This project demonstrates unit testing and integration testing patterns in Python, focusing on testing a GitHub organization client API wrapper.

## Project Overview

This project implements:
- **utils.py**: Utility functions for accessing nested data structures, making HTTP requests, and caching results
- **client.py**: A GitHub organization client that fetches org and repository information
- **test_utils.py**: Unit tests for utility functions using parameterization and mocking
- **test_client.py**: Unit and integration tests for the GitHub client with fixtures

## Learning Objectives

At the end of this project, you should understand:
- The difference between unit tests and integration tests
- How to use mocking to isolate code under test
- How to parameterize tests to cover multiple scenarios
- How to use fixtures for integration testing
- How to work with the `unittest` framework and `unittest.mock` library

## Project Structure

```
.
├── utils.py              # Utility functions module
├── client.py             # GitHub org client module
├── fixtures.py           # Test fixtures with sample data
├── test_utils.py         # Unit tests for utils
├── test_client.py        # Unit and integration tests for client
└── README.md             # This file
```

## Requirements

- Python 3.7+
- Dependencies:
  - `requests` - HTTP library
  - `parameterized` - Parameterized testing library
  - `unittest` - Python's built-in testing framework (included in standard library)
  - `unittest.mock` - Mocking framework (included in standard library)

## Installation

Install the required dependencies:

```bash
pip install requests parameterized
```

## Running Tests

### Run all unit tests for utils:

```bash
python -m unittest test_utils.py
```

### Run all unit and integration tests for client:

```bash
python -m unittest test_client.py
```

### Run specific test class:

```bash
python -m unittest test_utils.TestAccessNestedMap
python -m unittest test_client.TestGithubOrgClient
python -m unittest test_client.TestIntegrationGithubOrgClient
```

### Run specific test method:

```bash
python -m unittest test_utils.TestAccessNestedMap.test_access_nested_map
```

### Run all tests with verbose output:

```bash
python -m unittest discover -v
```

## Module Documentation

### utils.py

#### access_nested_map(nested_map, path)
Access a value in a nested dictionary using a sequence of keys.

**Example:**
```python
nested_map = {"a": {"b": {"c": 1}}}
result = access_nested_map(nested_map, ("a", "b", "c"))  # Returns 1
```

#### get_json(url)
Fetch and return JSON data from a remote URL.

**Example:**
```python
data = get_json("https://api.github.com/orgs/google")
```

#### memoize(fn)
Decorator to cache function results by converting method to property.

**Example:**
```python
class MyClass:
    @memoize
    def expensive_property(self):
        return expensive_computation()

obj = MyClass()
result1 = obj.expensive_property  # Computed
result2 = obj.expensive_property  # Cached result
```

### client.py

#### GithubOrgClient(org_name)
A client for fetching GitHub organization data.

**Methods:**
- `org` - Returns organization information (memoized)
- `_public_repos_url` - Returns the URL for public repositories
- `public_repos(license=None)` - Returns list of public repository names, optionally filtered by license
- `has_license(repo, license_key)` - Static method to check if a repository has a specific license

**Example:**
```python
client = GithubOrgClient("google")
org_data = client.org  # Returns org information
repos = client.public_repos()  # Returns all public repos
apache_repos = client.public_repos(license="apache-2.0")  # Returns Apache-licensed repos
```

## Testing Patterns

### Unit Testing Patterns

#### 1. Parameterized Testing
Tests the same function with multiple inputs:
```python
@parameterized.expand([
    (input1, expected1),
    (input2, expected2),
])
def test_function(self, input_val, expected):
    self.assertEqual(function(input_val), expected)
```

#### 2. Mocking External Dependencies
Replaces external calls with mock objects:
```python
@patch("module.requests.get")
def test_function(self, mock_get):
    mock_get.return_value = Mock()
    # Test without making actual HTTP calls
```

#### 3. Mocking Properties
Uses PropertyMock to mock @property and @memoize decorated methods:
```python
with patch.object(Class, "property", new_callable=PropertyMock) as mock_prop:
    mock_prop.return_value = expected_value
    # Test code
```

#### 4. Exception Testing
Verifies that functions raise expected exceptions:
```python
with self.assertRaises(KeyError) as context:
    function_that_raises()
self.assertEqual(str(context.exception), "'expected_key'")
```

### Integration Testing Patterns

#### 1. Parameterized Classes
Uses @parameterized_class decorator to run same test class with different fixtures:
```python
@parameterized_class(
    ("param1", "param2"),
    [(value1_a, value1_b), (value2_a, value2_b)]
)
class TestIntegration(unittest.TestCase):
    # Tests run with different parameter values
```

#### 2. setUp/tearDown for Fixtures
Manages test fixtures at class level:
```python
@classmethod
def setUpClass(cls):
    # Start mocking and set up fixtures
    cls.patcher = patch("module.function")
    cls.mock = cls.patcher.start()

@classmethod
def tearDownClass(cls):
    # Clean up mocks
    cls.patcher.stop()
```

#### 3. Side Effects for Complex Mocking
Uses side_effect to return different values based on parameters:
```python
def mock_side_effect(url):
    if url == "url1":
        return value1
    elif url == "url2":
        return value2
    return default_value

mock_function.side_effect = mock_side_effect
```

## Code Quality

All code follows PEP 8 style guidelines using pycodestyle.

### Check code style:
```bash
pycodestyle utils.py client.py test_utils.py test_client.py
```

## Test Coverage

The test suite covers:
- **access_nested_map**: Normal cases and exception cases
- **get_json**: HTTP requests with different payloads
- **memoize**: Caching behavior and single call verification
- **GithubOrgClient.org**: Correct URL generation and mocking
- **GithubOrgClient._public_repos_url**: Property access with mocking
- **GithubOrgClient.public_repos**: Filtering by license and result verification
- **GithubOrgClient.has_license**: License key validation
- **Integration**: End-to-end tests with fixtures

## Files and Lines of Code

- **utils.py**: Utility functions with full documentation
- **client.py**: GitHub client implementation (pre-provided)
- **fixtures.py**: Test fixtures with sample GitHub API responses (pre-provided)
- **test_utils.py**: ~100 lines of comprehensive unit tests
- **test_client.py**: ~150 lines of unit and integration tests

## Author Notes

This project demonstrates professional testing practices:

1. **Separation of Concerns**: Tests focus on single responsibilities
2. **Proper Mocking**: External dependencies are mocked to isolate code under test
3. **Comprehensive Coverage**: Both success and failure cases are tested
4. **Clear Documentation**: All modules, classes, and functions are well-documented
5. **Type Hints**: All functions include type annotations
6. **Parameterization**: Tests cover multiple scenarios efficiently
7. **Fixtures**: Integration tests use realistic test data

## References

- [unittest Documentation](https://docs.python.org/3/library/unittest.html)
- [unittest.mock Documentation](https://docs.python.org/3/library/unittest.mock.html)
- [parameterized Library](https://pypi.org/project/parameterized/)
- [PEP 8 Style Guide](https://www.python.org/dev/peps/pep-0008/)
