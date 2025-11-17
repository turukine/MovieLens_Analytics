from collections import defaultdict
from bs4 import BeautifulSoup
import requests
import datetime
import pytest
import re


class Ratings:
    """
    Analyzing data from ratings.csv
    """
    def __init__(self, path_to_ratings, path_to_movies):
        """
        Put here any fields that you think you will need.
        """
        self.path_to_ratings = path_to_ratings
        self.path_to_movies = path_to_movies
        self.data = [] 

        self._load_data()
        self._load2_and_merge_on_movieid()

    def _load_data(self):

        with open(self.path_to_ratings, 'r') as file:
            headers = file.readline().strip().split(',')
            for line in file:
                if not line.strip():
                    continue
                values = line.strip().split(',')
                row = dict(zip(headers, values))
                self.data.append(row)
    
    def _load2_and_merge_on_movieid(self):

        dict_movie = defaultdict(dict)
        with open(self.path_to_movies, 'r') as file:
            headers = file.readline().strip().split(',')
            for line in file:
                if not line.strip():
                    continue
                values = line.strip().split(',')
                movie_id = values[0]
                dict_movie[movie_id] = dict(zip(headers, values))

        for rating in self.data:
            movie_id = rating['movieId']
            if movie_id in dict_movie:
                for key, val in dict_movie[movie_id].items():
                    if key != 'movieId':
                        rating[key] = val
            else:
                print(f"Warning: movieId {movie_id} not found in movies.csv")

    class Movies:    
        def __init__(self, data):
            self.data = data
            self.start_date = datetime.datetime.strptime('1970-01-01', "%Y-%m-%d")

        def dist_by_year(self):
            """
            The method returns a dict where the keys are years and the values are counts. 
            Sort it by years ascendingly. You need to extract years from timestamps.
            """
            ratings_by_year = defaultdict(int)
            for line in self.data:
                year = (self.start_date + datetime.timedelta(seconds=int(line['timestamp']))).year
                ratings_by_year[year] += 1

            return dict(sorted(ratings_by_year.items()))

        def dist_by_rating(self):
            """
            The method returns a dict where the keys are ratings and the values are counts.
            Sort it by ratings ascendingly.
            """
            ratings_distribution = defaultdict(int)
            
            for line in self.data:
                rating = float(line['rating'])
                ratings_distribution[rating] += 1

            return dict(sorted(ratings_distribution.items()))
        
        def top_by_num_of_ratings(self, n=10):
            """
            The method returns top-n movies by the number of ratings. 
            It is a dict where the keys are movie titles and the values are numbers.
            Sort it by numbers descendingly.
            """
            if not isinstance(n, int) or n < 1 :
                return "Неверное значение n"
            
            top_movies = defaultdict(int)

            for line in self.data:
                title = line['title']
                top_movies[title] += 1

            return dict(sorted(top_movies.items(), key=lambda item: item[1], reverse=True)[:n])

        def top_by_ratings(self, n=10, metric='average'):
            """
            The method returns top-n movies by the average or median of the ratings.
            It is a dict where the keys are movie titles and the values are metric values.
            Sort it by metric descendingly.
            The values should be rounded to 2 decimals.
            """
            if not isinstance(n, int) or n < 1 :
                return "Неверное значение n"
            
            top_movies  = defaultdict(list)

            for line in self.data:
                title = line['title']
                rating = line['rating']
                top_movies[title].append(float(rating))

            if metric == 'average':
                for key, value in top_movies.items():
                    top_movies[key] = round((sum(value)/len(value)), 2)

            if metric == 'median':
                for key, value in top_movies.items():
                    sorted_data = sorted(value)  
                    k = len(sorted_data)  
                    mid = k // 2
                    if len(value) % 2 == 0:
                        top_movies[key] = (sorted_data[mid - 1] + sorted_data[mid]) / 2 

                    else:
                        top_movies[key] = (sorted_data[mid])

            return dict(sorted(top_movies.items(), key=lambda item: item[1], reverse=True)[:n])
        
        def top_controversial(self, n=10):
            """
            The method returns top-n movies by the variance of the ratings.
            It is a dict where the keys are movie titles and the values are the variances.
          Sort it by variance descendingly.
            The values should be rounded to 2 decimals.
            """

            if not isinstance(n, int) or n < 1 :
                return "Неверное значение n"
            
            top_movies  = defaultdict(list)

            for line in self.data:
                title = line['title']
                rating = line['rating']
                top_movies[title].append(float(rating))

            for key, value in top_movies.items():
                k = len(value)  
                if k > 0:
                    mean = sum(value) / k  
                    top_movies[key] = round((sum((x - mean) **2 for x in value) / k), 2)

            return dict(sorted(top_movies.items(), key=lambda item: item[1], reverse=True)[:n])

    class Users(Movies):     

        """
        In this class, three methods should work. 
        The 1st returns the distribution of users by the number of ratings made by them.
        The 2nd returns the distribution of users by average or median ratings made by them.
        The 3rd returns top-n users with the biggest variance of their ratings.
        Inherit from the class Movies. Several methods are similar to the methods from it.
        """

        def top_by_num_of_ratings(self, n=10):
            '''
            The 1st returns the distribution of users by the number of ratings made by them.
            '''
            if not isinstance(n, int) or n < 1 :
                return "Неверное значение n"
            
            top_ratings = defaultdict(int)
            for line in self.data:
                user_id = line['userId']
                top_ratings[user_id] += 1
            
            return dict(sorted(top_ratings.items(), key=lambda item: item[1], reverse=True)[:n])
        
        def top_by_ratings(self, n=10, metric='average'):
            """
            The 2nd returns the distribution of users by average or median ratings made by them.
            """
            if not isinstance(n, int) or n < 1 :
                return "Неверное значение n"
            
            top_ratings  = defaultdict(list)

            for line in self.data:
                user_id = line['userId']
                rating = line['rating']
                top_ratings[user_id].append(float(rating))

            if metric == 'average':
                for key, value in top_ratings.items():
                    top_ratings[key] = round((sum(value)/len(value)), 2)

            if metric == 'median':
                for key, value in top_ratings.items():
                    sorted_data = sorted(value)  
                    k = len(sorted_data)  
                    mid = k // 2
                    if len(value) % 2 == 0:
                        top_ratings[key] = (sorted_data[mid - 1] + sorted_data[mid]) / 2 

                    else:
                        top_ratings[key] = (sorted_data[mid])

            return dict(sorted(top_ratings.items(), key=lambda item: item[1], reverse=True)[:n])

        def top_controversial(self, n=10):
            """
            The 3rd returns top-n users with the biggest variance of their ratings.
            """

            if not isinstance(n, int) or n < 1 :
                return "Неверное значение n"
            
            top_movies  = defaultdict(list)

            for line in self.data:
                user_id = line['userId']
                rating = line['rating']
                top_movies[user_id].append(float(rating))

            for key, value in top_movies.items():
                k = len(value)  
                if k > 0:
                    mean = sum(value) / k  
                    top_movies[key] = round((sum((x - mean) **2 for x in value) / k), 2)

            return dict(sorted(top_movies.items(), key=lambda item: item[1], reverse=True)[:n])

