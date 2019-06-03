import itertools
import json
from dataclasses import dataclass
from typing import List


@dataclass
class Handler:
    name: str
    options: str


@dataclass
class Location:
    path: str
    handlers: List[Handler]

    def find_handlers(self, name: str) -> List[Handler]:
        return list(filter(lambda handler: handler.name == name, self.handlers))


@dataclass
class Domain:
    host: str
    locations: List[Location]

    def find_handlers(self, name: str) -> List[Handler]:
        return list(itertools.chain.from_iterable(map(lambda location: location.find_handlers(name), self.locations)))


class Config:
    def __init__(self, path):
        try:
            with open(path) as f:
                domains = json.load(f)
                # for host, locations in domains.items():
                #
                #     print(host)
                #     print(locations)
                self.domains = list(map(parse_domain, domains.items()))
        except FileNotFoundError:
            print('Configuration file not found!')
            exit(1)


def parse_domain(data) -> Domain:
    host, locations = data
    return Domain(
        host=host,
        locations=list(map(parse_location, locations.items()))
        if not isinstance(locations, str)
        else [Location(path='/', handlers=parse_handlers(locations))]
    )


def parse_location(data) -> Location:
    path, handlers = data
    return Location(path=path, handlers=parse_handlers(handlers))


def parse_handlers(handlers_string: str) -> List[Handler]:
    handlers = []
    for handler in handlers_string.split(';'):
        handler = handler.strip()
        if ' ' in handler:
            name, options = handler.split(' ')
            handlers.append(Handler(name=name, options=options))
        else:
            handlers.append(Handler(name=handler, options=''))
    return handlers
