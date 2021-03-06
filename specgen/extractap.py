import csv
import pydash
import os

def convert_csv(path):
    ap = []
    result = ""

    with open(path) as csvfile:
        dialect = csv.Sniffer().sniff(csvfile.read(4096))
        dialect.doublequote = True
        csvfile.seek(0)
        reader = csv.reader(csvfile, dialect)
        header = False

        for row in reader:
            if not header:
                header = row
            else:
                item = {}
                for i in range(0, len(row)):
                    item[header[i]] = row[i]
                ap.append(item)

    domains = pydash.without(pydash.uniq(pydash.map_(ap, 'EA-Domain')), '', None)
    codelists = pydash.filter_(ap, {'EA-Type': 'ENUMERATION'})
    domains = list(set(domains) - set(pydash.map_(codelists.copy(), 'EA-Name')))
    domains.sort()
    final_domains = []
    final_datypes = []
    classes = pydash.filter_(ap, {'EA-Type': 'CLASS'}) + pydash.filter_(ap, {'EA-Type': 'DATATYPE'})
    datatypes = pydash.map_(pydash.filter_(ap, {'EA-Type': 'DATATYPE'}), 'EA-Name')
    classes_only = pydash.map_(pydash.filter_(ap, {'EA-Type': 'CLASS'}), 'EA-Name')
    attributes = pydash.filter_(ap, {'EA-Type': 'attribute'}) + pydash.filter_(ap, {'EA-Type': 'connector'})
    attributes = pydash.sort_by(attributes, 'EA-Domain')
    # for enumeration in codelists:
    #    attributes = pydash.remove(attributes, {'EA-Domain': enumeration})

    title = os.path.splitext(os.path.basename(path))[0]
    package = pydash.find(ap, {'EA-Type': 'Package'})

    if len(domains) > 0:
        for domain in domains:

            klassen = pydash.filter_(classes, {'EA-Name': domain})
            if 0 < len(klassen) <= 1:
                klasse = pydash.find(classes, {'EA-Name': domain})
                if klasse['EA-Type'] == 'DATATYPE':
                    result += "\n[%s]\n" % domain
                    final_datypes.append(domain)
                else:
                    result += "\n[%s]\n" % domain
                    final_domains.append(domain)

                if klasse is not None:
                    result += 'ap-definition-nl=%s\n' % klasse['ap-definition-nl']
                    result += 'ap-usagenote-nl=%s\n' % klasse['ap-usageNote-nl']
                    result += 'namespace=%s\n' % klasse['namespace']
                    result += 'localname=%s\n' % klasse['localname']


                domain_attributes = pydash.filter_(attributes, {'EA-Domain': domain})
                domain_attribute_names = pydash.without(pydash.uniq(pydash.map_(domain_attributes, 'EA-Name')), '', None) #localname

                result += 'attributes=%s\n' % ','.join(domain_attribute_names)

                for attr_name in domain_attribute_names:
                    result += "\n[%s:%s]\n" % (domain, attr_name)
                    attr = pydash.find(domain_attributes, {'EA-Name': attr_name})
                    if attr['range'] == "http://www.w3.org/2004/02/skos/core#Concept":
                        ap_codelist = pydash.find(codelists, {'EA-Name': attr['EA-Range']})
                        if not ap_codelist is None:
                            attr['ap-codelist'] = ap_codelist['ap-codelist']
                    for key in attr:
                        result += '%s=%s\n' % (key, attr[key].replace('&', '&amp;'))

            elif len(klassen) > 1:
                for klasse in klassen:
                    if klasse['ap-label-nl'] == "":
                        klasse['ap-label-nl'] = domain
                    if klasse['EA-Type'] == 'DATATYPE':
                        result += "\n[%s]\n" % klasse['ap-label-nl']
                        final_datypes.append(klasse['ap-label-nl'])
                    else:
                        result += "\n[%s]\n" % klasse['ap-label-nl']
                        final_domains.append(klasse['ap-label-nl'])
                    if klasse is not None:
                        result += 'ap-definition-nl=%s\n' % klasse['ap-definition-nl']
                        result += 'ap-usagenote-nl=%s\n' % klasse['ap-usageNote-nl']
                        result += 'namespace=%s\n' % klasse['namespace']
                        result += 'localname=%s\n' % klasse['localname']

                    domain_attributes = pydash.filter_(attributes,
                                                       {'EA-Domain-GUID': klasse['EA-GUID']})
                    domain_attribute_names = pydash.without(pydash.uniq(
                        pydash.map_(domain_attributes, 'localname')), '', None)

                    result += 'attributes=%s\n' % ','.join(
                        domain_attribute_names)

                    for attr_name in domain_attribute_names:
                        result += "\n[%s:%s]\n" % (klasse['ap-label-nl'], attr_name)
                        attr = pydash.find(domain_attributes,
                                           {'localname': attr_name})
                        if attr[
                            'range'] == "http://www.w3.org/2004/02/skos/core#Concept":
                            ap_codelist = pydash.find(codelists, {
                                'EA-Name': attr['EA-Range']})
                            if not ap_codelist is None:
                                attr['ap-codelist'] = ap_codelist[
                                    'ap-codelist']
                        for key in attr:
                            result += '%s=%s\n' % (key, attr[key])

        result += "\n[overview]\n"
        final_domains = list(set(final_domains))
        final_domains.sort()
        result += 'entities=%s\n' % ','.join(final_domains)
        result += 'dtypes=%s\n' % ','.join(final_datypes)
        if package is not None:
            result += 'package=%s\n' % package['EA-Name'].replace('OSLO-', '')
        result += 'title=%s\n' % title

    return [result, package['EA-Name'].replace('OSLO-', '')]
