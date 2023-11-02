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


def get_sentiment(data, text_column):
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
    data['Sentiment'] = data[text_column].apply(get_sentiment_helper)

    # Get the sentiment distribution
    sentiment_distribution = data['Sentiment'].value_counts(normalize=True)
    for k, v in sentiment_distribution.items():
        rounded_v = round(v * 100, 2)
        print(f"{k}: {rounded_v}%")


def get_top_positive_comments(data, text_column):
    def get_polarity_safe(text):
        if isinstance(text, str):
            return TextBlob(text).sentiment.polarity
        return 0

    data['Sentiment'] = data[text_column].apply(get_polarity_safe)

    # Sort the dataframe by sentiment in descending order to get most positive comments
    df_sorted_sentiment = data.sort_values(by='Sentiment', ascending=False)

    # Extract top 10 positive comments based on sentiment analysis
    top_positive_comments_safe = df_sorted_sentiment[text_column].head(
        500).tolist()

    seen = set()
    unique_comments = []
    for el in top_positive_comments_safe:
        if el not in seen:
            unique_comments.append(el)
            seen.add(el)
    for i, el in enumerate(unique_comments):
        print(f"{i+1}: {el}")


def get_top_replies(data, reply_column):
    influence = data.groupby('Vertex 1')[
        reply_column].sum().sort_values(ascending=False)

    # Displaying the top individuals from both datasets based on the aggregated counts
    top_individuals = influence.head(10)

    for el in top_individuals.index:
        print(f"{el}, {top_individuals[el]}")


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

            # 'Text' = Volkswagen
            # 'Tweet' = Nike
            text_column = 'Text' if 'Text' in df.columns else 'Tweet'
            # 'Number of Replies' = Volkswagen
            # 'Retweet Count' = Nike
            reply_column = 'Number of Replies' if 'Number of Replies' in df.columns else 'Retweet Count'

            get_top_influencers(df)
            get_sentiment(df, text_column)
            get_top_positive_comments(df, text_column)
            get_top_replies(df, reply_column)
