DROP TABLE IF EXISTS draw;
DROP TABLE IF EXISTS lottery;

CREATE TABLE lottery (
    id SERIAL PRIMARY KEY,
    name VARCHAR(10) NOT NULL,
    total_numbers INT NOT NULL,
    range_max INT NOT NULL
);

INSERT INTO lottery (name, total_numbers, range_max) VALUES
('hu5', 5, 90),
('hu6', 6, 45),
('hu7a', 7, 35),
('hu7b', 7, 35);

CREATE TABLE draw (
    id SERIAL PRIMARY KEY,
    lottery_id VARCHAR(4),
    draw_date DATE NOT NULL,
    numbers INT[] NOT NULL,
    UNIQUE(lottery_id, draw_date)
);

INSERT INTO draw (draw_date, lottery_id, numbers) VALUES
('2025-10-18', 'hu5', ARRAY[3,25,32,55,74]),
('2025-10-11', 'hu5', ARRAY[11,15,31,75,79]),
('2025-10-04', 'hu5', ARRAY[7,8,39,41,49]);

INSERT INTO draw (draw_date, lottery_id, numbers) VALUES
('2025-10-19', 'hu6', ARRAY[8,12,25,29,30,41]),
('2025-10-16', 'hu6', ARRAY[6,12,33,35,37,40]),
('2025-10-12', 'hu6', ARRAY[6,7,8,23,24,32]);

INSERT INTO draw (draw_date, lottery_id, numbers) VALUES
('2025-10-29', 'hu7a', ARRAY[4,6,9,10,20,29,30]),
('2025-10-22', 'hu7a', ARRAY[1,2,4,7,9,16,23]),
('2025-10-15', 'hu7a', ARRAY[8,10,11,15,18,22,28]);

INSERT INTO draw (draw_date, lottery_id, numbers) VALUES
('2025-10-29', 'hu7b', ARRAY[4,15,18,20,21,29,32]),
('2025-10-22', 'hu7b', ARRAY[2,3,5,6,25,34,35]),
('2025-10-15', 'hu7b', ARRAY[3,8,14,15,19,24,31]);