class Movies:
    """
    Analyzing data from movies.csv
    """

    def __init__(self, path_to_the_file):
        """
        Put here any fields that you think you will need.
        """   
        self.data = []
        with open(path_to_the_file, 'r') as file:
            lines = file.readlines()
        
        headers = lines[0].strip().split(',')
        for line in lines[1:]:
            values = self.parse_line(line)
            movie = {}
            for i in range(len(headers)):
                if i < len(values):
                    movie[headers[i]] = values[i]
                else:
                    movie[headers[i]] = "" 
            self.data.append(movie)  

    def get_all(self):
        """
        Returns the full list of movies from the dataset.
        This method gives access to all loaded movie records as a list of dictionaries.
        """
        return self.data

    def extract_year(self, title):
        """
        Extracts the release year from the movie title.
        """
        if '(' in title and ')' in title:
                parts = title.split('(')
                mb_year = parts[-1].strip(')')
                if len(mb_year) == 4 and mb_year.isdigit():
                    return mb_year
        return 'unknown year' 

    def dist_by_release(self):
        """
        The method returns a dict or an OrderedDict where the keys are years and the values are counts. 
        You need to extract years from the titles. Sort it by counts descendingly.
        """
        release_years = defaultdict(int)
        for movie in self.data:
            year = self.extract_year(movie["title"])
            release_years[year] += 1
    
        sorted_years = dict(sorted(release_years.items(), key=lambda x: x[1], reverse=True))
        return sorted_years 
    

    def parse_line(self, line):
        result = []
        current = ""
        in_quotes = False  

        for char in line:
            if char == '"':
                in_quotes = not in_quotes 
                current += char
            elif char == ',' and not in_quotes:
                result.append(current.strip())
                current = ""
            else:
                current += char

        result.append(current.strip())  
        return result


    def dist_by_genres(self):
        """
        The method returns a dict where the keys are genres and the values are counts.
        Sort it by counts descendingly.
        """
        genres_count = defaultdict(int)

        for movie in self.data:
            genres = movie["genres"].split('|')
            for genre in genres:
                genre = genre.strip()

                if '(' in genre or ')' in genre or 'http' in genre or ':' in genre or '"' in genre:
                    continue
                if not genre or genre == "(no genres listed)":
                    continue

                genres_count[genre] += 1
        
        sorted_genres = dict(sorted(genres_count.items(), key=lambda x: x[1], reverse=True))
        return sorted_genres
    
    def most_genres(self, n):
        """
        The method returns a dict with top-n movies where the keys are movie titles and 
        the values are the number of genres of the movie. Sort it by numbers descendingly.
        """
        movie_genres_c = {}
        for movie in self.data:
            genres = movie['genres'].split('|')
            movie_genres_c[movie['title']] = len(genres)

        top_movies = dict(sorted(movie_genres_c.items(), key=lambda x: x[1], reverse=True)[:n] )
        return top_movies

