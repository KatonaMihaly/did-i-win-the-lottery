import unittest
from unittest.mock import patch, MagicMock
import os
import datetime
import psycopg2

from backend import WinningNumbers

# Define mock environment variables for testing
MOCK_ENV_VARS = {
    "DB_NAME": "fake_db",
    "DB_USER": "fake_user",
    "DB_PASSWORD": "fake_password",
    "DB_HOST": "fake_host",
    "DB_PORT": "5432"
}

# Use patch.dict to set the environment variables *before* the class is tested
@patch.dict(os.environ, MOCK_ENV_VARS)
class TestValidation(unittest.TestCase):
    """Tests for all data validation methods."""

    def test_validity_lottery_ok(self):
        """Test that valid lottery IDs are accepted."""
        for lid in ['hu5', 'hu6', 'hu7']:
            with self.subTest(lid=lid):
                wn = WinningNumbers(lid, [])
                self.assertEqual(wn._check_validity_lottery(), lid)

    def test_validity_lottery_invalid_str(self):
        """Test that invalid string lottery IDs are rejected."""
        wn = WinningNumbers('invalid_id', [])
        self.assertIsNone(wn._check_validity_lottery())

    def test_validity_lottery_invalid_type(self):
        """Test that non-string-convertible lottery IDs are rejected."""
        wn_int = WinningNumbers(12345, [])
        self.assertIsNone(wn_int._check_validity_lottery())

        # Test the try/except block
        wn_none = WinningNumbers(None, [])
        self.assertIsNone(wn_none._check_validity_lottery())

    def test_validity_numbers_hu5_ok(self):
        """Test valid hu5 numbers (len 5, range 1-90)."""
        valid_nums = [1, 10, 20, 30, 90]
        wn = WinningNumbers('hu5', valid_nums)
        self.assertEqual(wn._check_validity_numbers(), valid_nums)

    def test_validity_numbers_hu5_invalid_length(self):
        """Test hu5 with incorrect number count."""
        invalid_nums = [1, 10, 20, 30]  # Only 4
        wn = WinningNumbers('hu5', invalid_nums)
        self.assertIsNone(wn._check_validity_numbers())

    def test_validity_numbers_hu5_invalid_range(self):
        """Test hu5 with numbers out of range (1-90)."""
        invalid_nums_high = [1, 10, 20, 30, 91]  # 91 is too high
        wn_high = WinningNumbers('hu5', invalid_nums_high)
        self.assertIsNone(wn_high._check_validity_numbers())

    def test_validity_numbers_hu6_ok(self):
        """Test valid hu6 numbers (len 6, range 1-45)."""
        valid_nums = [1, 10, 20, 30, 40, 45]
        wn = WinningNumbers('hu6', valid_nums)
        self.assertEqual(wn._check_validity_numbers(), valid_nums)

    def test_validity_numbers_hu6_invalid_length(self):
        """Test hu6 with incorrect number count."""
        invalid_nums = [1, 10, 20, 30, 40]  # Only 5
        wn = WinningNumbers('hu6', invalid_nums)
        self.assertIsNone(wn._check_validity_numbers())

    def test_validity_numbers_hu6_invalid_range(self):
        """Test hu6 with number out of range (1-45)."""
        invalid_nums = [1, 10, 20, 30, 40, 46]  # 46 is too high
        wn = WinningNumbers('hu6', invalid_nums)
        self.assertIsNone(wn._check_validity_numbers())

    def test_validity_numbers_hu7_ok(self):
        """Test valid hu7 numbers (len 7, range 1-35)."""
        valid_nums = [1, 5, 10, 15, 20, 25, 35]
        wn = WinningNumbers('hu7', valid_nums)
        self.assertEqual(wn._check_validity_numbers(), valid_nums)

    def test_validity_numbers_hu7_invalid_length(self):
        """Test hu7 with incorrect number count."""
        invalid_nums = [1, 10, 20, 30, 40, 50]  # Only 6
        wn = WinningNumbers('hu7', invalid_nums)
        self.assertIsNone(wn._check_validity_numbers())

    def test_validity_numbers_hu7_invalid_range(self):
        """Test hu7 with number out of range (1-35)."""
        invalid_nums = [1, 5, 10, 15, 20, 25, 36]  # 36 is too high
        wn = WinningNumbers('hu7', invalid_nums)
        self.assertIsNone(wn._check_validity_numbers())

    def test_validity_numbers_from_set(self):
        """Test that a set input is correctly converted to a list."""
        valid_set = {1, 10, 20, 30, 90}
        wn = WinningNumbers('hu5', valid_set)
        self.assertEqual(sorted(wn._check_validity_numbers()), sorted(list(valid_set)))

    def test_validity_numbers_empty(self):
        """Test that an empty list is rejected."""
        wn = WinningNumbers('hu5', [])
        self.assertIsNone(wn._check_validity_numbers())

    def test_validity_numbers_non_int(self):
        """Test that a list with non-integers is rejected."""
        wn = WinningNumbers('hu5', [1, 2, 'a', 4, 5])
        self.assertIsNone(wn._check_validity_numbers())


