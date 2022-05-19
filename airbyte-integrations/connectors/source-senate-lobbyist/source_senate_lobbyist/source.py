#
# Copyright (c) 2021 Airbyte, Inc., all rights reserved.
#


from abc import ABC
from typing import Any, Iterable, List, Mapping, MutableMapping, Optional, Tuple

import requests
from airbyte_cdk.sources import AbstractSource
from airbyte_cdk.sources.streams import Stream
from airbyte_cdk.sources.streams.http import HttpStream
from airbyte_cdk.sources.streams.http.auth import HttpAuthenticator

"""
TODO: Most comments in this class are instructive and should be deleted after the source is implemented.

This file provides a stubbed example of how to use the Airbyte CDK to develop both a source connector which supports full refresh or and an
incremental syncs from an HTTP API.

The various TODOs are both implementation hints and steps - fulfilling all the TODOs should be sufficient to implement one basic and one incremental
stream from a source. This pattern is the same one used by Airbyte internally to implement connectors.

The approach here is not authoritative, and devs are free to use their own judgement.

There are additional required TODOs in the files within the integration_tests folder and the spec.yaml file.
"""


# Basic full refresh stream
class SenateLobbyistStream(HttpStream, ABC):
    """
    TODO remove this comment

    This class represents a stream output by the connector.
    This is an abstract base class meant to contain all the common functionality at the API level e.g: the API base URL, pagination strategy,
    parsing responses etc..

    Each stream should extend this class (or another abstract subclass of it) to specify behavior unique to that stream.

    Typically for REST APIs each stream corresponds to a resource in the API. For example if the API
    contains the endpoints
        - GET v1/customers
        - GET v1/employees

    then you should have three classes:
    `class SenateLobbyistStream(HttpStream, ABC)` which is the current class
    `class Customers(SenateLobbyistStream)` contains behavior to pull data for customers using v1/customers
    `class Employees(SenateLobbyistStream)` contains behavior to pull data for employees using v1/employees

    If some streams implement incremental sync, it is typical to create another class
    `class IncrementalSenateLobbyistStream((SenateLobbyistStream), ABC)` then have concrete stream implementations extend it. An example
    is provided below.

    See the reference docs for the full list of configurable options.
    """

    # TODO: Fill in the url base. Required.
    url_base = "https://lda.senate.gov/api/v1/"

    def __init__(self, config: Mapping[str, Any]):
        super().__init__(authenticator=config["authenticator"])
        self.config = config

    def next_page_token(self, response: requests.Response) -> Optional[Mapping[str, Any]]:
        """
        TODO: Override this method to define a pagination strategy. If you will not be using pagination, no action is required - just return None.

        This method should return a Mapping (e.g: dict) containing whatever information required to make paginated requests. This dict is passed
        to most other methods in this class to help you form headers, request bodies, query params, etc..

        For example, if the API accepts a 'page' parameter to determine which page of the result to return, and a response from the API contains a
        'page' number, then this method should probably return a dict {'page': response.json()['page'] + 1} to increment the page count by 1.
        The request_params method should then read the input next_page_token and set the 'page' param to next_page_token['page'].

        :param response: the most recent response from the API
        :return If there is another page in the result, a mapping (e.g: dict) containing information needed to query the next page in the response.
                If there are no more pages in the result, return None.
        """
        r = response.json()
        if r['next'] is None:
            return None
        page = int(r['next'].split('=')[1])
        return { 'nextUrl': r['next'] }

    def request_params(
        self, stream_state: Mapping[str, Any], stream_slice: Mapping[str, any] = None, next_page_token: Mapping[str, Any] = None
    ) -> MutableMapping[str, Any]:
        """
        TODO: Override this method to define any query parameters to be set. Remove this method if you don't need to define request params.
        Usually contains common params e.g. pagination size etc.
        """
        page = 1
        if (next_page_token is not None and next_page_token['nextUrl']):
            page = int(next_page_token['nextUrl'].split('=')[1])
        return {'page': page}

    def parse_response(self, response: requests.Response, **kwargs) -> Iterable[Mapping]:
        """
        TODO: Override this method to define how a response is parsed.
        :return an iterable containing each record in the response
        """

        json_response = response.json()
        for record in json_response["results"]:
            r = record
            r['registrant_id'] = r['registrant']['id']
            r['registrant_name'] = r['registrant']['name']
            r['registrant_description'] = r['registrant']['description']
            r['registrant_contact_name'] = r['registrant']['contact_name']
            r['registrant_telephone'] = r['registrant']['contact_telephone']
            r['registrant_updated_at'] = r['registrant']['dt_updated']
            yield r

class Lobbyists(SenateLobbyistStream):

    # TODO: Fill in the primary key. Required. This is usually a unique field in the stream, like an ID or a timestamp.
    primary_key = "id"

    def path(
        self, stream_state: Mapping[str, Any] = None, stream_slice: Mapping[str, Any] = None, next_page_token: Mapping[str, Any] = None
    ) -> str:
        """
        TODO: Override this method to define the path this stream corresponds to. E.g. if the url is https://example-api.com/v1/customers then this
        should return "customers". Required.
        """
        return "lobbyists"


class SenateAuthenticator(HttpAuthenticator):
    """
    Generate auth header for start making requests from API token and API key.
    """

    def __init__(
        self,
        key: str,
        auth_header: str = "Authorization",
    ):
        self.auth_header = auth_header
        self._key = key

    def get_auth_header(self) -> Mapping[str, Any]:
        return {self.auth_header: f'Token {self._key}'}

# Source
class SourceSenateLobbyist(AbstractSource):

    @staticmethod
    def _get_authenticator(config: dict) -> SenateAuthenticator:
        key = config["apiKey"]
        return SenateAuthenticator(key=key)

    def check_connection(self, logger, config) -> Tuple[bool, any]:
        """
        TODO: Implement a connection check to validate that the user-provided config can be used to connect to the underlying API

        See https://github.com/airbytehq/airbyte/blob/master/airbyte-integrations/connectors/source-stripe/source_stripe/source.py#L232
        for an example.

        :param config:  the user-input config object conforming to the connector's spec.yaml
        :param logger:  logger object
        :return Tuple[bool, any]: (True, None) if the input config can be used to connect to the API successfully, (False, error) otherwise.
        """
        try:
            authenticator = self._get_authenticator(config)
            url = f"{SenateLobbyistStream.url_base}"

            response = requests.get(url, headers=authenticator.get_auth_header())
            response.raise_for_status()
            return True, None
        except requests.exceptions.RequestException as e:
            return False, e

    def streams(self, config: Mapping[str, Any]) -> List[Stream]:
        """
        TODO: Replace the streams below with your own streams.

        :param config: A Mapping of the user input configuration as defined in the connector spec.
        """
        config["authenticator"] = self._get_authenticator(config)
        return [Lobbyists(config)]
