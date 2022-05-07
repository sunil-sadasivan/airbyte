#
# Copyright (c) 2021 Airbyte, Inc., all rights reserved.
#


import sys

from airbyte_cdk.entrypoint import launch
from source_senate_lobbyist import SourceSenateLobbyist

if __name__ == "__main__":
    source = SourceSenateLobbyist()
    launch(source, sys.argv[1:])
