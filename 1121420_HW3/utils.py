import os
import pandas as pd

BASE = os.path.join(os.path.dirname(__file__), '..', '1121420_HW2')

TEAM_ABBR = {
    'Anaheim AngelsAngels': 'ANA',
    'Los Angeles AngelsAngels': 'LAA',
    'Arizona DiamondbacksDiamondbacks': 'AZ',
    'Arizona DiamondbacksD-backs': 'AZ',
    'Atlanta BravesBraves': 'ATL',
    'Baltimore OriolesOrioles': 'BAL',
    'Boston Red SoxRed Sox': 'BOS',
    'Chicago CubsCubs': 'CHC',
    'Chicago White SoxWhite Sox': 'CWS',
    'Cincinnati RedsReds': 'CIN',
    'Cleveland IndiansIndians': 'CLE',
    'Cleveland GuardiansGuardians': 'CLE',
    'Colorado RockiesRockies': 'COL',
    'Detroit TigersTigers': 'DET',
    'Florida MarlinsMarlins': 'FLA',
    'Miami MarlinsMarlins': 'MIA',
    'Houston AstrosAstros': 'HOU',
    'Kansas City RoyalsRoyals': 'KC',
    'Los Angeles DodgersDodgers': 'LAD',
    'Milwaukee BrewersBrewers': 'MIL',
    'Minnesota TwinsTwins': 'MIN',
    'Montreal ExposExpos': 'MON',
    'New York MetsMets': 'NYM',
    'New York YankeesYankees': 'NYY',
    'Oakland AthleticsAthletics': 'OAK',
    'Philadelphia PhilliesPhillies': 'PHI',
    'Pittsburgh PiratesPirates': 'PIT',
    'San Diego PadresPadres': 'SD',
    'San Francisco GiantsGiants': 'SF',
    'Seattle MarinersMariners': 'SEA',
    'St. Louis CardinalsCardinals': 'STL',
    'Tampa Bay Devil RaysDevil Rays': 'TB',
    'Tampa Bay RaysRays': 'TB',
    'Texas RangersRangers': 'TEX',
    'Toronto Blue JaysBlue Jays': 'TOR',
    'Washington NationalsNationals': 'WSH',
}

WIN_RATE_BINS = [0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8]
WIN_RATE_LABELS = ['0.2-0.3', '0.3-0.4', '0.4-0.5', '0.5-0.6', '0.6-0.7', '0.7-0.8']

ERA_BINS = [0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 200]
ERA_LABELS = ['0-1', '1-2', '2-3', '3-4', '4-5', '5-6', '6-7', '7-8', '8-9', '9-10', '10+']


def load_team_hitting():
    path = os.path.join(BASE, 'mlb_team_hitting_2003_2023.csv')
    df = pd.read_csv(path, encoding='utf-8-sig')
    return df


def load_team_pitching():
    path = os.path.join(BASE, 'mlb_team_pitching_2003_2023.csv')
    df = pd.read_csv(path, encoding='utf-8-sig')
    df['win_rate'] = df['W'] / (df['W'] + df['L'])
    return df


def load_player_pitching():
    path = os.path.join(BASE, 'mlb_player_pitching_2003_2023.csv')
    df = pd.read_csv(path, encoding='utf-8-sig')
    return df


def merge_team_data():
    th = load_team_hitting()
    tp = load_team_pitching()
    merged = pd.merge(tp[['YEAR', 'TEAM', 'win_rate']], th[['YEAR', 'TEAM', 'AVG', 'HR']], on=['YEAR', 'TEAM'])
    merged['win_rate_bin'] = pd.cut(merged['win_rate'], bins=WIN_RATE_BINS, labels=WIN_RATE_LABELS, right=False)
    return merged


def team_abbr(team_name, year):
    if team_name == 'Los Angeles DodgersDodgers' and year <= 2004:
        return 'LA'
    return TEAM_ABBR.get(team_name)


def get_best_worst_team_pitchers():
    tp = load_team_pitching()
    pp = load_player_pitching()

    best_pitchers = []
    worst_pitchers = []

    for year in range(2003, 2024):
        yr_tp = tp[tp['YEAR'] == year]
        best_team = yr_tp.loc[yr_tp['win_rate'].idxmax(), 'TEAM']
        worst_team = yr_tp.loc[yr_tp['win_rate'].idxmin(), 'TEAM']

        best_abbr = team_abbr(best_team, year)
        worst_abbr = team_abbr(worst_team, year)

        yr_pp = pp[pp['YEAR'] == year]
        best_pitchers.append(yr_pp[yr_pp['TEAM'] == best_abbr])
        worst_pitchers.append(yr_pp[yr_pp['TEAM'] == worst_abbr])

    best_df = pd.concat(best_pitchers, ignore_index=True)
    worst_df = pd.concat(worst_pitchers, ignore_index=True)

    best_df['ERA'] = pd.to_numeric(best_df['ERA'], errors='coerce')
    worst_df['ERA'] = pd.to_numeric(worst_df['ERA'], errors='coerce')

    best_df['era_bin'] = pd.cut(best_df['ERA'], bins=ERA_BINS, labels=ERA_LABELS, right=False)
    worst_df['era_bin'] = pd.cut(worst_df['ERA'], bins=ERA_BINS, labels=ERA_LABELS, right=False)

    return best_df, worst_df
