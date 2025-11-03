mport streamlit as st
import pandas as pd

# The simple test query to fetch all lotteries
LOTTERY_QUERY = "SELECT id, name, total_numbers, range_max FROM lottery ORDER BY id;"

def run_db_query(query):
    """
    Connects to Snowflake, runs the query, and returns the result as a DataFrame.
    """
    try:
        # Connect using the named connection defined in secrets.toml
        conn = st.connection("snowflake", type="sql")
        
        # Display feedback in the Streamlit app
        st.info("Attempting to connect to Snowflake and execute query...")
        
        # Execute the query and cache the results for 60 seconds
        df = conn.query(query, ttl="60s")
        
        st.success("✅ Database connection successful and query executed.")
        return df

    except Exception as e:
        st.error("❌ Connection or Query Failed.")
        st.exception(e)
        return pd.DataFrame() # Return empty DataFrame on failure


# --- Main Application Logic ---

def app():
    st.set_page_config(page_title="Minimal Streamlit DB Example", layout="centered")
    st.title("Snowflake Lottery Data Viewer")
    
    st.markdown(
        """
        This is a minimal Streamlit application demonstrating a connection 
        to Snowflake using `st.connection()` and running a simple SELECT query 
        against the `lottery` table.
        """
    )

    # Run the query
    lottery_data = run_db_query(LOTTERY_QUERY)

    # Display the results if data was returned
    if not lottery_data.empty:
        st.subheader("Results from the 'lottery' table:")
        # Display the DataFrame in a Streamlit table format
        st.dataframe(lottery_data)
    else:
        st.warning("No data returned or query failed.")

if __name__ == "__main__":
    app()