class Links:
    """
    Analyzing data from links.csv
    """
    def __init__(self, path_to_the_file):
        """
        Put here any fields that you think you will need.
        """
        with open(path_to_the_file, 'r') as file:
            self.imdb_links = {}
            self.tmdb_links = {}
            self.movie_ids = set()
            self.titles = {}
            for line in file:
                parts = line.strip().split(',')
                if len(parts) != 3 or not(parts[0].isdigit()):
                    continue
                movie_id = int(parts[0])
                self.imdb_links[movie_id] = 'https://www.imdb.com/title/tt' + parts[1] + '/'
                self.tmdb_links[movie_id] = 'https://www.themoviedb.org/movie/' + parts[2]
                self.movie_ids.add(movie_id)

        movies_file = path_to_the_file.replace('links.csv', 'movies.csv')
        with open(movies_file, 'r') as file:
            for line in file:
                pattern = re.compile(r'^(\d+),((?:"[^"]+")|(?:[^,]+)),(.*)$')
                parts = pattern.match(line.strip())
                if not parts:
                  continue
                if len(parts.groups()) != 3 or not parts.group(1).isdigit(): continue
                movie_id = int(parts.group(1))
                title = re.compile(r'(.+?)\s\((\d{4})\)').search(parts.group(2))
                self.titles[movie_id] = title.group(1).strip('"') if title else 'Unknown'
    
    def get_imdb(self, list_of_movies: list, list_of_fields: list):
        """
        The method returns a list of lists [movieId, field1, field2, field3, ...] for the list of movies given as the argument (movieId).
        For example, [movieId, Director, Budget, Cumulative Worldwide Gross, Runtime].
        The values should be parsed from the IMDB webpages of the movies.
        Sort it by movieId descendingly.
        """
        headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'}
        imdb_info = []

        for movie_id in list_of_movies:
            if movie_id in self.imdb_links:
                imdb_url = self.imdb_links[movie_id]

                try:
                    response = requests.get(imdb_url, headers=headers, timeout=10)
                    if response.status_code == 404:
                        raise ValueError(f"Movie ID {movie_id} not found on IMDb.")
                    elif response.status_code != 200:
                        raise ValueError(f"Failed to retrieve data for movie ID {movie_id}. Status code: {response.status_code}")
                    response.raise_for_status()
                    soup = BeautifulSoup(response.text, 'html.parser')
                    movie_data = [movie_id]

                    for field in list_of_fields:
                        if field == 'Title':
                            title = self.titles[movie_id]
                            movie_data.append(title)
                        elif field == 'Release Date':
                            date = soup.find('li', {'data-testid': "title-details-releasedate"}).find('ul')
                            movie_data.append((date.text) if date else 'N/A')
                        elif field == 'Rating':
                            rating = soup.find('div', {'data-testid': "hero-rating-bar__aggregate-rating__score"}).find('span')
                            movie_data.append(float(rating.text) if rating else 'N/A')
                        elif field == 'Director':
                            director = soup.find('a', {'href': re.compile(r'/name/nm\d+')})
                            movie_data.append(director.text if director else 'N/A')
                        elif field == 'Budget':
                            budget_block = soup.find('li', {'data-testid':"title-boxoffice-budget"})
                            if budget_block:
                                budget = budget_block.find('span', string=re.compile(r'\$\d+'))
                                movie_data.append(int(''.join([c for c in budget.text if c.isdigit()])) if budget else 'N/A')
                            else: movie_data.append('N/A')
                        elif field == 'Cumulative Worldwide Gross':
                            gross_block = soup.find('li', {'data-testid': "title-boxoffice-cumulativeworldwidegross"})
                            if gross_block:
                                gross = gross_block.find('span', string=re.compile(r'\$\d+'))
                                movie_data.append(int(''.join([c for c in gross.text if c.isdigit()])) if gross else 'N/A')
                            else: movie_data.append('N/A')
                        elif field == 'Runtime':
                            runtime_block = soup.find('li', {'data-testid': "title-techspec_runtime"})
                            runtime = runtime_block.find('div')
                            runtime = list(map(int, re.findall(r'\d+', runtime.text)) if runtime else (0, 0))
                            if len(runtime) == 1:
                                hours, minutes = 0, runtime[0]
                            elif len(runtime) == 2:
                                hours, minutes = runtime
                            else:
                                hours, minutes = 0, 0
                            minutes = hours * 60 + minutes
                            movie_data.append(minutes if runtime else 'N/A')
                        else:
                            movie_data.append('Unknown')                    
                    imdb_info.append(movie_data)
                except Exception as e:
                    print(f"Error fetching data for movie ID {movie_id}: {e}")

        imdb_info.sort(key=lambda x: x[0], reverse=True)
        return imdb_info

    def get_tmdb(self, list_of_movies: list, list_of_fields: list):
        """
        The method returns a list of lists [movieId, field1, field2, field3, ...] for the list of movies given as the argument (movieId).
        For example, [movieId, Director, Budget, Cumulative Worldwide Gross, Runtime].
        The values parsed from the TMDB webpages of the movies.
        Sorted by movieId descendingly.
        """
        headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'}
        tmdb_info = []

        for movie_id in list_of_movies:
            if movie_id in self.tmdb_links:
                tmdb_url = self.tmdb_links[movie_id]

                try:
                    response = requests.get(tmdb_url, headers=headers, timeout=10)
                    if response.status_code == 404:
                        raise ValueError(f"Movie ID {movie_id} not found on TMDB.")
                    elif response.status_code != 200:
                        raise ValueError(f"Failed to retrieve data for movie ID {movie_id}. Status code: {response.status_code}")
                    response.raise_for_status()
                    soup = BeautifulSoup(response.text, 'html.parser')
                    movie_data = [movie_id]

                    for field in list_of_fields:
                        if field == 'Title':
                            title = self.titles[movie_id]
                            movie_data.append(title if title else 'N/A')
                        elif field == 'Release Date':
                            date = soup.find('span', {'class': 'release'})
                            movie_data.append(date.text.strip() if date else 'N/A')
                        elif field == 'Genres':
                            genres = soup.find_all('a', {'href': re.compile(r'/genre/\d+')})
                            movie_data.append(', '.join(genre.text for genre in genres) if genres else 'N/A')
                        elif field == 'Director':
                            profile_blocks = soup.find_all('li', class_='profile')
                            for block in profile_blocks:
                                role_tag = block.find('p', class_='character', string='Director')
                                if role_tag:
                                    director_tag = block.find('a')
                                    break
                            movie_data.append(director_tag.text.strip() if director_tag else 'N/A')
                        elif field == 'Cast':
                            cast = soup.find('div', {'id': "cast_scroller"})
                            cast = cast.find_all('a', {'href': re.compile(r'/person/\d+')})
                            cast_list = [actor.text.strip() for actor in cast[1::2]]
                            movie_data.append(', '.join(cast_list[:3]) if cast_list else 'N/A')
                        elif field == 'Budget':
                            budget_block = soup.find('strong', string=re.compile(r'Budget'))
                            find_sib = str(budget_block.next_sibling) if budget_block else None
                            budget = re.search(r'\$([\d,]+)', find_sib) if find_sib else None
                            movie_data.append(int(budget.group(1).replace(',', '')) if budget else 'N/A')
                        elif field == 'Cumulative Worldwide Gross':
                            gross_block = soup.find('strong', string=re.compile(r'Revenue'))
                            find_sib = str(gross_block.next_sibling) if gross_block else None
                            gross = re.search(r'\$([\d,]+)', find_sib) if find_sib else None
                            movie_data.append(int(gross.group(1).replace(',', '')) if gross else 'N/A')
                        elif field == 'Runtime':
                            runtime_block = soup.find('span', {'class': 'runtime'})
                            runtime = list(map(int, re.findall(r'\d+', runtime_block.text)) if runtime_block else (0, 0))
                            if len(runtime) == 1:
                                hours, minutes = 0, runtime[0]
                            elif len(runtime) == 2:
                                hours, minutes = runtime
                            else:
                                hours, minutes = 0, 0
                            total_minutes = hours * 60 + minutes
                            movie_data.append(total_minutes)
                        else:
                            movie_data.append('Unknown')
                    tmdb_info.append(movie_data)
                except Exception as e:
                    print(f"Error fetching data for movie ID {movie_id}: {e}")
        tmdb_info.sort(key=lambda x: x[0], reverse=True)
        return tmdb_info

    def top_directors(self, n):
        """
        The method returns a dict with top-n directors where the keys are directors and 
        the values are numbers of movies created by them. Sort it by numbers descendingly.
        """
        directors = {}
        
        for movie_id in list(self.movie_ids)[:25]:
            if movie_id in self.imdb_links:
                imdb_url = self.imdb_links[movie_id]
                try:
                    director = self.get_imdb([movie_id], ['Director'])
                    if director:
                        director_name = director[0][1]
                        if director_name in directors:
                            directors[director_name] += 1
                        else:
                            directors[director_name] = 1
                except Exception as e:
                    print(f"Error fetching director for movie ID {movie_id}: {e}")

        directors = dict(sorted(directors.items(), key=lambda item: item[1], reverse=True)[:n])
        return directors
        
    def most_expensive(self, n):
        """
        The method returns a dict with top-n movies where the keys are movie titles and
        the values are their budgets. Sort it by budgets descendingly.
        """
        budgets = {}

        for movie_id in list(self.movie_ids)[:25]:
            if movie_id in self.imdb_links:
                imdb_url = self.imdb_links[movie_id]
                try:
                    budget = self.get_imdb([movie_id], ['Title', 'Budget'])
                    if budget and budget[0][2] != 'N/A':
                        budgets[budget[0][1]] = int(budget[0][2])
                except Exception as e:
                    print(f"Error fetching budget for movie ID {movie_id}: {e}")
        budgets = dict(sorted(budgets.items(), key=lambda item: item[1], reverse=True)[:n])
        return budgets
        
    def most_profitable(self, n):
        """
        The method returns a dict with top-n movies where the keys are movie titles and
        the values are the difference between cumulative worldwide gross and budget.
        Sort it by the difference descendingly.
        """
        profits = {}

        for movie_id in list(self.movie_ids)[:25]:
            if movie_id in self.imdb_links:
                imdb_url = self.imdb_links[movie_id]
                try:
                    profit_data = self.get_imdb([movie_id], ['Title', 'Budget', 'Cumulative Worldwide Gross'])
                    if profit_data and profit_data[0][2] != 'N/A' and profit_data[0][3] != 'N/A':
                        budget = int(profit_data[0][2])
                        gross = int(profit_data[0][3])
                        profits[profit_data[0][1]] = gross - budget
                    else:
                        profits[profit_data[0][1]] = 0
                except Exception as e:
                    print(f"Error fetching profit for movie ID {movie_id}: {e}")
        profits = dict(sorted(profits.items(), key=lambda item: item[1], reverse=True)[:n])
        return profits

    def longest(self, n):
        """
        The method returns a dict with top-n movies where the keys are movie titles and
        the values are their runtime. If there are more than one version – choose any.
        Sort it by runtime descendingly.
        """
        runtimes = {}

        for movie_id in list(self.movie_ids)[:25]:
            if movie_id in self.imdb_links:
                imdb_url = self.imdb_links[movie_id]
                try:
                    runtime_data = self.get_imdb([movie_id], ['Title', 'Runtime'])
                    if runtime_data and runtime_data[0][2] != 'N/A':
                        title = runtime_data[0][1]
                        total_minutes = runtime_data[0][2]
                        runtimes[title] = total_minutes
                except Exception as e:
                    print(f"Error fetching runtime for movie ID {movie_id}: {e}")
        runtimes = dict(sorted(runtimes.items(), key=lambda item: item[1], reverse=True)[:n])
        return runtimes
        
    def top_cost_per_minute(self, n):
        """
        The method returns a dict with top-n movies where the keys are movie titles and
        the values are the budgets divided by their runtime. The budgets can be in different currencies – do not pay attention to it. 
        The values should be rounded to 2 decimals. Sort it by the division descendingly.
        """
        costs = {}

        for movie_id in list(self.movie_ids)[:25]:
            if movie_id in self.imdb_links:
                imdb_url = self.imdb_links[movie_id]
                try:
                    cost_data = self.get_imdb([movie_id], ['Title', 'Budget', 'Runtime'])
                    if cost_data and cost_data[0][2] != 'N/A' and cost_data[0][3] != 'N/A':
                        title = cost_data[0][1]
                        budget = int(cost_data[0][2])
                        total_minutes = cost_data[0][3]
                        if total_minutes > 0:
                            costs[title] = round(budget / total_minutes, 2)
                except Exception as e:
                    print(f"Error fetching cost per minute for movie ID {movie_id}: {e}")
        costs = dict(sorted(costs.items(), key=lambda item: item[1], reverse=True)[:n])
        return costs

