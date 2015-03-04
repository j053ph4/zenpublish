#! /usr/bin/env python
from lib.ZenossHandler import *
import argparse, json

# TEST VARS

VERBOSE = False

# DEVICE = 'testhost'
# COMPONENT = 'testcomponent'
# SEVERITY = 3
# SUMMARY = "TESTING"
# EVCLASSKEY = 'TESTING'
# EVCLASS = '/Unknown'


class ZenEvent(object):
    ''''''
    def __init__(self):
        ''''''
        self.buildOptions()
        self.zen = ZenossHandler(self.args.zenoss, self.args.username, self.args.password, self.args.verbose)
        self.data = {
                     'device': self.args.device,
                     'component': self.args.component,
                     'summary': self.args.summary,
                     'severity': self.args.severity,
                     'eventClassKey': self.args.evclasskey,
                     'eventClass': self.args.evclass
                     }
        # these keys return a dictionary
        self.dicttypes = ['device','component','eventClass' ]
    
    def findEventID(self):
        ''''''
        results = self.zen.getEvents()
        try: events = results['events']
        except: events = []
        for e in events:
            # create a temp dictionary for comparison
            comparison = {}
            # using the local keys
            for k in self.data.keys():
                # find the equivalent value
                evval = e[k]
                # pull only the text value for comparison
                if k in self.dicttypes: evval = evval['text']
                comparison[k] = evval
            # if comparison matches the arguments, return the event ID
            if comparison == self.data: return e['id']

    def run(self):
        '''main execution'''
        if self.args.new is True:
            #print "creating event"
            # depending on action either:
            # create a new event with parameters
            event = self.zen.createEvent(summary=self.data['summary'], device=self.data['device'], component=self.data['component'], severity=self.data['severity'], evclasskey=self.data['eventClassKey'], evclass=self.data['eventClass'])
            #print event
        # update/close event 
        else:
            if self.args.ack is True: action = "acknowledge"
            else: action = "close"
            #print "changing event status to %s" % action
            # first search for event
            evid = self.findEventID()
            # then apply desired change
            self.zen.manageEventStatus([evid], action)
    
    def buildOptions(self):
        '''define runtime arguments'''
        self.parser = argparse.ArgumentParser(description='Zenoss event export')
        # Run Options
        self.parser.add_argument('-n','--new', help='whether to create or update an event', action="store_true")
        self.parser.add_argument('-a','--ack', help='whether to acknowledge instead of close', action="store_true")
        
        # Connection parameters
        self.parser.add_argument('-z','--zenoss', help='hostname or ip of Zenoss server', required=True)
        self.parser.add_argument('-u','--username', help='Zenoss account username', required=True)
        self.parser.add_argument('-p','--password', help='Zenoss account password', required=True)
        
        # Event Parameters
        self.parser.add_argument('-d','--device', help='device parameter', required=True)
        self.parser.add_argument('-c','--component', help='component (can be blank)',  required=False)
        self.parser.add_argument('-j','--evclass', help='eventClass', required=False)
        self.parser.add_argument('-k','--evclasskey', help='eventKey (can be blank)', required=False)
        self.parser.add_argument('-s','--severity', help='"Severity" event parameter', required=False)
        self.parser.add_argument('-m','--summary', help='summary (omitted from the dedupid if evclasskey is non-blank)', required=False)
        self.parser.add_argument('-v','--verbose', help='increase output verbosity', action="store_true")
        
        self.args = self.parser.parse_args()


if __name__ == "__main__":
    u = ZenEvent()
    u.run()
