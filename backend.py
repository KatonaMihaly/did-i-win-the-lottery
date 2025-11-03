import streamlit as st
import pandas as pd
# Removed unused imports from typing to match the minimal style of the working code
import os
# Added pandas back, as it's needed for df_matches.itertuples
import pandas as pd 

class WinningNumbers:
    """A class to calculate winning numbers"""

    def __init__(self, _lottery_id, _input_numbers):
        """Initialize the class with lottery ID and the user's numbers."""
        self._lottery_id = _lottery_id
        self._input_numbers = _input_numbers

        # Placeholders to store the SQL queries.
        self.query_matches = ""
        self.query_total = ""

    def _check_validity_lottery(self):
        """Validate lottery ID is in the allowed list."""
        try:
            lottery_id_str = str(self._lottery_id)
            allowed_lotteries = ['hu5', 'hu6', 'hu7']

            if lottery_id_str not in allowed_lotteries:
                print(f"Invalid lottery_id value: {lottery_id_str}. Must be one of {allowed_lotteries}")
                return None
            return lottery_id_str

        except TypeError:
            print("Invalid lottery ID type. Cannot convert to string.")

    def _check_validity_numbers(self):
        """
        Validate numbers:
        - Convert to list of integers.
        - Check for correct length and range based on lottery_id.
        Returns the valid list of integers as a COMMA-SEPARATED STRING or None if validation fails.
        """
        # Convert input from a set to a list if necessary
        if isinstance(self._input_numbers, set):
            self._input_numbers = list(self._input_numbers)

        if not self._input_numbers:
            print("Error: No numbers provided.")
            return None

        try:
            # Convert all numbers in the list to integers
            numbers_list = [int(n) for n in self._input_numbers]
        except (ValueError, TypeError):
            print("Error: All input numbers must be convertible to integers.")
            return None

        # Define validation rules
        rules = {
            'hu5': {'length': 5, 'min': 1, 'max': 90},
            'hu6': {'length': 6, 'min': 1, 'max': 45},
            'hu7': {'length': 7, 'min': 1, 'max': 35}
        }

        lottery_rule = rules.get(self._lottery_id)

        if lottery_rule:
            # Check length
            if len(numbers_list) != lottery_rule['length']:
                print(
                    f"Error: Lottery '{self._lottery_id}' requires {lottery_rule['length']}"
                    f" numbers, but {len(numbers_list)} were provided.")
                return None

            # Check range
            for num in numbers_list:
                if not (lottery_rule['min'] <= num <= lottery_rule['max']):
                    print(
                        f"Error: Number {num} is out of range for '{self._lottery_id}'"
                        f" ({lottery_rule['min']}-{lottery_rule['max']}).")
                    return None

        # Return the validated list of integers converted to a comma-separated string
        return ','.join(map(str, numbers_list))

    def _run_db_queries(self, query_matches, match_params, query_total, total_params):
        """Helper method to connect to the DB and execute queries using st.connection."""
        try:
            # 1. Initialize the connection.
            conn = st.connection("snowflake")

            # 2. First query: find all matching draws
            # Pass the wrapped parameters list
            df_matches = conn.query(query_matches, params=match_params, ttl="1m")

            # 3. Second query: find the total number of draws
            # Pass the wrapped parameters list
            df_total = conn.query(query_total, params=total_params, ttl="1m")

            # Convert the matches DataFrame to a list of tuples,
            results = list(df_matches.itertuples(index=False, name=None))

            # Extract the single count value from the total_draws DataFrame
            total_draws = int(df_total.iloc[0, 0])

            # Return the data in the format your other methods expect
            return results, total_draws

        except Exception as e:
            # Handle any query or connection errors
            print(f"Database query error: {e}")
            return [], 0

    def check_lottery_numbers(self):
        """
        Main method to check lottery numbers against the database.
        """

        # Step 1: Validate the lottery ID
        lottery = self._check_validity_lottery()
        if not lottery:
            return [], 0

        # Step 2: Get the validated user's numbers as a COMMA-SEPARATED STRING
        numbers_str = self._check_validity_numbers() 
        if not numbers_str:
            return [], 0

        # Initialize variables
        formatted_results = []
        total_draws = 0

        # --- Logic for 'hu7' (which has two sets of numbers) ---
        if self._lottery_id == 'hu7':
            # 🟢 Standardized SQL using SPLIT and ARRAY_INTERSECTION
            self.query_matches = """
                SELECT
                    sub_a.draw_date,
                    sub_a.numbers AS numbers_a,
                    ARRAY_SIZE(ARRAY_INTERSECTION(SPLIT(numbers_a, ','), SPLIT(?, ','))) AS match_count_a,
                    sub_b.numbers AS numbers_b,
                    ARRAY_SIZE(ARRAY_INTERSECTION(SPLIT(numbers_b, ','), SPLIT(?, ','))) AS match_count_b
                FROM
                    (
                        SELECT draw_date, numbers
                        FROM draw
                        WHERE lottery_id = ?
                    ) AS sub_a

                INNER JOIN
                    (
                        SELECT draw_date, numbers
                        FROM draw
                        WHERE lottery_id = ?
                    ) AS sub_b
                ON
                    sub_a.draw_date = sub_b.draw_date
                WHERE
                    match_count_b > 0 OR
                    match_count_a > 0
                ORDER BY
                    sub_a.draw_date DESC;
                            """
            # Total query remains simple
            self.query_total = "SELECT COUNT(*) FROM draw WHERE lottery_id = ?;"
            
            match_params = (numbers_str, numbers_str, 'hu7a', 'hu7b',)
            total_params = ('hu7a',)

            # Get raw data from DB using the helper method
            raw_results, total_draws = self._run_db_queries(
                self.query_matches, match_params, self.query_total, total_params
            )

            # --- Format results for hu7 (Date, Match A, Match B) ---
            formatted_results = [(row[0].strftime("%Y-%m-%d"), row[1], row[2], row[3], row[4]) for row in
                                 raw_results]

        # --- Logic for 'hu5' or 'hu6' (which have one set of numbers) ---
        elif self._lottery_id == 'hu5' or self._lottery_id == 'hu6':
            self.query_matches = """
            SELECT draw_date, numbers,
                ARRAY_SIZE(ARRAY_INTERSECTION(
                    SPLIT(numbers, ','),
                    SPLIT(?, ',')
                )) AS match_count
            FROM draw
            WHERE lottery_id = ?
            AND match_count > 0 
            ORDER BY draw_date DESC;
            """
            # Total query remains simple
            self.query_total = "SELECT COUNT(*) FROM draw WHERE lottery_id = ?;"

            match_params = (numbers_str, lottery,) # Use the validated string
            total_params = (lottery,)

            # Get raw data from DB using the helper method
            raw_results, total_draws = self._run_db_queries(
                self.query_matches, match_params, self.query_total, total_params
            )

            # --- Format results for hu5/hu6 (Date, Numbers, Match Count) ---
            formatted_results = [(row[0].strftime("%Y-%m-%d"), row[1], row[2]) for row in raw_results]

        # Return the final formatted results and the total draw count
        return formatted_results, total_draws
