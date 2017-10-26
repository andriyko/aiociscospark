# pragma: no cover
import os.path
from pkg_resources import get_distribution, DistributionNotFound

_pkg_name = 'aiociscospark'

try:
    _dist = get_distribution(_pkg_name)
    # Normalize case for Windows systems
    dist_loc = os.path.normcase(_dist.location)
    here = os.path.normcase(__file__)
    if not here.startswith(os.path.join(dist_loc, _pkg_name)):
        # not installed, but there is another version that *is*
        raise DistributionNotFound
except DistributionNotFound:
    __version__ = 'Please install this project with setup.py'
else:
    __version__ = _dist.version
