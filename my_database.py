import sqlite3
import requests
import ast
import re
import os


class myDataBase():
    def __init__(self, file_name='moviesdata.sqlite'):
        self.file_name = file_name
        self.connection = sqlite3.connect(file_name)
        self.cursor = self.connection.cursor()
        self.columns = ['TITLE', 'YEAR', 'RUNTIME', 'GENRE', 'DIRECTOR', 'WRITER', 'LANGUAGE', 'COUNTRY', 'IMDb_Rating',
                        'IMDb_votes',
                        'ACTORS', 'BOX_OFFICE', 'RUNTIME', 'OSCARS_WON', 'OSCARS_NOMINATIONS', 'ALL_WINS',
                        'ALL_NOMINATIONS']
        self.create_database()

    def __del__(self):
        self.connection.close()

    def create_database(self):
        # creating database if one doesn't exist
        self.cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='MOVIES';")
        if self.cursor.fetchone() is None:
            self.cursor.execute(f"CREATE TABLE MOVIES (TITLE text)")
            self.connection.commit()
        types = ['text', 'integer', 'text', 'text', 'text', 'text', 'text', 'text', 'float',
                 'integer', 'text', 'integer', 'text', 'integer', 'integer', 'integer', 'integer']
        for column, t in zip(self.columns, types):
            try:
                self.cursor.execute(f"ALTER TABLE MOVIES ADD COLUMN {column} {t}")
            except Exception:
                pass
            self.connection.commit()

    def load_data(self, file_names):
        # loading titles from existing database and adding to this one
        for file_name in file_names:
            if not os.path.exists(file_name):
                print(f'{file_name} file not found.')
                return
            connection = sqlite3.connect(file_name)
            cursor = connection.cursor()
            cursor.execute("SELECT TITLE FROM MOVIES")
            for title in cursor.fetchall():
                self.add_movie(title[0])
            connection.close()

    def add_movie(self, movie_name):
        # adding movie by movie name
        self.cursor.execute("SELECT TITLE FROM MOVIES WHERE TITLE = ?", (movie_name,))
        if self.cursor.fetchall():
            print(f'{movie_name} already in database.')
            return
        content = self.download_content(movie_name)
        if content == 0:
            return
        self.update_movie(content)

    def download_content(self, movie_name):
        # downloading information about move from omdbapi
        try:
            response = requests.get(f'http://www.omdbapi.com/?t={movie_name}&apikey=e5714101')
        except requests.exceptions.ConnectionError:
            print('Error connecting to server.')
            return 0
        content = response.content.decode('utf-8')
        if content[0] != '{':
            print(f"API for movie: {movie_name} doesn't seem to work")
            return 0
        content = ast.literal_eval(content)
        if content.get('Error'):
            self.printError(content.get('Error'), movie_name)
            return 0
        return content

    def update_movie(self, content):
        # inserting information about movie
        self.cursor.execute(
            f"""INSERT INTO MOVIES VALUES (:Title, :Year, :Runtime, :Genre, :Director, :Writer, :Language, :Country,
             :imdbRating, :imdbVotes, :Actors, :BoxOffice, :oscarsWon, :oscarsNominations, :allWins,
              :allNominations)"""
            , self.clean_data(content))
        self.connection.commit()
        print(f"{content['Title']} added to database.")

    def clean_data(self, d):
        # cleaning downloaded data
        d.update(self.get_Awards(d['Awards'].split(' ')))
        keys = ['Title', 'Year', 'Runtime', 'Genre', 'Director', 'Actors', 'Writer', 'Language', 'Country', 'Awards',
                'Actors', 'imdbRating', 'imdbVotes', 'BoxOffice', 'oscarsWon', 'oscarsNominations', 'allWins',
                'allNominations']
        info = dict(zip(keys, [d.get(key) for key in keys]))
        for key in info:
            if info[key] == 'N/A':
                info[key] = None
        for col in ['BoxOffice', 'Year', 'imdbVotes']:
            info[col] = self.convert_to_int(info[col])
        return info

    def convert_to_int(self, num):
        if num is None:
            return num
        return int(str(re.sub(r"\D", "", num)))

    def printError(self, error, movie_name=''):
        if error == 'Movie not found!':
            print(f'{movie_name} movie not found.')
            return
        print(error)

    def get_highscores(self):
        # printing highest scores
        args = ['RUNTIME', 'BOX_OFFICE', 'ALL_WINS', 'ALL_NOMINATIONS', 'OSCARS_WON', 'IMDb_Rating']
        bests = []
        for arg in args:
            sorted = self.get_sorted(arg, title=True)
            if sorted is None:
                bests.append(['-', '-'])
                continue
            bests.append(sorted[0])
        print(f"""Longest Runtime: {bests[0][0]} min from movie: {bests[0][1]}
Best Box Office: {self.print_box_office(bests[1][0])} from movie: {bests[1][1]}
Most Awards Won: {bests[2][0]} from movie: {bests[2][1]}
Most Nominations: {bests[3][0]} from movie: {bests[3][1]}
Most Oscars Won: {bests[4][0]} from movie: {bests[4][1]}
Highest IMDb Rating: {bests[5][0]} from movie: {bests[5][1]}""")

    def get_Awards(self, awards):
        # extracting information about awards
        d = {'oscarsWon': 0, 'oscarsNominations': 0, 'allWins': 0, 'allNominations': 0}
        if awards[0] == 'N/A':
            return d
        num_of_oscars = 0
        for i, word in enumerate(awards):
            if word in ['Oscars.', 'Oscar.']:
                num_of_oscars = int(awards[i - 1])
            elif word in ['win', 'wins', 'win.', 'wins.']:
                d['allNominations'] += int(awards[i - 1])
                d['allWins'] += int(awards[i - 1])
            elif word in ['nomination', 'nominations', 'nominations.', 'nomination.']:
                d['allNominations'] += int(awards[i - 1])
        d['oscarsNominations'] += num_of_oscars
        d['allNominations'] += num_of_oscars
        if awards[0] == 'Won':
            d['allWins'] += num_of_oscars
            if num_of_oscars > 0:
                d['oscarsWon'] += num_of_oscars
        return d

    def sort_by(self, column):
        # printing sorted data
        if column.lower() == 'Title':
            sorted = self.get_sorted(column)
            if sorted is None:
                return
            for elems in sorted:
                print(f'Title: {elems[0]}')
        else:
            sorted = self.get_sorted(column, title=True)
            if sorted is None:
                return
            for elems in sorted:
                if elems[0] is None:
                    continue
                if column.lower() == 'box_office':
                    print(f'Title: {elems[1]} Box office: {self.print_box_office(elems[0])}')
                    continue
                print(f'Title: {elems[1]} {column}: {elems[0]}')

    def get_sorted(self, column, title=False, sort_type='DESC'):
        # returning sorted column
        if column.lower() not in [c.lower() for c in self.columns]:
            print(f'{column} not found in database.')
            return None
        if column.lower() == 'runtime':
            column = f'CAST({column} AS INTEGER)'
        if title and column.lower() != 'title':
            self.cursor.execute(f'SELECT {column},TITLE FROM MOVIES ORDER BY {column} {sort_type}')
        else:
            self.cursor.execute(f'SELECT {column} FROM MOVIES ORDER BY {column} {sort_type}')
        ret = self.cursor.fetchall()
        if not ret:
            return None
        return ret

    def filter_by(self, args):
        # printed filtered information
        cont = False
        for i, arg in enumerate(args):
            if cont:
                cont = False
                continue
            arg = arg.strip()
            if arg.lower() in ['director', 'actors', 'language']:
                filter_by = arg
                arg_to_filter = args[i + 1]
                self.cursor.execute(
                    f"SELECT {filter_by}, TITLE FROM MOVIES WHERE {filter_by} LIKE '%{arg_to_filter}%'")
                for elems in self.cursor.fetchall():
                    print(f'Title: {elems[1]} {arg}: {elems[0]}')
                cont = True
            elif arg.lower() == 'oscar':
                self.cursor.execute(f"SELECT TITLE FROM MOVIES WHERE OSCARS_NOMINATIONS > 0 AND OSCARS_WON = 0")
                for elems in self.cursor.fetchall():
                    print(f'Title: {elems[0]}')
            elif arg.lower() == 'over_80':
                self.cursor.execute(
                    f"SELECT TITLE,ALL_NOMINATIONS,ALL_WINS FROM MOVIES WHERE ALL_WINS/ALL_NOMINATIONS >= 0.8")
                for elems in self.cursor.fetchall():
                    print(f'Title: {elems[0]}. {elems[1]} nomination(s) and {elems[2]} win(s)')
            elif arg.lower() == 'over_100_mil':
                self.cursor.execute(
                    f"SELECT TITLE,BOX_OFFICE FROM MOVIES WHERE BOX_OFFICE>=100000000")
                for elems in self.cursor.fetchall():
                    print(f'Title: {elems[0]}. Box office: {self.print_box_office(elems[1])}')
            else:
                print(f'{arg} is invalid argument.')

    def print_box_office(self, box_office):
        # printing box office in proper format
        if box_office is None:
            return None
        s = []
        for i in range(1, len(str(box_office)) + 1):
            s.insert(0, str(box_office)[-i])
            if i % 3 == 0 and i != len(str(box_office)):
                s.insert(0, ',')
        s.append('$')
        return ''.join(s)

    def compare_by(self, args):
        # printing compared movies
        compare = args[0]
        results = []
        for movie_name in args[1:]:
            self.cursor.execute(f"SELECT TITLE,{compare} FROM MOVIES WHERE TITLE = '{movie_name}'")
            results.append(self.cursor.fetchone())
            if results[-1] is None:
                print(f'{movie_name} not found in database.')
                return
            if results[-1][1] is None:
                print(f'No information about {compare} for movie {movie_name} in database.')
                return
        best_movie = results[0][0]
        best_result = results[0][1]
        for result in results[1:]:
            if result[1] > best_result:
                best_result = result[1]
                best_movie = result[0]
        if compare.lower() == 'box_office':
            best_result = self.print_box_office(best_result)
        print(f"Best {compare}: {best_result}. Movie: {best_movie}")
