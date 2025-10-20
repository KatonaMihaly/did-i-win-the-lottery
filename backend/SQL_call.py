import psycopg2

def check_lottery_numbers(lottery_id, user_numbers):
    # Connect to PostgreSQL
    conn = psycopg2.connect(dbname='your_db', user='your_user', password='your_password', host='localhost')
    cur = conn.cursor()

    # SQL query: computes how many numbers match for each draw of the specified lottery
    sql = """
    SELECT draw_date,
           cardinality(ARRAY(
               SELECT UNNEST(numbers) 
               INTERSECT 
               SELECT UNNEST(%s::int[])
           )) AS match_count
    FROM draw
    WHERE lottery_id = (
        SELECT id FROM lottery WHERE name = %s
    )
    ORDER BY draw_date DESC;
    """

    cur.execute(sql, (user_numbers, lottery_id))
    results = cur.fetchall()
    cur.close()
    conn.close()

    # Return list of dicts with draw date and number of matches
    return [{'draw_date': row[0], 'match_count': row[1]} for row in results]

# Example usage
user_nums = [3, 25, 32, 55, 74]
lottery = 'Hu5'
matches_per_draw = check_lottery_numbers(lottery, user_nums)
print(matches_per_draw)
