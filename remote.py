import twitter, logging, optparse, sys, os, simplejson, time


def apply_rules(sender, text, rules):
    def match(rule, txt):
        return rule == txt

    # narrow by rules available to sender
    rules = [ x for x in rules if sender in x['users'] ]
    rules = [ x for x in rules if match(x['pattern'], text) ]
    
    for rule in rules:
        logging.debug(u" (%s) %s => %s" % (sender, text, rule['rewrite']))
        os.command(rule['rewrite'])


def remote(user, pwd, rules, last_checked=None):

    api = twitter.Api(username=user, password=pwd)
    checked = int(str(time.time()).split('.')[0])
    for dm in api.GetDirectMessages(last_checked):
        apply_rules(dm.sender_screen_name, dm.text, rules)
        checked = int(str(dm.GetCreatedAtInSeconds()).split('.')[0])
    return checked


def main():
    p = optparse.OptionParser("usage: remote.py user pwd dir")
    (options, (user, pwd, dir)) = p.parse_args()

    # setup logger
    log_path = os.path.join(dir, 'remote.log')
    logging.basicConfig(filename=log_path, level=logging.DEBUG)
    
    # last checked
    timestamp_path = os.path.join(dir, 'timestamp')
    time = None
    try:
        fin = open(timestamp_path,'r')
        time = int(fin.read())
        fin.close()
    except IOError:
        pass
    except ValueError:
        pass

    # load rules
    rules_path = os.path.join(dir, 'rules.json')
    logging.debug(rules_path)

    rules = []
    try:
        fin = open(rules_path,'r')
        data = fin.read()
        rules = simplejson.loads(data)
        fin.close()
    except IOError:
        pass

        
    checked_at = remote(user, pwd, rules, time)
    fout = open(timestamp_path, 'w')
    fout.write(u"%s" % checked_at)
    fout.close()



if __name__ == "__main__":

    sys.exit(main())


