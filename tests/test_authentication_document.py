from collections import defaultdict
import json
from nose.tools import (
    assert_raises_regexp,
    assert_raises,
    eq_,
    set_trace,
)
from sqlalchemy.orm.exc import (
    MultipleResultsFound,
)
from authentication_document import AuthenticationDocument

# Alias for a long class name
AuthDoc = AuthenticationDocument

class MockPlace(object):
    """Used to test AuthenticationDocument.parse_coverage."""

    # Used to indicate that a place name is ambiguous.
    AMBIGUOUS = object()

    # Used to indicate coverage through the universe or through a
    # country.
    EVERYWHERE = object()
    
    def __init__(self, by_name=None, is_inside=None):
        self.by_name = by_name or dict()
        self.is_inside = is_inside or dict()

    def _lookup(self, look_in):
        place = look_in.get(name)
        if place is self.AMBIGUOUS:
            raise MultipleResultsFound()
        return place

    def lookup_by_name(self, _db, name, place_type):
        return self._lookup(self.by_name)
        
    def lookup_inside(self, _db, name, must_be_inside):
        return self._lookup(self.is_inside)

    def everywhere(self, _db):
        return self.EVERYWHERE

class TestParseCoverage(object):

    def parse_places(self, mock_place, coverage_object, expected_places=None,
                     expected_unknown=None, expected_ambiguous=None):
        """Call AuthenticationDocument.parse_coverage. Verify that the
        dictionaries of unknown and ambiguous place names are empty,
        and that the parsed list of places is `expected`.
        """
        place_objs, unknown, ambiguous = AuthDoc.parse_coverage(
            None, coverage_object, mock_place
        )
        empty = defaultdict(list)
        expected_places = expected_places or []
        expected_unknown = expected_unknown or empty
        expected_ambiguous = expected_ambiguous or empty
        eq_(expected_places, place_objs)
        eq_(expected_unknown, unknown)
        eq_(expected_ambiguous, ambiguous)
        
    def test_universal_coverage(self):
        places = MockPlace()
        self.parse_places(
            places, AuthDoc.COVERAGE_EVERYWHERE, [MockPlace.EVERYWHERE]
        )