@patch.dict(os.environ, MOCK_ENV_VARS)
class TestDatabaseInteraction(unittest.TestCase):
    """
    Tests the main check_lottery_numbers method and db helper
    with mocked database interaction to test the logic.
    """

    def setUp(self):
        """Create a standard date object for mocking."""
        self.mock_date = datetime.datetime(2023, 1, 1)

    @patch('backend.WinningNumbers._run_db_queries')
    def test_check_lottery_numbers_hu5_success(self, mock_run_db_queries):
        """Test the hu5 logic with mocked db results."""
        # 1. Define mock data
        mock_raw_results = [(self.mock_date, [1, 2, 6, 7, 8], 2)]
        mock_total_draws = 50
        mock_run_db_queries.return_value = (mock_raw_results, mock_total_draws)

        valid_nums = [1, 2, 3, 4, 5]
        wn = WinningNumbers('hu5', valid_nums)

        # 2. Call the main method
        results, total_draws = wn.check_lottery_numbers()

        # 3. Assert the results are correctly formatted
        expected_results = [("2023-01-01", [1, 2, 6, 7, 8], 2)]
        self.assertEqual(results, expected_results)
        self.assertEqual(total_draws, mock_total_draws)

        # 4. Assert the db helper was called with the correct parameters

        # MODIFIED: Assert match_params uses the dictionary format
        expected_match_params = {"number": valid_nums, "id": 'hu5'}

        # MODIFIED: Assert total_params uses the dictionary format
        expected_total_params = {"id": 'hu5'}

        mock_run_db_queries.assert_called_once_with(
            wn.query_matches, expected_match_params, wn.query_total, expected_total_params
        )

    @patch('backend.WinningNumbers._run_db_queries')
    def test_check_lottery_numbers_hu6_success(self, mock_run_db_queries):
        """Test the hu6 logic with mocked db results."""
        # 1. Define mock data
        mock_raw_results = [(self.mock_date, [1, 2, 7, 8, 9, 10], 2)]
        mock_total_draws = 50
        mock_run_db_queries.return_value = (mock_raw_results, mock_total_draws)

        valid_nums = [1, 2, 3, 4, 5, 6]
        wn = WinningNumbers('hu6', valid_nums)

        # 2. Call the main method
        results, total_draws = wn.check_lottery_numbers()

        # 3. Assert the results are correctly formatted
        # Expected results must match the output format: (date_str, numbers_list, match_count)
        expected_results = [("2023-01-01", [1, 2, 7, 8, 9, 10], 2)]
        self.assertEqual(results, expected_results)
        self.assertEqual(total_draws, mock_total_draws)

        # 4. Assert the db helper was called with the correct parameters
        # MODIFIED: Assert expected parameters are dictionaries
        expected_match_params = {"number": valid_nums, "id": 'hu6'}
        expected_total_params = {"id": 'hu6'}

        mock_run_db_queries.assert_called_once_with(
            wn.query_matches, expected_match_params, wn.query_total, expected_total_params
        )

    @patch('backend.WinningNumbers._run_db_queries')
    def test_check_lottery_numbers_hu7_success(self, mock_run_db_queries):
        """Test the hu7 logic with mocked db results."""
        # 1. Define mock data
        mock_raw_results = [(self.mock_date, [1, 2, 8, 9, 10, 11, 12], 2, [1, 2, 10, 11, 12, 13, 14], 3)]
        mock_total_draws = 50
        mock_run_db_queries.return_value = (mock_raw_results, mock_total_draws)

        valid_nums = [1, 2, 3, 4, 5, 6, 7]
        wn = WinningNumbers('hu7', valid_nums)

        # 2. Call the main method
        results, total_draws = wn.check_lottery_numbers()

        # 3. Assert the results are correctly formatted
        # Expected results must match the output format: (date_str, numbers_a, match_a, numbers_b, match_b)
        expected_results = [("2023-01-01", [1, 2, 8, 9, 10, 11, 12], 2, [1, 2, 10, 11, 12, 13, 14], 3)]
        self.assertEqual(results, expected_results)
        self.assertEqual(total_draws, mock_total_draws)

        # 4. Assert the db helper was called with the correct parameters
        # MODIFIED: Assert expected parameters are dictionaries
        expected_match_params = {
            "numbers_a": valid_nums,
            "id_a": 'hu7a',
            "numbers_b": valid_nums,
            "id_b": 'hu7b'
        }
        expected_total_params = {"id": 'hu7a'}

        mock_run_db_queries.assert_called_once_with(
            wn.query_matches, expected_match_params, wn.query_total, expected_total_params
        )

    @patch('backend.WinningNumbers._run_db_queries')
    def test_check_lottery_numbers_invalid_id(self, mock_run_db_queries):
        """Test that an invalid lottery ID stops execution."""
        wn = WinningNumbers('invalid', [1, 2, 3, 4, 5])
        results, total_draws = wn.check_lottery_numbers()

        # Assert we get empty results and the db is NOT called
        self.assertEqual(results, [])
        self.assertEqual(total_draws, 0)
        mock_run_db_queries.assert_not_called()

    @patch('backend.WinningNumbers._run_db_queries')
    def test_check_lottery_numbers_h5_invalid_numbers(self, mock_run_db_queries):
        """Test that invalid numbers stop execution."""
        wn = WinningNumbers('hu5', [1, 2])  # Invalid length
        results, total_draws = wn.check_lottery_numbers()

        # Assert we get empty results and the db is NOT called
        self.assertEqual(results, [])
        self.assertEqual(total_draws, 0)
        mock_run_db_queries.assert_not_called()

    @patch('backend.WinningNumbers._run_db_queries')
    def test_check_lottery_numbers_h6_invalid_numbers(self, mock_run_db_queries):
        """Test that invalid numbers stop execution."""
        wn = WinningNumbers('hu6', [1, 2])  # Invalid length
        results, total_draws = wn.check_lottery_numbers()

        # Assert we get empty results and the db is NOT called
        self.assertEqual(results, [])
        self.assertEqual(total_draws, 0)
        mock_run_db_queries.assert_not_called()

    @patch('backend.WinningNumbers._run_db_queries')
    def test_check_lottery_numbers_h7_invalid_numbers(self, mock_run_db_queries):
        """Test that invalid numbers stop execution."""
        wn = WinningNumbers('hu7', [1, 2])  # Invalid length
        results, total_draws = wn.check_lottery_numbers()

        # Assert we get empty results and the db is NOT called
        self.assertEqual(results, [])
        self.assertEqual(total_draws, 0)
        mock_run_db_queries.assert_not_called()

    @patch('psycopg2.connect')
    def test_run_db_queries_db_error(self, mock_connect):
        """Test that _run_db_queries returns empty on a db error."""
        # Make the connect call raise an error
        mock_connect.side_effect = psycopg2.OperationalError("Connection failed")

        wn = WinningNumbers('hu5', [1, 2, 3, 4, 5])

        # Call the helper method directly
        results, total_draws = wn._run_db_queries(
            "fake_query", (), "fake_query_total", ()
        )

        # Assert it catches the error and returns empty results
        self.assertEqual(results, [])
        self.assertEqual(total_draws, 0)


if __name__ == '__main__':
    unittest.main()

