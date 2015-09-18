from urllib import request
from bs4 import BeautifulSoup
import json
from pprint import pprint
from scipy import stats
from utils import truncate

#############
### Setup ###
#############

teams = ['SF', 'CHI', 'CIN', 'BUF', 'DEN', 'CLE', 'TB', 'ARI',
             'SD', 'KC', 'IND', 'DAL', 'MIA', 'PHI', 'ATL', 'NYG',
             'JAX', 'NYJ', 'DET', 'GB', 'CAR', 'NE', 'OAK', 'STL',
             'BAL', 'WAS', 'NO', 'SEA', 'PIT', 'HOU', 'TEN', 'MIN']

teams.sort()

api_key = 'b7d211fd970143a2940d9905fe5c2447'

url_form_stats = 'http://api.nfldata.apiphany.com/trial/json/TeamSeasonStats/2013?subscription-key=b7d211fd970143a2940d9905fe5c2447'  

url_form_sched = 'http://api.nfldata.apiphany.com/trial/json/Schedules/2015?subscription-key=b7d211fd970143a2940d9905fe5c2447'

#################################
### Data Extraction Functions ###
#################################

## These functions extract the NFL team performance data from external API's and save them to local text files to 
## avoid having to poing the API. The YEAR argument can be entered as an int and the TEAM argument can be entered
## as a string abbreviation as seen in the teams array in Setup. With much more experience now than at the time, 
## I would add simple MongoDB integration as I worked in JSON format and extensively with dictionaries. This would
## also allow me to avoid using 'eval' which I now know is frowned upon. 

def pullSeasonData(year):
    file = open("NFLstats" + str(year % 100).zfill(2) + ".txt", "w")
    url = 'http://api.nfldata.apiphany.com/trial/json/TeamSeasonStats/' + year + '?subscription-key=b7d211fd970143a2940d9905fe5c2447'
    obj = request.urlopen(url)
    data = str(json.load(obj))
    file.write(data)
    file.close()

def pullSeasonSchedule(year):
    file = open("NFLsched" + str(year % 100).zfill(2) + ".txt", "w")
    url = 'http://api.nfldata.apiphany.com/trial/json/Schedules/' + year + '?subscription-key=b7d211fd970143a2940d9905fe5c2447'
    obj = request.urlopen(url)
    data = str(json.load(obj))
    file.write(data)
    file.close()

def getTeamSchedule(team,year):
    data_file = open("NFLsched" + str(year % 100).zfill(2) + ".txt", "r+")
    data = eval(data_file.read())
    schedule = []
    for item in data:
        if item["HomeTeam"] == team:
            schedule.append(str(item["AwayTeam"]))
        elif item["AwayTeam"] == team:
            schedule.append(str(item["HomeTeam"]))
    data_file.close()
    return schedule
 
def getLocationSchedule(team,year):
    data_file = open("NFLsched" + str(year % 100).zfill(2) + ".txt", "r+")
    data = eval(data_file.read())
    location = []
    for item in data:
        if item["HomeTeam"] == team:
            location.append("H")
        elif item["AwayTeam"] == team:
            location.append("A")
    data_file.close()
    return location
    #returns home/away in order as a list which can be iterated over

#####################################
### Qualitative Factors Functions ###
#####################################

## The functions in this section look to use qualitative factors such as personnel changes, injuries, 
## coaching changes, etc... to develop position group power rankings which are used to provide quantitative 
## performance boosts or costs into the coming year. This is a way of translating last year's performance
## statistics into this year's projections. 

def assignOffensiveRatings(year):
    scale = {"Coaching": 25, "QB": 25, "O-Line": 20, "WR/TE": 15, "RB": 15}
    data_file = open("TeamRankings" + str(year % 100).zfill(2) + ".txt", "r+")
    data = eval(data_file.read())
    offensiveRatings = {}
    for team in teams:
        coachingScore = ((data[teams.index(team)]["Coaching"] / 5.0) * scale["Coaching"])
        qbScore = ((data[teams.index(team)]["QB"] / 5.0) * scale["QB"])
        oLineScore = ((data[teams.index(team)]["O-Line"] / 5.0) * scale["O-Line"])
        wrTeScore = ((data[teams.index(team)]["WR/TE"] / 5.0) * scale["WR/TE"])
        rbScore = ((data[teams.index(team)]["RB"] / 5.0) * scale["RB"])
        offensiveRatings[team] = int(coachingScore + qbScore + oLineScore + wrTeScore + rbScore)
    data_file.close()
    return offensiveRatings

