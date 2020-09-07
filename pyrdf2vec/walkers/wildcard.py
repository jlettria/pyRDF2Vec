import itertools
from typing import Any, List, Set, Tuple

import rdflib

from pyrdf2vec.graph import KnowledgeGraph, Vertex
from pyrdf2vec.walkers import RandomWalker


class WildcardWalker(RandomWalker):
    """Defines the wild card walking strategy.

    Attributes:
        depth: The depth per entity.
        walks_per_graph: The maximum number of walks per entity.

    """

    def __init__(
        self, depth: int, walks_per_graph: float, wildcards: List[int] = [1]
    ):
        super().__init__(depth, walks_per_graph)
        self.wildcards = wildcards

    def extract(
        self, graph: KnowledgeGraph, instances: List[rdflib.URIRef]
    ) -> Set[Tuple[Any, ...]]:
        """Extracts walks rooted at the provided instances which are then each
        transformed into a numerical representation.

        Args:
            graph: The knowledge graph.

                The graph from which the neighborhoods are extracted for the
                provided instances.
            instances: The instances to extract the knowledge graph.

        Returns:
            The 2D matrix with its number of rows equal to the number of
            provided instances; number of column equal to the embedding size.

        """
        canonical_walks = set()  # type: ignore
        for instance in instances:  # type: ignore
            walks = self.extract_random_walks(graph, Vertex(str(instance)))
            for walk in walks:
                canonical_walks.add(tuple([x.name for x in walk]))  # type: ignore
                for wildcard in self.wildcards:
                    combinations = itertools.combinations(
                        range(1, len(walk)), wildcard  # type: ignore
                    )
                    for idx in combinations:
                        new_walk = []
                        for ix, hop in enumerate(walk):  # type: ignore
                            if ix in idx:
                                new_walk.append(Vertex("*"))
                            else:
                                new_walk.append(hop.name)
                        canonical_walks.add(tuple(new_walk))
        return canonical_walks
