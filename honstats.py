# Honstats by Kevin Darlington (http://outroot.com)

import sys
import httplib
import urllib
from PHPUnserialize import PHPUnserialize

#-----------------------------------------
class Stats(object):
  #=========================================
  def __init__(self):
    # Just one of the stat servers. Eventually I should either iterate through
    # s2games[number] until we find a server that is up, or see if HoN queries
    # the master server for a stat server list.
    self.http = httplib.HTTPConnection('s2games14.hosting.flyingcroc.net')
    # Headers we need for the backend script to recognize us. Anything that
    # strays from this gets a 404 back.
    self.headers = {
      'Host': 'masterserver.hon.s2games.com',
      'User-Agent': 'PHP Script',  
      'Content-Type': 'application/x-www-form-urlencoded',
      'Connection': 'close'
    }
    
  #=========================================
  def post(self, data):
    """Do an HTTP post to /client_requester.php and return the response.
    """
    # Attempt to encode the data. If data is not an object, then just assume it's
    # an already encoded string.
    try:
      data = urllib.urlencode(data)
    except TypeError:
      pass
    
    self.http.request('POST', '/client_requester.php', headers=self.headers, body=data)
    return self.http.getresponse()

  #=========================================
  def lookup(self, names):
    """Looks up the statistics given a list of names.
    returns a tuple of the id mapping and the stats.
    """
    post_data = {
      'f': 'nick2id' # The nick to id function. We're searching by nick.
    }
    
    # Add all the names passed to our post_data in the format defined by the protocol.
    for index,name in enumerate(names):
      post_data['nickname[{0}]'.format(index)] = name
    
    # Send the data and read the response.
    res = self.post(post_data)
    data = res.read().split('\n')[-1]

    # The data is returned in a PHP serialized format. Unserialize it.
    id_mapping = PHPUnserialize().unserialize(data)
    
    post_data = {
      'f': 'get_all_stats' # The get all stats function.
    }
    
    # Add all the ids of the accounts we want to get the stats to.
    for index,name in enumerate(names):
      post_data['account_id[{0}]'.format(index)] = id_mapping.get(id_mapping.keys()[1])
    
    # Send the data and read the response.
    res = self.post(post_data)    
    data = res.read()
    # The data is returned in a PHP serialized format. Unserialize it.
    stats = PHPUnserialize().unserialize(data)
    
    return (id_mapping, stats)

#=========================================
def print_stats(id_mapping, stats):
  for map_key,map_value in id_mapping.iteritems():
    if map_key != 0:
      print('----------------------------------------')
      print('Stats for "{0}"'.format(map_key))
      print('----------------------------------------')
       
      for stat_key,stat_value in stats['all_stats'][int(map_value)].iteritems():
        print('{0:25} : {1}'.format(stat_key, stat_value))
  
if __name__ == '__main__':
  stats = Stats()
  
  (id_mapping, stats) = stats.lookup(sys.argv[1:])
  print_stats(id_mapping, stats)