def offensiveBoosts(prev_year, proj_year):
    prevYearOffensiveRatings = assignOffensiveRatings(prev_year)
    projYearOffensiveRatings = assignOffensiveRatings(proj_year)
    offensiveBoosts = {} 
    for team in teams:
        offensiveBoosts[team] = ((projYearOffensiveRatings[team] - prevYearOffensiveRatings[team]) / 100.0)
    return offensiveBoosts
    # returns boosts in terms of positive or negative percent indicating an improvement or worsening of personnel/injuries

def assignDefensiveRatings(year):
    scale = {"Coaching": 25, "Secondary": 25, "LB": 25, "D-Line": 25}
    data_file = open("TeamRankings" + str(year % 100).zfill(2) + ".txt", "r+")
    data = eval(data_file.read())
    defensiveRatings = {}
    for team in teams:
        coachingScore = ((data[teams.index(team)]["Coaching"] / 5.0) * scale["Coaching"])
        secondaryScore = ((data[teams.index(team)]["Secondary"] / 5.0) * scale["Secondary"])
        lbScore = ((data[teams.index(team)]["LB"] / 5.0) * scale["LB"])
        dLineScore = ((data[teams.index(team)]["D-Line"] / 5.0) * scale["D-Line"])
        defensiveRatings[team] = int(coachingScore + secondaryScore + lbScore + dLineScore)
    data_file.close()
    return defensiveRatings

def defensiveBoosts(prev_year, proj_year):
    prevYearDefensiveRatings = assignDefensiveRatings(prev_year)
    projYearDefensiveRatings = assignDefensiveRatings(proj_year)
    defensiveBoosts = {} 
    for team in teams:
        defensiveBoosts[team] = ((projYearDefensiveRatings[team] - prevYearDefensiveRatings[team]) / 100.0)
    return defensiveBoosts
    # returns boosts in terms of positive or negative percent indicating an improvement or worsening of personnel/injuries
        
######################################
### Quantitative Factors Functions ###
######################################

## Here we dive into the performance stats and develop a method to handicap games or, in other words, calculate
## the spreads which drive our probabilistic distributions. The primary stat used is YARDS PER POINT which can be 
## used to calculate offensive and defensive efficiency. The qualitative rankings in the previous section go 
## toward adjusting the YARDS PER POINT SPREAD based on perceived improvements or declines in qualitative 
## performance metrics. The last function here lays out a method to calculate the PER GAME win probability for 
## a mathchup using YPP Spreads.

def assignOffensiveYPP(year):
    stats_file = open("NFLstats" + str((year - 1) % 100).zfill(2) + ".txt", "r")
    stats = eval(stats_file.read())
    offensiveBoost = offensiveBoosts(year -1 , year)
    offensiveYPP = {}
    for team in teams:
        offensiveYPP[team] = round(((1 - offensiveBoost[team]) * ((stats[teams.index(team)]["OffensiveYards"] + 0.0) / (stats[teams.index(team)]["Score"]))), 2)
    stats_file.close()
    return offensiveYPP

def assignDefensiveYPP(year):
    stats_file = open("NFLstats" + str((year - 1) % 100).zfill(2) + ".txt", "r")
    stats = eval(stats_file.read())
    defensiveBoost = defensiveBoosts(year - 1, year)
    defensiveYPP = {}
    for team in teams:
        defensiveYPP[team] = round(((1 + defensiveBoost[team]) * ((stats[teams.index(team)]["OpponentOffensiveYards"] + 0.0) / (stats[teams.index(team)]["OpponentScore"]))), 2)
    stats_file.close()
    return defensiveYPP

