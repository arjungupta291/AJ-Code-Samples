from urllib import request
import json
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
    
### Main Function ###

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


if __name__ == '__main__':
    year = int(input("Enter A Year to see Win Predictions: "))
    print (expectedWins(year))


        
            
            
        




    

        

            


    
    





    

    

    

    
        
    


    

    
                
