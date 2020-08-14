from rdf2vec.walkers import Walker
from rdf2vec.graph import Vertex
import numpy as np
from hashlib import md5


class RandomWalker(Walker):
    """Defines the random walker of the walking strategy.

    Attributes:
        depth (int): The depth per entity.
        walks_per_graph (float): The maximum number of walks per entity.

    """

    def __init__(self, depth, walks_per_graph):
        super(RandomWalker, self).__init__(depth, walks_per_graph)

    def extract_random_walks(self, graph, root):
        """Extracts random walks of depth - 1 hops rooted in root.

        Note:
            You can create a `graph.KnowledgeGraph` object from an
            `rdflib.Graph` object by using a converter method.

        Args:
            graph (graph.KnowledgeGraph): The knowledge graph.
                The graph from which the neighborhoods are extracted for the
                provided instances.
            root (Vertex): The root.

        Returns:
            numpy.array: The array of the walks.

        """
        # Initialize one walk of length 1 (the root)
        walks = {(root,)}

        for i in range(self.depth):
            # In each iteration, iterate over the walks, grab the 
            # last hop, get all its neighbors and extend the walks
            walks_copy = walks.copy()
            for walk in walks_copy:
                node = walk[-1]
                neighbors = graph.get_neighbors(node)

                if len(neighbors) > 0:
                    walks.remove(walk)

                for neighbor in neighbors:
                    walks.add(walk + (neighbor, ))

            # TODO: Should we prune in every iteration?
            if self.walks_per_graph is not None:
                n_walks = min(len(walks),  self.walks_per_graph)
                walks_ix = np.random.choice(range(len(walks)), replace=False, 
                                            size=n_walks)
                if len(walks_ix) > 0:
                    walks_list = list(walks)
                    walks = {walks_list[ix] for ix in walks_ix}

        # Return a numpy array of these walks
        return list(walks)

    def extract(self, graph, instances):
        """Extracts a knowledge graph and transform it into a 2D vector, based
        on provided instances.

        Note:
            You can create a `graph.KnowledgeGraph` object from an
            `rdflib.Graph` object by using a converter method.

        Args:
            graph (graph.KnowledgeGraph): The knowledge graph.
                The graph from which the neighborhoods are extracted for the
                provided instances.
            instances (array-like): The instances to extract the knowledge graph.

        Returns:
            list: The 2D vector corresponding to the knowledge graph.

        """
        canonical_walks = set()
        for instance in instances:
            walks = self.extract_random_walks(graph, Vertex(str(instance)))
            for walk in walks:
                canonical_walk = []
                for i, hop in enumerate(walk):
                    if i == 0 or i % 2 == 1:
                        canonical_walk.append(hop.name)
                    else:
                        digest = md5(hop.name.encode()).digest()[:8]
                        canonical_walk.append(str(digest))

                canonical_walks.add(tuple(canonical_walk))

        return canonical_walks