class Tags:
    """
    Analyzing data from tags.csv
    """
    def __init__(self, path_to_the_file):
        """
        Put here any fields that you think you will need.
        """
        self.userIDs = set()
        self.movieIDs = set()
        self.tags = {}
        self.timestamps = {}
        with open(path_to_the_file, 'r') as file:
            for line in file:
                parts = line.strip().split(',')
                if len(parts) != 4 or not(parts[0].isdigit()) or not(parts[1].isdigit()):
                    continue
                user_id = int(parts[0])
                movie_id = int(parts[1])
                tag = parts[2].strip()
                timestamp = parts[3].strip()
                
                self.userIDs.add(user_id)
                self.movieIDs.add(movie_id)
                
                if tag not in self.tags:
                    self.tags[tag] = {'count': 0, 'users': set(), 'movies': set()}
                
                self.tags[tag]['count'] += 1
                self.tags[tag]['users'].add(user_id)
                self.tags[tag]['movies'].add(movie_id)

    def most_words(self, n):
        """
        The method returns top-n tags with most words inside. It is a dict 
        where the keys are tags and the values are the number of words inside the tag.
        Drop the duplicates. Sort it by numbers descendingly.
        """
        big_tags = {tag: len(tag.split()) for tag in self.tags}
        big_tags = dict(sorted(big_tags.items(), key=lambda item: item[1], reverse=True)[:n])
        return big_tags

    def longest(self, n):
        """
        The method returns top-n longest tags in terms of the number of characters.
        It is a list of the tags. Drop the duplicates. Sort it by numbers descendingly.
        """
        big_tags = sorted(self.tags.keys(), key=lambda tag: len(tag), reverse=True)[:n]
        return big_tags

    def most_words_and_longest(self, n):
        """
        The method returns the intersection between top-n tags with most words inside and 
        top-n longest tags in terms of the number of characters.
        Drop the duplicates. It is a list of the tags.
        """
        big_tags = self.most_words(n)
        longest_tags = self.longest(n)
        big_tags = set(big_tags.keys()).intersection(set(longest_tags))
        return big_tags

    def most_popular(self, n):
        """
        The method returns the most popular tags. 
        It is a dict where the keys are tags and the values are the counts.
        Drop the duplicates. Sort it by counts descendingly.
        """
        popular_tags = {tag: data['count'] for tag, data in self.tags.items()}
        popular_tags = dict(sorted(popular_tags.items(), key=lambda item: item[1], reverse=True)[:n])
        return popular_tags

    def tags_with(self, word):
        """
        The method returns all unique tags that include the word given as the argument.
        Drop the duplicates. It is a list of the tags. Sort it by tag names alphabetically.
        """
        tags_with_word = sorted(set([tag for tag in self.tags if word.lower() in tag.lower()]))
        return tags_with_word