def assignYPPspread(year):
    stats_file = open("NFLstats" + str((year - 1) % 100).zfill(2) + ".txt", "r")
    stats = eval(stats_file.read())
    YPPspread = {}
    offensiveYPP = assignOffensiveYPP(year)
    defensiveYPP = assignDefensiveYPP(year)
    for team in teams:
        YPPspread[team] = round((defensiveYPP[team] - offensiveYPP[team]), 2)
    stats_file.close()
    return YPPspread

def gameWinProbability(year,team,opponent):
    YPPspread = assignYPPspread(year)
    schedule = getTeamSchedule(team,year)
    location = getLocationSchedule(team,year)
    if location[schedule.index(opponent)] == "H":
        line = ((YPPspread[team] - YPPspread[opponent]) + 1.5)
    elif location[schedule.index(opponent)] == "A":
        line = ((YPPspread[team] - YPPspread[opponent]) - 1.5)
    distribution = stats.norm(line,13)
    winProbability = round((1 - distribution.cdf(0)), 2)
    return winProbability

##################################################
### Vegas Odds/Lines Data Extraction Functions ###
##################################################

## This is another data extraction section. I use a custom built web scraper to collect Odds/Lines
## from Vegas Bookies. Web Scraping is a variable process involving trial and error so a large 
## challenge is isolating the data you need and formatting it for efficienct use within the program.
## We do that here and then lastly, use the over/under odds data to calculate the implied probabilities
## Vegas is showing for teams finishing above/below the line (Vegas's expected win total).

def assignOdds(data):
    teams_unsorted = ['SF', 'CHI', 'CIN', 'BUF', 'DEN', 'CLE', 'TB', 'ARI',
                      'SD', 'KC', 'IND', 'DAL', 'MIA', 'PHI', 'ATL', 'NYG',
                      'JAX', 'NYJ', 'DET', 'GB', 'CAR', 'NE', 'OAK', 'STL',
                      'BAL', 'WAS', 'NO', 'SEA', 'PIT', 'HOU', 'TEN', 'MIN']
    team_info = {}
    for team in teams_unsorted:
        team_data = data.pop(0)
        if team_data[0] == 'Chiefs':
            team_info[team] = [float(team_data[1]), int(team_data[3][:4]), int(team_data[6][:4])]
        elif len(team_data) == 10:
            team_info[team] = [float(team_data[1]), int(team_data[4][:4]), int(team_data[6][:4])]
        elif len(team_data) == 11:
            team_info[team] = [float(team_data[1]), int(team_data[4][:4]), int(team_data[7][:4])]
    return team_info

def oddsScraper():
    url = "http://linemakers.sportingnews.com/article/4635972-nfl-win-totals-2015-season-vegas-odds-seahawks-patriots-cowboys-saints-broncos"
    content = request.urlopen(url)
    html = content.read()
    soup = BeautifulSoup(html, "html.parser")
    info_location = soup.find_all('div', {'class': 'entry-content'})
    general_odds_section = info_location[0].find_all('p')
    odds_data = general_odds_section[4].find_all('br')
    relevant_data = odds_data[0].get_text()
    formatted_data = relevant_data.split('\n')
    split_data = [item.split(" ") for item in formatted_data if item]
    return assignOdds(split_data)
    ## Returned in format {team: [expectedWins, 'Over', 'Under']} ##

def vegasProbabilites(teamOdds):
    for team in teamOdds:
        over = teamOdds[team][1]
        under = teamOdds[team][2]
        if over < 0:
            teamOdds[team][1] = round(((-(over)) / ((-(over)) + 100.0 )), 2)
        else:
            teamOdds[team][1] =  round((100.0 / (over + 100)), 2)
        if under < 0:
            teamOdds[team][2] = round(((-(under)) / ((-(under)) + 100.0 )), 2)
        else:
            teamOdds[team][2] = round((100.0 / (under + 100)), 2)
    return teamOdds

######################    
### Main Functions ###
######################

