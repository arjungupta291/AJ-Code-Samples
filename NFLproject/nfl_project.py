from urllib import request
from bs4 import BeautifulSoup
import json
import heapq
from pprint import pprint
from scipy import stats

teams = ['SF', 'CHI', 'CIN', 'BUF', 'DEN', 'CLE', 'TB', 'ARI',
             'SD', 'KC', 'IND', 'DAL', 'MIA', 'PHI', 'ATL', 'NYG',
             'JAX', 'NYJ', 'DET', 'GB', 'CAR', 'NE', 'OAK', 'STL',
             'BAL', 'WAS', 'NO', 'SEA', 'PIT', 'HOU', 'TEN', 'MIN']

teams.sort()

api_key = 'b7d211fd970143a2940d9905fe5c2447'

url_form_stats = 'http://api.nfldata.apiphany.com/trial/json/TeamSeasonStats/2013?subscription-key=b7d211fd970143a2940d9905fe5c2447'  

url_form_sched = 'http://api.nfldata.apiphany.com/trial/json/Schedules/2015?subscription-key=b7d211fd970143a2940d9905fe5c2447'

###Builder Functions###

def truncate(f, n):
    '''Truncates/pads a float f to n decimal places without rounding'''
    s = '{}'.format(f)
    if 'e' in s or 'E' in s:
        return '{0:.{1}f}'.format(f, n)
    i, p, d = s.partition('.')
    return '.'.join([i, (d+'0'*n)[:n]])

def pullSeasonData(year):
    # enter year as int in yyyy format
    file = open("NFLstats" + str(year % 100).zfill(2) + ".txt", "w")
    url = 'http://api.nfldata.apiphany.com/trial/json/TeamSeasonStats/' + year + '?subscription-key=b7d211fd970143a2940d9905fe5c2447'
    obj = request.urlopen(url)
    data = str(json.load(obj))
    file.write(data)
    file.close()
    # data is in the format of a list with dictionary elements
    # data is converted to string to be written to txt file; can use eval() to undo

def pullSeasonSchedule(year):
    # enter year as int in yyyy format
    file = open("NFLsched" + str(year % 100).zfill(2) + ".txt", "w")
    url = 'http://api.nfldata.apiphany.com/trial/json/Schedules/' + year + '?subscription-key=b7d211fd970143a2940d9905fe5c2447'
    obj = request.urlopen(url)
    data = str(json.load(obj))
    file.write(data)
    file.close()
    # data is in the format of a list with dictionary elements
    # data is converted to string to be written to txt file; can use eval() to undo

def getTeamSchedule(team,year):
    # enter team as string of abbreviation as seen in list Teams
    # enter year as int in yyyy format
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
    # returns schedule in order as a list which can be iterated over
 
def getLocationSchedule(team,year):
    # enter team as string of abbreviation as seen in list Teams
    # enter year as int in yyyy format
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
    #returns location = home/away in order as a list which can be iterated over

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
    # enter year as int in yyyy format
    # enter in the previous year and the target projected year to find percentage boost due to personnel
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
    # enter year as int in yyyy format
    # enter in the previous year and the target projected year to find percentage boost due to personnel
    prevYearDefensiveRatings = assignDefensiveRatings(prev_year)
    projYearDefensiveRatings = assignDefensiveRatings(proj_year)
    defensiveBoosts = {} 
    for team in teams:
        defensiveBoosts[team] = ((projYearDefensiveRatings[team] - prevYearDefensiveRatings[team]) / 100.0)
    return defensiveBoosts
    # returns boosts in terms of positive or negative percent indicating an improvement or worsening of personnel/injuries
        
def assignOffensiveYPP(year):
    # enter year as int in yyyy format
    # if we want to predict 2014 wins, enter 2014
    stats_file = open("NFLstats" + str((year - 1) % 100).zfill(2) + ".txt", "r")
    stats = eval(stats_file.read())
    offensiveBoost = offensiveBoosts(year -1 , year)
    offensiveYPP = {}
    for team in teams:
        offensiveYPP[team] = round(((1 - offensiveBoost[team]) * ((stats[teams.index(team)]["OffensiveYards"] + 0.0) / (stats[teams.index(team)]["Score"]))), 2)
    stats_file.close()
    return offensiveYPP

def assignDefensiveYPP(year):
    # enter year as int in yyyy format
    # if we want to predict 2014 wins, enter 2014
    stats_file = open("NFLstats" + str((year - 1) % 100).zfill(2) + ".txt", "r")
    stats = eval(stats_file.read())
    defensiveBoost = defensiveBoosts(year - 1, year)
    defensiveYPP = {}
    for team in teams:
        defensiveYPP[team] = round(((1 + defensiveBoost[team]) * ((stats[teams.index(team)]["OpponentOffensiveYards"] + 0.0) / (stats[teams.index(team)]["OpponentScore"]))), 2)
    stats_file.close()
    return defensiveYPP

def assignYPPspread(year):
    # enter year as int in yyyy format
    # if we want to predict 2014 wins, enter 2013 stats
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
    # enter year as int in yyyy format
    # will output win percentage from the perspective of 'team' input
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
    
### Main Functions ###

def expectedWins(year):
    # enter year as int in yyyy format
    # enter the year you want to make predictions for
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

   


        
            
            
        




    

        

            


    
    





    

    

    

    
        
    


    

    
                
