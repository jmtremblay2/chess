--DROP TABLE moves;
--DROP TABLE description;
--create types
DO $$
BEGIN
    IF NOT EXISTS (SELECT 1 FROM pg_type WHERE typname = 'player') THEN
		CREATE TYPE player AS ENUM ('white', 'black');
    END IF;
	
	IF NOT EXISTS (SELECT 1 FROM pg_type WHERE typname = 'piece') THEN
		CREATE TYPE piece AS ENUM (
				'0',
    
				'R',
				'N',
				'B',
				'Q',
				'K',
				'P',

				'r',
				'n',
				'b',
				'q',
				'k',
				'p');
    END IF;
	
	IF NOT EXISTS (SELECT 1 FROM pg_type WHERE typname = 'square') THEN
		CREATE TYPE square AS ENUM (
			'a1','a2','a3','a4','a5','a6','a7','a8',
			'b1','b2','b3','b4','b5','b6','b7','b8',
			'c1','c2','c3','c4','c5','c6','c7','c8',
			'd1','d2','d3','d4','d5','d6','d7','d8',
			'e1','e2','e3','e4','e5','e6','e7','e8',
			'f1','f2','f3','f4','f5','f6','f7','f8',
			'g1','g2','g3','g4','g5','g6','g7','g8',
			'h1','h2','h3','h4','h5','h6','h7','h8');

    END IF;
	
	
    --more types here...
END$$;

CREATE TABLE IF NOT EXISTS description(
    gameid INTEGER check (gameid > 0),
    Black text,
	BlackElo integer check (BlackElo BETWEEN 0 and 3000),
	Date date check (Date BETWEEN '1900-01-01' AND '2018-05-01'),
	ECO text,
	Event text,
	EventDate date check (EventDate BETWEEN '1900-01-01' AND '2018-05-01'),
	Result text check (Result IN ('1/2-1/2','1-0','0-1','*')),
	Round text,
	Site text,
	White text,
	WhiteElo integer check (WhiteElo BETWEEN 0 and 3000),
    
    played text[],
    
    PRIMARY KEY(gameid)
);

CREATE TABLE IF NOT EXISTS board(
	gameid INTEGER,
    moveid INTEGER check(moveid BETWEEN 1 and 500),
    player player,
    
    played text,
    
    board char(1)[8][8],
    
    enpassant square check (enpassant IN ('a3','b3','c3','d3','e3','f3','g3','h3','a6','b6','c6','d6','e6','f6','g6','h6')),
    
    whitecastlequeen bool,
    whitecastleking bool,
    blackcastlequeen bool,
    blackcastleking bool,    
    
    PRIMARY KEY(gameid, moveid, player),
    FOREIGN KEY(gameid) REFERENCES description(gameid) DEFERRABLE);
	
--GRANT ALL PRIVILEGES ON ALL TABLES IN SCHEMA public TO chess;
