# Authors: Jose Luis Jorro-Aragoneses
import numpy as np

class ExplainedCommunitiesDetection:
    """Class to search all communities that all members have a common
    propertie. This algorithm works with clustering techniques.
    """

    def __init__(self, data, algorithm, sim='euclidean'):
        """Method to configure the detection algorithm.

        Args:
            data (DataFrame): Data used to apply the similarity measure between
            users.
            algorithm (Class): Class of clustering technique.
            sim (str/Class, optional): Similarity function used in clustering
            technique. Defaults to 'euclidean'.
        """
        self.data = data.copy()
        self.algorithm = algorithm
        self.similarity = sim

    def search_all_communities(self, answer_binary=False, percentage=1.0):
        """Method to search all explainable communities.

        Args:
            answer_binary (bool, optional): True to indicate that a common property
            occurs only when all answers are 1.0. Defaults to False.
            percentage (float, optional): Value to determine the minimum percetage of
            commons answers to detect a community. Defaults to 1.0.

        Returns:
            int: Number of communities detected.
            dict: Dictionary where each user is assigned to a community.
        """
        n_communities = 2
        finish_search = False

        while not finish_search:
            community_detection = self.algorithm(self.data)
            result = community_detection.calculate_communities(metric=self.similarity, n_clusters=n_communities)

            complete_data = self.data.copy()
            complete_data['community'] = result.values()

            # Comprobamos que para cada grupo existe al menos una respuesta en común
            explainables = []
            self.communities = complete_data.groupby(by='community')
            for c in range(n_communities):
                community = self.communities.get_group(c)
                explainables.append(self.is_explainable(community, answer_binary, percentage))

            finish_search = sum(explainables) == n_communities

            if not finish_search:
                n_communities += 1

        return n_communities, result

    def get_community(self, id_community, answer_binary=False, percentage=1.0):
        """Method to obtain all information about a community.

        Args:
            id_community (int): Id or name of community returned by detection method.
            answer_binary (bool, optional): True to indicate that a common property
            occurs only when all answers are 1.0. Defaults to False. Defaults to False.

        Returns:
            dict: All data that describes the community:
                - name: name of community.
                - members: list of index included in this community.
                - properties: common properties of community. It is a dictionary where:
                    each property is identified by column_name of data, and the value is
                    the common value in this column.
        """
        community = self.communities.get_group(id_community)


        community_data = {'name': id_community}
        community_data['percentage'] = percentage
        community_data['members'] = list(community.index.values)

        community_data['properties'] = dict()       

        for col in community.columns.values:
            if col != 'community':
                if answer_binary:
                    if (len(community[col]) * percentage) <= community[col].sum():
                        community_data['properties'][col] = community[col].value_counts().index[0]
                        # print('-', col, community[col].value_counts().index[0])
                else:
                    
                    if (len(community[col]) * percentage) <= community[col].value_counts().max():
                        community_data['properties'][col] = community[col].value_counts().index[0]
                        # print('-', col, community[col].value_counts().index[0])

        return community_data

    def is_explainable(self, community, answer_binary=False, percentage=1.0):
        explainable_community = False

        for col in community.columns.values:
            if col != 'community':
                if answer_binary:
                    explainable_community |= (len(community[col]) * percentage)  <= community[col].sum()
                else:
                    explainable_community |= (len(community[col]) * percentage) <= community[col].value_counts().max()
        
        return explainable_community