## This section is the real functionality of the program. We use our statistical spreads to calculate the 
## win probabilite for every team in every game they play that year. We then sum up those probabilities, 
## as dictated by the method of indicators, to determine the expected win total for each team in the coming
## year. Our per game scoring distribution is normal with mean derived from our YPP spreading technique, and 
## standard deviation obtained through research into how games have unfolded in the past, namely through 
## academic papers. Our next steps are to determine the probability of our expected win scenario occurring under
## the implied Vegas Distribition for win totals which we obtained in the last section. With these calculations, 
## we can find the edge in certain bets and make recommendations on whether to take the over or under bet. 
## Of note is that if our predicted win total and the Vegas predicted win total differs by less than 1.5 games, 
## we conclude that there is no edge to be had in the bet. Recommendations are returned as a dict with all the 
## relevant information.

def expectedWins(year):
    YPPspread = assignYPPspread(year)
    expectedWins = {}
    for team in teams:
        schedule = getTeamSchedule(team,year)
        location = getLocationSchedule(team,year)
        winProbabilities = []
        for opponent in schedule:
            if opponent == "BYE":
                winProbabilities.append(0.0)
            else:
                if location[schedule.index(opponent)] == "H":
                    line = ((YPPspread[team] - YPPspread[opponent]) + 1.5)
                elif location[schedule.index(opponent)] == "A":
                    line = ((YPPspread[team] - YPPspread[opponent]) - 1.5)
                distribution = stats.norm(line,13)
                winProbabilities.append(round((1 - distribution.cdf(0)), 2))
        expectedWins[team] = int(round(sum(winProbabilities), 0))
    return expectedWins

def compareProbabilities(year):
    ## Expectation of a normal random variable suggests 50/50 over/under probabilites ##
    teamWins = expectedWins(year)
    teamOdds = oddsScraper()
    vegasImpliedProbs = vegasProbabilites(teamOdds)
    vegasValgoProbabilities = {}
    for team in teamWins:
        vegasExpectation = vegasImpliedProbs[team][0]
        vegasDistribution = stats.norm(vegasExpectation, 2.5)
        againstVegasUnderProbability = float(truncate(vegasDistribution.cdf(teamWins[team]), 2))
        againstVegasOverProbability = float(truncate(1 - againstVegasUnderProbability, 2))
        vegasValgoProbabilities[team] = [vegasImpliedProbs[team][0], againstVegasOverProbability, againstVegasUnderProbability]
    return vegasValgoProbabilities, teamWins

def generalRecommendations(year):
    algoProbabilites, algoWins = compareProbabilities(year)
    recommendations = {}
    for team in algoProbabilites:
        if abs(algoProbabilites[team][0] - algoWins[team]) < 1.5:
            recommendations[team] = {"Algo Expected Wins": algoWins[team],
                                     "Vegas Wins": algoProbabilites[team][0],
                                     "Recommendation": "Avoid", 
                                     "Edge": "Minimal/None"}
        elif algoProbabilites[team][1] < 0.50:
            recommendations[team] = {"Algo Expected Wins": algoWins[team],
                                     "Vegas Wins": algoProbabilites[team][0],
                                     "Recommendation": "Over", 
                                     "Edge": truncate((algoProbabilites[team][2] - 0.50) * 100, 2) + "%"}
        elif algoProbabilites[team][1] > 0.50:
            recommendations[team] = {"Algo Expected Wins": algoWins[team],
                                     "Vegas Wins": algoProbabilites[team][0],
                                     "Recommendation": "Under", 
                                     "Edge": truncate((algoProbabilites[team][1] - 0.50) * 100, 2) + "%"}
    return recommendations


if __name__ == '__main__':
    year = int(input("Enter current year to see betting recommendations: "))
    pprint(generalRecommendations(year), width=1)


## In this GitHUb demo, there is only support for the 2015 season. If you pip install the dependencies, run the program, 
## and enter 2015, you should get the right bet predictions. Feel free to add to the code or make changes on a separate
## branch. This was my first ever actual functional Python Program. It was a lot of fun. Perhaps if I developed it now, 
## with more experience under my belt it would look different. I would use OO design, database integration, and try to 
## research into more advanced mathematica methods to make predictions. Current coaches examine stats on a rolling 4 week
## basis. I was thinking of turning this into a week to week betting app where stats over a rolling 4 week period are 
## analyzed and bets are recommended through analysis of the most recent performance statistics. 

   


        
            
            
        




    

        

            


    
    





    

    

    

    
        
    


    

    
                
