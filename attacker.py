#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""Network attacks following various strategies."""

import random


class NetworkAttacker:
    def __init__(self, network, n, metric=None):
        """Initialize a network attacker.

        Parameters
        ----------
        network : networkx.Graph (or similar)
            Network to be attacked.

        n : int
            Number of nodes to be removed per step.

        metric : function, optional
            Node metric to measure which node to target
            in certain attacks (nodes with higher values
            for the metric are better targets).  Defaults
            to a degree-based metric.
        """
        self._network = network.copy()
        self._n = n

        if metric is None:
            self._metric = type(self._network).degree
        else:
            self._metric = metric

    def _random_node(self, nodes=None):
        """Choose a node at random.

        Parameters
        ----------
        nodes : iterable, optional
            Nodes to choose from.  If not provided, the entire
            network is assumed.

        Returns
        -------
        Random node from the graph.
        """
        return random.choice(list(
            nodes if nodes is not None else self._network.nodes()))

    def _best_node(self, nodes=None):
        """Choose the node with the highest value for the metric.

        Parameters
        ----------
        nodes : iterable, optional
            Nodes to choose from.  If not provided, the entire
            network is assumed.

        Returns
        -------
        Node with the maximum value of the metric.
        """
        ranks = self._metric(self._network, nodes)
        node, _ = max(ranks, key=lambda item: item[1])
        return node

    def _attack(self, choose_target, n=None):
        if n is None:
            n = self._n

        for _ in range(n):
            self._network.remove_node(choose_target())

    def _path_chooser(self, neighbor_discriminator):
        target = self._random_node()
        neighbors = None

        def choose_target():
            nonlocal target
            nonlocal neighbors

            if neighbors is not None:
                if not neighbors:
                    target = self._random_node()
                else:
                    target = neighbor_discriminator(neighbors)

            neighbors = list(self._network.neighbors(target))
            return target

        return choose_target

    def random(self, n=None):
        """Attack nodes randomly."""
        self._attack(self._random_node, n)

    def targeted(self, n=None):
        """Attack nodes as ordered by the metric."""
        self._attack(self._best_node, n)

    def random_path(self, n=None):
        """Attack nodes following a random path.

        The first node is chosen at random.  Afterwards, a random
        neighbor is attacked.  If the previously attacked node has no
        neighbors, the procedure is restarted.
        """
        self._attack(self._path_chooser(self._random_node), n)

    def targeted_path(self, n=None):
        """Attack nodes using a "mixed" approach.

        The first node is chosen at random.  Afterwards, the "fittest"
        (as gauged by the metric) neighbor is attacked.  If the
        previously attacked node has no neighbors, the procedure is
        restarted.
        """
        self._attack(self._path_chooser(self._best_node), n)

    @property
    def n(self):
        """int: Number of nodes that are attacked at each step."""
        return self._n

    @property
    def network(self):
        """networkx.Graph (or similar): Network being attacked."""
        return self._network
