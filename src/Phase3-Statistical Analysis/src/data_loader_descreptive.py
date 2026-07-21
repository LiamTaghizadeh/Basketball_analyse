import pandas as pd

class NBADataLoader:
    def __init__( self , engine ):
        self.engine = engine 

    def load_dataframe(self , query):
        df = pd.read_sql(query, self.engine)
        return df
    
    def load_top50_league_players(self , query_top50_league_players):
        df = self.load_dataframe(query_top50_league_players)
        return df

    def load_michel_jordan_list(self , query_micheljordan_tropy_list):
        df = self.load_dataframe(query_micheljordan_tropy_list)
        return df

    def load_champion_top15_height(self , query_champions_top15_height):
        df = self.load_dataframe(query_champions_top15_height)
        return df

    def load_champion_top15_experience(self , query_champions_top15_experience):
        df = self.load_dataframe(query_champions_top15_experience)
        return df
    
    def load_suggested_players(self , qury_suggested_players):
        df = self.load_dataframe(qury_suggested_players)
        return df
    
    def load_top15_league_players_height(self , query_top15_league_players_height):
        df = self.load_dataframe(query_top15_league_players_height)
        return df
    
    def load_top15_league_players_experience(self , query_top15_league_players_experience):
        df = self.load_dataframe(query_top15_league_players_experience)
        return df