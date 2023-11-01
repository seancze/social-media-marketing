import os
import pandas as pd
import networkx as nx
from textblob import TextBlob


def get_top_influencers(data):
    # Create a graph from the dataframe
    G = nx.from_pandas_edgelist(data, 'Vertex 1', 'Vertex 2')

    # Calculate centrality measures
    degree_centrality = nx.degree_centrality(G)
    betweenness_centrality = nx.betweenness_centrality(G)
    closeness_centrality = nx.closeness_centrality(G)

    # Get the top influencers based on each measure
    top_degree = sorted(degree_centrality.items(),
                        key=lambda x: x[1], reverse=True)[:10]
    top_betweenness = sorted(betweenness_centrality.items(),
                             key=lambda x: x[1], reverse=True)[:10]
    top_closeness = sorted(closeness_centrality.items(),
                           key=lambda x: x[1], reverse=True)[:10]

    line_break = '\n'
    d = {
        'degree centrality': top_degree,
        'betweenness centrality': top_betweenness,
        'closeness centrality': top_closeness
    }
    for k, v in d.items():
        print(
            f"Top 10 influencers based on {k}:\n{line_break.join([f'{i+1}: {el[0]}' for i, el in enumerate(v)])}")


def get_sentiment(data):
    def get_sentiment_helper(text):
        try:
            analysis = TextBlob(text)
            if analysis.sentiment.polarity > 0:
                return 'positive'
            elif analysis.sentiment.polarity == 0:
                return 'neutral'
            else:
                return 'negative'
        except:
            return 'neutral'

    # apply sentiment analysis
    if 'Text' in data.columns:
        # 'Text' column is for volkswagen
        data['Sentiment'] = data['Text'].apply(get_sentiment_helper)
    else:
        # 'Tweet' column is for nike
        data['Sentiment'] = data['Tweet'].apply(get_sentiment_helper)

    # Get the sentiment distribution
    sentiment_distribution = data['Sentiment'].value_counts(normalize=True)
    for k, v in sentiment_distribution.items():
        rounded_v = round(v * 100, 2)
        print(f"{k}: {rounded_v}%")


if __name__ == "__main__":
    folder_path = 'data'
    # loop through all .xlsx files in the data folder
    for filename in os.listdir(folder_path):
        if filename.endswith('.xlsx'):
            file_path = os.path.join(folder_path, filename)
            print(f"Reading {file_path}")
            # read the .xlsx file into a DataFrame
            df = pd.read_excel(file_path)

            # set the first row as the header and remove it
            df.columns = df.iloc[0]
            df = df.drop(0)
            get_top_influencers(df)
            get_sentiment(df)