@pytest.fixture(scope="session")
def ratings_instance():
    return Ratings('../datasets/ratings.csv', '../datasets/movies.csv') # PATH TO DATASETS

@pytest.fixture(scope="session")
def movies_instance(ratings_instance):
    return ratings_instance.Movies(ratings_instance.data)

@pytest.fixture(scope="session")
def users_instance(ratings_instance):
    return ratings_instance.Users(ratings_instance.data)

@pytest.fixture(scope="session")
def n_value_fixture():
    n = 5
    return n

@pytest.fixture(scope="session")
def links_instance():
    return Links('../datasets/links.csv')

@pytest.fixture(scope="session")
def tags_instance():
    return Tags('../datasets/tags.csv')

class Tests:
    def test_ratings(self, ratings_instance):
        ratings = ratings_instance
        assert isinstance(ratings.data, list)
        assert len(ratings.data) > 0
        required_fields = {'userId', 'movieId', 'rating', 'timestamp', 'title', 'genres'}
        for item in ratings.data:
            assert isinstance(item, dict)
            assert required_fields.issubset(item.keys())

    def test_movies(self, movies_instance):
        movies = movies_instance
        assert isinstance(movies.data, list)
        assert len(movies.data) > 0
        required_fields = {'userId', 'movieId', 'rating', 'timestamp', 'title', 'genres'}
        for item in movies.data:
            assert isinstance(item, dict)
            assert required_fields.issubset(item.keys())
        
    def test_dist_by_year(self, movies_instance):
        movies = movies_instance
        func = movies.dist_by_year()
        assert isinstance(func, dict)
        assert all(isinstance(key, int) for key in func.keys())
        assert all(isinstance(value, int) for value in func.values())
        assert list(func.keys()) == sorted(func.keys())

    def test_dist_by_rating(self, movies_instance):
        movies = movies_instance
        func = movies.dist_by_rating()
        assert isinstance(func, dict)
        assert all(isinstance(key, float) for key in func.keys())
        assert all(isinstance(value, int) for value in func.values())
        assert list(func.keys()) == sorted(func.keys())
    
    def test_top_by_num_of_ratings(self, movies_instance, n_value_fixture):
        movies = movies_instance
        func = movies.top_by_num_of_ratings(n_value_fixture)
        assert isinstance(func, dict)
        assert all(isinstance(key, str) for key in func.keys())
        assert all(isinstance(value, int) for value in func.values())
        assert list(func.values()) == sorted(func.values(),reverse=True)
    
    def test_top_by_ratings(self, movies_instance, n_value_fixture):
        movies = movies_instance
        func_1 = movies.top_by_ratings(n=n_value_fixture, metric='average')
        func_2 = movies.top_by_ratings(n=n_value_fixture, metric='median')
        assert isinstance(func_1, dict)
        assert all(isinstance(key, str) for key in func_1.keys())
        assert all(isinstance(value, float) for value in func_1.values())
        assert list(func_1.values()) == sorted(func_1.values(),reverse=True)

        assert isinstance(func_2, dict)
        assert all(isinstance(key, str) for key in func_2.keys())
        assert all(isinstance(value, float) for value in func_2.values())
        assert list(func_2.values()) == sorted(func_2.values(),reverse=True)

    def test_top_controversial(self, movies_instance, n_value_fixture):
        movies = movies_instance
        func = movies.top_controversial(n=n_value_fixture)
        assert isinstance(func, dict)
        assert all(isinstance(key, str) for key in func.keys())
        assert all(isinstance(value, float) for value in func.values())
        assert list(func.values()) == sorted(func.values(),reverse=True)

    def test_users(self, users_instance):
        users = users_instance
        assert isinstance(users.data, list)
        assert len(users.data) > 0
        required_fields = {'userId', 'movieId', 'rating', 'timestamp', 'title', 'genres'}
        for item in users.data:
            assert isinstance(item, dict)
            assert required_fields.issubset(item.keys())

    def test_users_top_by_num_of_ratings(self, users_instance, n_value_fixture):
        users = users_instance
        func = users.top_by_num_of_ratings(n_value_fixture)
        assert isinstance(func, dict)
        assert all(isinstance(key, str) for key in func.keys())
        assert all(isinstance(value, int) for value in func.values())
        assert list(func.values()) == sorted(func.values(),reverse=True)
    
    def test_users_top_by_ratings(self, users_instance, n_value_fixture):
        users = users_instance
        func_1 = users.top_by_ratings(n=n_value_fixture, metric='average')
        func_2 = users.top_by_ratings(n=n_value_fixture, metric='median')
        assert isinstance(func_1, dict)
        assert all(isinstance(key, str) for key in func_1.keys())
        assert all(isinstance(value, float) for value in func_1.values())
        assert list(func_1.values()) == sorted(func_1.values(),reverse=True)

        assert isinstance(func_2, dict)
        assert all(isinstance(key, str) for key in func_2.keys())
        assert all(isinstance(value, float) for value in func_2.values())
        assert list(func_2.values()) == sorted(func_2.values(),reverse=True)

    def test_users_top_controversial(self, users_instance, n_value_fixture):
        users = users_instance
        func = users.top_controversial(n=n_value_fixture)
        assert isinstance(func, dict)
        assert all(isinstance(key, str) for key in func.keys())
        assert all(isinstance(value, float) for value in func.values())
        assert list(func.values()) == sorted(func.values(),reverse=True)

    @pytest.fixture
    def movies(self):
        return Movies('../datasets/movies.csv')

    def test_data_load(self, movies):
        assert isinstance(movies.data, list)
        assert len(movies.data) > 0
        for movie in movies.data:
            assert isinstance(movie, dict)

    def test_extract_year(self, movies):
        title = "Toy Story (1995)"
        year = movies.extract_year(title)
        assert year == "1995"

    def test_extract_year_notcorrect(self, movies):
        title = "Toy Story (199)"
        year = movies.extract_year(title)
        assert year == "unknown year"
    
    def test_extract_year_notcorrect2(self, movies):
        title = "Toy Story"
        year = movies.extract_year(title)
        assert year == "unknown year"

    def test_dist_by_release(self, movies):
        release_test = movies.dist_by_release()
        assert isinstance(release_test, dict)
        for key, value in release_test.items():
            assert isinstance(key, str) and (key.isdigit() or key == "unknown year")
            assert isinstance(value, int)
        assert len(release_test) >0

    def test_dist_by_release_sort(self, movies):
        release_test_sort = movies.dist_by_release()
        values = list(release_test_sort.values())
        assert all(values[i] >= values[i+1] for i in range(len(values)-1))

    def test_dist_by_genres(self, movies):
        genre_test = movies.dist_by_genres()
        assert isinstance(genre_test, dict) 
        for genre, count in genre_test.items():
            assert isinstance(genre, str)
            assert isinstance(count, int)
        assert len(genre_test) > 0

    def test_most_genres(self, movies):
        top_genres = movies.most_genres(5)
        assert isinstance(top_genres, dict)
        assert len(top_genres) <= 5
        for title, count in top_genres.items():
            assert isinstance(title, str)
            assert isinstance(count, int)
            assert count >=1

    def test_most_genres_sort(self, movies):
        top_movies = movies.most_genres(5)
        values = list(top_movies.values())
        assert all(values[i] >= values[i+1] for i in range(len(values) - 1))

    def test_get_all(self, movies):
        all_movies = movies.get_all()
        assert isinstance(all_movies, list)
        for movie in all_movies:
            assert isinstance(movie, dict)
        assert len(all_movies) == len(movies.data)
    
    """
    They should check:
    - if the methods return the correct data types
    - if the lists elements have the correct data types
    - if the returned data sorted correctly
    """
    def test_links(self, links_instance):
        links = links_instance
        assert isinstance(links.imdb_links, dict)
        assert isinstance(links.tmdb_links, dict)
        assert isinstance(links.movie_ids, set)
        assert len(links.movie_ids) > 0

    def test_get_imdb(self, links_instance):
        links = links_instance
        movie_ids = list(links.movie_ids)[:100]
        fields = ['Director', 'Release Date', 'Rating', 'Budget', 'Cumulative Worldwide Gross', 'Runtime']
        imdb_data = links.get_imdb(movie_ids, fields)
        assert isinstance(imdb_data, list)
        assert all(isinstance(item, list) for item in imdb_data)
        assert all(len(item) == len(fields) + 1 for item in imdb_data)
        assert all(item[0] in movie_ids for item in imdb_data)
        assert all([imdb_data[i][0] >= imdb_data[i + 1][0] for i in range(len(imdb_data) - 1)])

    def test_get_tmdb(self, links_instance):
        links = links_instance
        movie_ids = list(links.movie_ids)[:100]
        fields = ['Director', 'Release Date', 'Genres', 'Cast', 'Budget', 'Cumulative Worldwide Gross', 'Runtime']
        tmdb_data = links.get_tmdb(movie_ids, fields)
        assert isinstance(tmdb_data, list)
        assert all(isinstance(item, list) for item in tmdb_data)
        assert all(len(item) == len(fields) + 1 for item in tmdb_data)
        assert all(item[0] in movie_ids for item in tmdb_data)
        assert all([tmdb_data[i][0] >= tmdb_data[i + 1][0] for i in range(len(tmdb_data) - 1)])

    def test_top_directors(self, links_instance, n_value_fixture):
        links = links_instance
        directors = links.top_directors(n_value_fixture)
        assert isinstance(directors, dict)
        assert all(isinstance(key, str) for key in directors.keys())
        assert all(isinstance(value, int) for value in directors.values())
        values = list(directors.values())
        assert all(values[i] >= values[i + 1] for i in range(len(values) - 1))


    def test_most_expensive(self, links_instance, n_value_fixture):
        links = links_instance
        expensive_movies = links.most_expensive(n_value_fixture)
        assert isinstance(expensive_movies, dict)
        assert all(isinstance(key, str) for key in expensive_movies.keys())
        assert all(isinstance(value, int) for value in expensive_movies.values())
        values = list(expensive_movies.values())
        assert all(values[i] >= values[i + 1] for i in range(len(values) - 1))


    def test_most_profitable(self, links_instance, n_value_fixture):
        links = links_instance
        profitable_movies = links.most_profitable(n_value_fixture)
        assert isinstance(profitable_movies, dict)
        assert all(isinstance(key, str) for key in profitable_movies.keys())
        assert all(isinstance(value, int) for value in profitable_movies.values())
        values = list(profitable_movies.values())
        assert all(values[i] >= values[i + 1] for i in range(len(values) - 1))

    def test_longest(self, links_instance, n_value_fixture):
        links = links_instance
        longest_movies = links.longest(n_value_fixture)
        assert isinstance(longest_movies, dict)
        assert all(isinstance(key, str) for key in longest_movies.keys())
        assert all(isinstance(value, int) for value in longest_movies.values())
        assert all([value[i] >= value[i + 1] for i in range(len(longest_movies) - 1) for value in longest_movies.values()])

    def test_top_cost_per_minute(self, links_instance, n_value_fixture):
        links = links_instance
        cost_per_minute_movies = links.top_cost_per_minute(n_value_fixture)
        assert isinstance(cost_per_minute_movies, dict)
        assert all(isinstance(key, str) for key in cost_per_minute_movies.keys())
        assert all(isinstance(value, float) for value in cost_per_minute_movies.values())
        values = list(cost_per_minute_movies.values())
        assert all(values[i] >= values[i + 1] for i in range(len(values) - 1))

    @pytest.fixture(scope="class")
    @staticmethod
    def word_fixture():
        word = 'netflix'
        return word

    def test_tags(self, tags_instance):
        assert isinstance(tags_instance.userIDs, set)
        assert isinstance(tags_instance.movieIDs, set)
        assert isinstance(tags_instance.tags, dict)
        assert isinstance(tags_instance.timestamps, dict)
        assert len(tags_instance.userIDs) > 0
        assert len(tags_instance.movieIDs) > 0

    def test_most_words(self, tags_instance, n_value_fixture):
        most_words = tags_instance.most_words(n_value_fixture)
        assert isinstance(most_words, dict)
        assert all(isinstance(key, str) for key in most_words.keys())
        assert all(isinstance(value, int) for value in most_words.values())
        vals = list(most_words.values())
        assert all(vals[i] >= vals[i+1] for i in range(len(most_words)-1))

    def test_longest(self, tags_instance, n_value_fixture):
        longest_tags = tags_instance.longest(n_value_fixture)
        assert isinstance(longest_tags, list)
        assert all(isinstance(tag, str) for tag in longest_tags)
        assert all(len(longest_tags[i]) >= len(longest_tags[i+1]) for i in range(len(longest_tags)-2))

    def test_most_words_and_longest(self, tags_instance, n_value_fixture):
        intersection = tags_instance.most_words_and_longest(n_value_fixture)
        assert isinstance(intersection, set)
        assert all(isinstance(tag, str) for tag in intersection)

    def test_most_popular(self, tags_instance, n_value_fixture):
        popular_tags = tags_instance.most_popular(n_value_fixture)
        assert isinstance(popular_tags, dict)
        assert all(isinstance(tag, str) for tag in popular_tags.keys())
        assert all(isinstance(value, int) for value in popular_tags.values())
        vals = list(popular_tags.values())
        assert all(vals[i] >= vals[i + 1] for i in range(len(popular_tags)-2))

    def test_tags_with(self, tags_instance, word_fixture):
        tags_with_word = tags_instance.tags_with(word_fixture.lower())
        assert isinstance(tags_with_word, list)
        assert all(isinstance(tag, str) for tag in tags_with_word)
        assert all(word_fixture in tag.lower() for tag in tags_with_word)
