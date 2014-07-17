import json
import sys

existing = json.load(open('bibpy/abbreviations.json'))
existing = [[e[0].encode('utf-8'), e[1].encode('utf-8')] for e in existing]
existing_keys = set(e[1] for e in existing)
initial_number = len(existing)

# wget http://jabref.sourceforge.net/journals/journal_abbreviations_lifescience.txt
# wget http://jabref.sourceforge.net/journals/journal_abbreviations_ams.txt

for file in sys.argv[1:]:
    items = [[e.strip() for e in line.split(' = ')[::-1]] for line in open(sys.argv[1]) if not line.startswith('#')]

    for item in items:
        if item[1] not in existing_keys:
            existing.append(item)


print 'Added %d entries' % (len(existing) - initial_number)

existing = sorted(existing, key=lambda x: x[1])
json.dump(existing, open('new.json', 'w'), indent=4)
print('saving to new.json')
