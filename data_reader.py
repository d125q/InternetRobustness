#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""Internet topology data reader."""

import os
import time


def read_data(dirname, filename_format, reader, *args, **kwargs):
    """Read Internet topology data.

    Filenames are assumed to be timestamped, e.g.,
    ``201603.relationship.gz''.  Such file would indicate the state of
    the Internet topology in March 2016.  Example data can be found at
    http://irl.cs.ucla.edu/topology/ipv4/relationship/.

    Additional parameters are passed over to the reader.

    Parameters
    ----------
    dirname : str
        Directory name where data will be searched for.

    filename_format : str
        Format string of each filename, using strftime format directives.

    reader : function
        Function to read in the dataset.  It must take a filename as its
        first parameter, with additional parameters as desired.

    Returns
    -------
    generator of (networkx.Graph (or similar), time.struct_time)
        Graphs that were read.
    """
    for root, _, filenames in os.walk(dirname):
        for filename in filenames:
            try:
                timestamp = time.strptime(filename, filename_format)
                graph = reader(os.path.join(root, filename),
                               *args, **kwargs)
                yield graph, timestamp
            except ValueError:
                pass
