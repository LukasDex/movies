import movies
import os
from shutil import copyfile


def setup_module():
    # creating temporary copy of database to work on
    copyfile('tests/test_data.sqlite', 'tests/test_data_temp.sqlite')


def create_command(args):
    movies.create_commands_list(['--set_file_name', 'tests/test_data_temp.sqlite'] + args)


def test_sort_by(capsys):
    columns = ['YEAR', 'RUNTIME', 'GENRE', 'DIRECTOR', 'WRITER', 'LANGUAGE', 'COUNTRY', 'IMDb_Rating',
               'IMDb_votes',
               'ACTORS', 'BOX_OFFICE', 'OSCARS_WON', 'OSCARS_NOMINATIONS', 'ALL_WINS', 'ALL_NOMINATIONS']
    predicted_outputs = []
    with open('tests/sort.csv') as data:
        output = ''
        for i, line in enumerate(data):
            if (i in range(1, 41) and i % 4 == 0) or i in [42, 46, 50, 54]:
                predicted_outputs.append(output)
                output = ''
            output += line
        predicted_outputs.append(output + '\n')

    # testing outputs for every column
    for i, column in enumerate(columns):
        create_command(['--sort_by', column])
        captured = capsys.readouterr()
        assert captured.out == predicted_outputs[i]

    # testing output for not existing column
    create_command(['--sort_by', 'notexistedcolumn'])
    captured = capsys.readouterr()
    assert captured.out == 'notexistedcolumn not found in database.\n'


def test_filter_by(capsys):
    options = ['director', 'actors', 'language', 'oscar', 'over_80', 'over_100_mil']
    args = [['Innes'], ['Chris'], ['Russian'], [], [], []]
    outputs = ["Title: Shazam director: Royston Innes\n",
               "Title: The Avengers actors: Robert Downey Jr., Chris Evans, Mark Ruffalo, Chris Hemsworth\n\
Title: Shazam actors: Roman Dior Degeddingseze, Christopher Mychael Watson\n",
               "Title: The Avengers language: English, Russian, Hindi\n",
               "Title: The Avengers\n\
Title: Trainspotting\n",
               "",
               "Title: The Avengers. Box office: 623,279,547$\n"]
    for arg, option, output in zip(args, options, outputs):
        create_command(['--filter_by', option] + arg)
        captured = capsys.readouterr()
        assert captured.out == output

    create_command(['--filter_by', 'invalidinput'])
    captured = capsys.readouterr()
    assert captured.out == "invalidinput is invalid argument.\n"

    # multiple arguments
    create_command(['--filter_by', 'language', 'English', 'over_100_mil'])
    captured = capsys.readouterr()
    assert captured.out == "Title: The Avengers language: English, Russian, Hindi\n\
Title: Room language: English\n\
Title: Shazam language: English\n\
Title: Trainspotting language: English\n\
Title: The Avengers. Box office: 623,279,547$\n"

    # no elements found
    create_command(['--filter_by', 'language', 'notexistinglanguage'])
    captured = capsys.readouterr()
    assert captured.out == ""


def test_compare(capsys):
    # comparing by every column
    options = ['IMDb_Rating', 'Box_office', 'all_wins', 'runtime']
    for option in options:
        create_command(['--compare', option, 'Room', 'The Avengers'])
    captured = capsys.readouterr()
    assert captured.out == "Best IMDb_Rating: 8.2. Movie: Room\n\
Best Box_office: 623,279,547$. Movie: The Avengers\n\
Best all_wins: 104. Movie: Room\n\
Best runtime: 143 min. Movie: The Avengers\n"

    # comparing movies that doesn't exists
    create_command(['--compare', 'all_wins', 'movie1', 'movie2'])
    captured = capsys.readouterr()
    assert captured.out == "movie1 not found in database.\n"

    # comparing movies where one doesn't have information about box_office
    create_command(['--compare', 'Box_office', 'Room', 'Trainspotting'])
    captured = capsys.readouterr()
    assert captured.out == "No information about Box_office for movie Trainspotting in database.\n"


def test_adding_movies(capsys):
    # trying to add movie that doesn't exist
    movie_name = 'wrongmoviename'
    create_command(['--add', movie_name])
    captured = capsys.readouterr()
    assert captured.out == "wrongmoviename movie not found.\n"

    # trying to add movie that does exist and not in database
    create_command(['--add', 'The Thing'])
    captured = capsys.readouterr()
    assert captured.out == "The Thing added to database.\n"

    # trying to add movie that does exist and is already in database
    create_command(['--add', 'The Thing'])
    captured = capsys.readouterr()
    assert captured.out == "The Thing already in database.\n"

    # adding multiple movies
    create_command(['--add', 'The Avengers', 'Guardians of the Galaxy Vol. 2', 'Guardians of the Galaxy'])
    captured = capsys.readouterr()
    assert captured.out == "The Avengers already in database.\nGuardians of the Galaxy Vol." \
                           " 2 added to database.\nGuardians of the Galaxy added to database.\n"


def test_highscores(capsys):
    create_command(['--highscores'])
    captured = capsys.readouterr()
    assert captured.out == "Longest Runtime: 143 min from movie: The Avengers\n\
Best Box Office: 623,279,547$ from movie: The Avengers\n\
Most Awards Won: 104 from movie: Room\n\
Most Nominations: 240 from movie: Room\n\
Most Oscars Won: 1 from movie: Room\n\
Highest IMDb Rating: 8.3 from movie: Shazam\n"

    # printing highscores from empty database
    movies.create_commands_list(['--set_file_name', 'tests/test_data2.sqlite', '--highscores'])
    captured = capsys.readouterr()
    assert captured.out == "Longest Runtime: - min from movie: -\n\
Best Box Office: -$ from movie: -\n\
Most Awards Won: - from movie: -\n\
Most Nominations: - from movie: -\n\
Most Oscars Won: - from movie: -\n\
Highest IMDb Rating: - from movie: -\n"
    os.remove('tests/test_data2.sqlite')


def test_load_data(capsys):
    # adding movies to database from other file
    create_command(['--load_data', 'tests/load_test.sqlite'])
    capsys.readouterr()

    # highscores with added movies
    create_command(['--highscores'])
    captured = capsys.readouterr()
    assert captured.out == "Longest Runtime: 207 min from movie: Seven Samurai\n\
Best Box Office: 623,279,547$ from movie: The Avengers\n\
Most Awards Won: 154 from movie: The Dark Knight\n\
Most Nominations: 309 from movie: The Dark Knight\n\
Most Oscars Won: 3 from movie: Jurassic Park\n\
Highest IMDb Rating: 9.0 from movie: The Dark Knight\n"

    # loading from not existing file
    create_command(['--load_data', 'notexisting'])
    captured = capsys.readouterr()
    assert captured.out == "notexisting file not found.\n"


def test_other(capsys):
    # command that doesn't exist
    create_command(['--wrongcommand'])
    captured = capsys.readouterr()
    assert captured.out == "wrongcommand command not found.\n"


def teardown_module():
    # removing temporary database
    os.remove('tests/test_data_temp.sqlite')
