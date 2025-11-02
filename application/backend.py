# --- Import necessary libraries ---
import psycopg2  # PostgreSQL database adapter
from dotenv import load_dotenv  # To load environment variables from a .env file
import os  # To access environment variables

# Load environmental variables from .env file into the script's environment
load_dotenv()


class WinningNumbers:
    """A class to calculate winning numbers"""

    def __init__(self, _lottery_id, _input_numbers):
        """Initialize the class with lottery ID and the user's numbers."""
        self._lottery_id = _lottery_id
        self._input_numbers = _input_numbers

        # Load database connection details from environment variables
        self._DB_NAME = os.getenv("DB_NAME")
        self._DB_USER = os.getenv("DB_USER")
        self._DB_PASSWORD = os.getenv("DB_PASSWORD")
        self._DB_HOST = os.getenv("DB_HOST")
        self._DB_PORT = os.getenv("DB_PORT")

        # Placeholders to store the SQL queries.
        self.query_matches = ""
        self.query_total = ""

    def _check_validity_lottery(self):
        """Validate lottery ID is in the allowed list."""
        # Ensure the lottery_id is a string for comparison
        try:
            lottery_id_str = str(self._lottery_id)

            # Define the list of supported lotteries
            allowed_lotteries = ['hu5', 'hu6', 'hu7']

            # Check if the provided ID is in our allowed list
            if lottery_id_str not in allowed_lotteries:
                # Print an error if invalid and return None
                print(f"Invalid lottery_id value: {lottery_id_str}. Must be one of {allowed_lotteries}")
                return None  # Invalid

            return lottery_id_str  # Return the valid string ID

        except TypeError:
            print("Invalid lottery ID type. Cannot convert to string.")

    def _check_validity_numbers(self):
        """
        Validate numbers:
        - Convert to list of integers.
        - Check for correct length and range based on lottery_id.
        Returns list of valid integers or None if validation fails.
        """
        # Convert input from a set to a list if necessary
        if isinstance(self._input_numbers, set):
            self._input_numbers = list(self._input_numbers)

        # Check if the input list is empty
        if not self._input_numbers:
            print("Error: No numbers provided.")
            return None

        try:
            # Convert all numbers in the list to integers
            numbers_list = [int(n) for n in self._input_numbers]
        except (ValueError, TypeError):
            # Fail if any number cannot be converted to an integer
            print("Error: All input numbers must be convertible to integers.")
            return None  # Failed validation

        # Define validation rules for each lottery type
        rules = {
            'hu5': {'length': 5, 'min': 1, 'max': 90},  # 5 numbers, 1-90
            'hu6': {'length': 6, 'min': 1, 'max': 45},  # 6 numbers, 1-45
            'hu7': {'length': 7, 'min': 1, 'max': 35}  # 7 numbers, 1-35
        }

        # Get the specific rule set for the current lottery_id
        lottery_rule = rules.get(self._lottery_id)

        # Apply the rules if they exist
        if lottery_rule:
            # Check if the correct number of numbers was provided
            if len(numbers_list) != lottery_rule['length']:
                print(
                    f"Error: Lottery '{self._lottery_id}' requires {lottery_rule['length']}"
                    f" numbers, but {len(numbers_list)} were provided.")
                return None  # Failed validation

            # Check if all numbers are within the allowed min/max range
            for num in numbers_list:
                if not (lottery_rule['min'] <= num <= lottery_rule['max']):
                    print(
                        f"Error: Number {num} is out of range for '{self._lottery_id}'"
                        f" ({lottery_rule['min']}-{lottery_rule['max']}).")
                    return None  # Failed validation

        # If all checks pass, return the validated list of integers
        return numbers_list

    def _run_db_queries(self, query_matches, match_params, query_total, total_params):
        """Helper method to connect to the DB and execute queries."""
        try:
            with psycopg2.connect(
                    dbname=self._DB_NAME,
                    user=self._DB_USER,
                    password=self._DB_PASSWORD,
                    host=self._DB_HOST,
                    port=self._DB_PORT
            ) as conn:
                with conn.cursor() as cur:
                    # First query: find all matching draws
                    cur.execute(query_matches, match_params)
                    results = cur.fetchall()  # Get all matching rows

                    # Second query: find the total number of draws for this lottery
                    cur.execute(query_total, total_params)
                    total_draws = cur.fetchone()[0]  # Get the count

            # Return the raw results from the database
            return results, total_draws

        except (psycopg2.OperationalError, psycopg2.DatabaseError) as e:
            # Handle database-specific errors (e.g., connection failed)
            print(f"Database error: {e}")
            return [], 0  # Return empty results so the app doesn't crash
        except Exception as e:
            # Handle any other unexpected errors
            print(f"An unexpected error occurred: {e}")
            return [], 0

    def check_lottery_numbers(self):
        """
        Main method to check lottery numbers against the database.
        It validates input, defines queries, runs them, and formats the output.
        """

        # Step 1: Validate the lottery ID
        lottery = self._check_validity_lottery()
        if not lottery:
            return [], 0  # Invalid lottery_id, return empty results

        # Step 2: Validate the user's numbers
        numbers = self._check_validity_numbers()
        if not numbers:
            return [], 0  # Invalid numbers, return empty results

        # Initialize variables
        formatted_results = []
        total_draws = 0

        # --- Logic for 'hu7' (which has two sets of numbers) ---
        if self._lottery_id == 'hu7':
            # This query joins the draw table on itself to check for matches
            # against two different sets of numbers (machine 'a' and manual 'b')
            # using the same user-provided number list.
            self.query_matches = """
                        SELECT
                            sub_a.draw_date,
                            sub_a.numbers,
                            sub_a.match_count AS match_count_a,
                            sub_b.numbers,
                            sub_b.match_count AS match_count_b
                        FROM
                            (
                                SELECT
                                    draw_date, numbers,
                                    CARDINALITY(ARRAY(
                                        SELECT UNNEST(numbers)
                                        INTERSECT
                                        SELECT UNNEST(%s::int[]) -- This is numbers_set_a
                                    )) AS match_count
                                FROM draw
                                WHERE lottery_id = %s -- This is lottery_id 'hu7a'
                            ) AS sub_a

                        INNER JOIN
                            (
                                SELECT
                                    draw_date, numbers,
                                    CARDINALITY(ARRAY(
                                        SELECT UNNEST(numbers)
                                        INTERSECT
                                        SELECT UNNEST(%s::int[]) -- This is numbers_set_b
                                    )) AS match_count
                                FROM draw
                                WHERE lottery_id = %s -- This is lottery_id 'hu7b'
                            ) AS sub_b
                        ON
                            sub_a.draw_date = sub_b.draw_date
                        WHERE
                            sub_b.match_count > 0 OR
                            sub_a.match_count > 0
                        ORDER BY
                            sub_a.draw_date DESC;
                            """
            # Query to get the total number of draws (e.g., for 'hu7a')
            self.query_total = "SELECT COUNT(*) FROM draw WHERE lottery_id = %s;"

            # Define parameters for the queries
            match_params = (numbers, 'hu7a', numbers, 'hu7b')
            total_params = ('hu7a',)  # Total draws for one type is sufficient

            # Get raw data from DB using the helper method
            raw_results, total_draws = self._run_db_queries(
                self.query_matches, match_params, self.query_total, total_params
            )

            # --- Format results for hu7 (Date, Match A, Match B) ---
            formatted_results = [(row[0].strftime("%Y-%m-%d"), row[1], row[2], row[3], row[4]) for row in raw_results]

        # --- Logic for 'hu5' or 'hu6' (which have one set of numbers) ---
        elif self._lottery_id == 'hu5' or self._lottery_id == 'hu6':
            # This query is simpler: it just finds matches for one lottery type.
            self.query_matches = """
            SELECT * FROM (
                SELECT draw_date, numbers,
                       CARDINALITY(ARRAY(
                           SELECT UNNEST(numbers)
                           INTERSECT
                           SELECT UNNEST(%s::int[])
                       )) AS match_count
                FROM draw
                WHERE lottery_id = %s
            ) AS sub
            WHERE match_count > 0
            ORDER BY draw_date DESC;
            """
            # Query to get the total number of draws
            self.query_total = "SELECT COUNT(*) FROM draw WHERE lottery_id = %s;"

            # Define parameters for the queries
            match_params = (numbers, lottery)
            total_params = (lottery,)

            # Get raw data from DB using the helper method
            raw_results, total_draws = self._run_db_queries(
                self.query_matches, match_params, self.query_total, total_params
            )

            # --- Format results for hu5/hu6 (Date, Match Count) ---
            formatted_results = [(row[0].strftime("%Y-%m-%d"), row[1], row[2]) for row in raw_results]

        # Return the final formatted results and the total draw count
        return formatted_results, total_draws
