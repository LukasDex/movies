# Movies OMDb API scraper

Script is using OMDb API for filling database with information about movies. Program also provides commands for printing information gathered in database.

All commands can be written one after another in a single line (e.g. python3 movies.py --set_file_name "thisfile.sqlite" --add "Memento" "The Avengers" --highscores)
Script works on file passed in --set_file_name command. If no file name passed, program will work on default "moviesdata.sqlite" file.

Available commands:

--set_file_name "filename.sqlite"
Setting file to work on "filename.sqlite". If file doesn’t exists new file will be created. Every command after this one will work with that file. 

--add "movie_name" "movie_name2"
Adding movies to data source. Multiple movies names can be passed. Requires internet connection.

--load_data "filename.sqlite"
Adding all movies from filename.sqlite. File must contain table named MOVIES with column TITLE containing movie names. Multiple files names can be passed. Requires internet connection.

--sort_by "column_name"
Printing database sorted by given column. Command prints movies titles and given column.
Available column names: year, runtime, genre, director, writer, language, country, imdb_rating, imdb_votes, actors, box_office, oscars_won, oscars_nominations, all_wins, all_nominations

--filter_by "column_name" "str"
Printing movies titles and given column where str could be found. (e.g. --filter_by language "English")
Available column names: director, actors, language

--filter_by "option"
option can be: 
oscar - printing all movies names that were nominated to oscar but didn't win any
over_80 - printing all movies names that won over 80% of awards that they were nominated for
over_100_mil - printing all movies with box office over 100 millions dollars

--highscores
Printing movies titles that are best in: runtime, box office, number of awards won, number of nominations, number of Oscars won, IMDb rating

--compare "compare_by" "movie_name1" "movie_name2" "movie_name3"
Printing movie that were the best in given compare argument. Available compare_by options: imdb_rating, box_office, all_wins, runtime


Test file test_movies.py is included. This file includes tests for all above commands and some scenarios of commands that are incorrect.
