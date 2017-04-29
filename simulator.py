#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""Simulate attacks on the Internet topology."""

# Remove up to 10% of the nodes with a step of 0.1%.
start = 0
end = 0.1
step = 0.001

# Test various attack types.
attack_types = ['random', 'targeted',
                'random_path', 'targeted_path']


def measure(network):
    """Measure the robustness of a network.

    The result is a pair having the number of connected components
    as its first member and the size of the largest connected component
    as its second member.

    Parameters
    ----------
    network : networkx.Graph (or similar)
        Network to measure.

    Returns
    -------
    (int, int)
        Pair consisting of the number of connected components and the size
        of the largest component.
    """
    components = list(nx.connected_component_subgraphs(network))
    gigantic_component = max(components, key=len)
    return len(components), len(gigantic_component)


def simulate(attacker, attack_type, result_store):
    """Simulate attacks on a network.

    The attacks are simulated and results are written in the `result_store`
    dictionary, indexed by the strength of the attack (fraction of nodes
    that were removed).

    Parameters
    ----------
    attacker : attacker.NetworkAttacker
        Attacker that will carry out the attacks.

    attack_type : str
        Type of the attack that will be performed.

    result_store : multiprocessing.managers.DictProxy
        Dictionary where results will be written.
    """
    global start, end, step

    def fmt(num): return "{:.3f}".format(num)
    iters = int((end - start) / step)
    result_store[fmt(0)] = measure(attacker.network)

    for i in range(iters):
        getattr(attacker, attack_type)()
        result_store[fmt((i + 1) * step)] = measure(attacker.network)


if __name__ == '__main__':
    """Main program."""
    import argparse
    import random
    import pickle
    from time import mktime
    from datetime import datetime
    from multiprocessing import Process, Manager
    import networkx as nx
    from attacker import NetworkAttacker
    from data_reader import read_data

    parser = argparse.ArgumentParser(prog='simulator')
    parser.add_argument('input_filename', help='Location of input data',
                        type=str)
    parser.add_argument('output_filename', help='Location of output data',
                        type=str)
    args = parser.parse_args()

    random.seed(13)

    with Manager() as manager:
        robustness = manager.dict({attack_type: manager.dict()
                                   for attack_type in attack_types})

        for network, timestamp in read_data(args.input_filename,
                                            '%Y%m.relationship.gz',
                                            nx.read_edgelist,
                                            nodetype=int,
                                            data=(('connection_class', str),)):
            # Convert the timestamp to human-readable.
            timestamp = datetime.fromtimestamp(mktime(timestamp))
            timestamp = timestamp.strftime("%Y-%m")
            print("Processing topology data for {}".format(timestamp))

            # Initialize the result store for this timestamp.
            for attack_type in attack_types:
                robustness[attack_type][timestamp] = manager.dict()

            # Calculate the number of nodes to be removed at each step,
            # and initialize the processes.
            n = int(round(len(network) * step))
            ps = [Process(target=simulate,
                          args=(NetworkAttacker(network, n),
                                attack_type,
                                robustness[attack_type][timestamp]))
                  for attack_type in attack_types]

            # Start the processes and wait for them to finish.
            for p in ps:
                p.start()

            for p in ps:
                p.join()

        # Convert the robustness data to a local dict, and pickle it.
        robustness = {
            attack_type: {
                timestamp: dict(result)
                for timestamp, result in timestamped_results.items()
            } for attack_type, timestamped_results in robustness.items()
        }

        with open(args.output_filename, 'wb') as handle:
            pickle.dump(robustness, handle)

        print(robustness)
