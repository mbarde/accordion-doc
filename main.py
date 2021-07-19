from lxml import etree


ignoreUnexpectedElements = False
repairIfPossible = True


def checkAccPanel(el, accIdNr):
    panelId = None
    panelIdNr = None

    schema = [
        {
            'action': 'start',
            'tag': 'div',
            'class': 'panel panel-default',
        },
        {
            'action': 'start',
            'tag': 'div',
            'class': 'panel-heading',
        },
        {
            'action': 'start',
            'tag': 'h4',
            'class': 'panel-title',
        },
        {
            'action': 'start',
            'tag': 'a',
            'class': 'accordion-toggle',
        },
        {
            'action': 'end',
            'tag': 'a',
            'class': 'accordion-toggle',
        },
        {
            'action': 'end',
            'tag': 'h4',
            'class': 'panel-title',
        },
        {
            'action': 'end',
            'tag': 'div',
            'class': 'panel-heading',
        },
        {
            'action': 'start',
            'tag': 'div',
            'class': 'panel-collapse',
        },
        {
            'action': 'start',
            'tag': 'div',
            'class': 'panel-body',
        },
        {
            'action': 'end',
            'tag': 'div',
            'class': 'panel-body',
        },
        {
            'action': 'end',
            'tag': 'div',
            'class': 'panel-collapse',
        },
        {
            'action': 'end',
            'tag': 'div',
            'class': 'panel panel-default',
        },
    ]

    # walk panel element and verify against schema
    ctx = etree.iterwalk(el, events=('start', 'end'))
    i = 0
    waitingFor = schema[i]
    for action, elem in ctx:

        if waitingFor is None:
            print('Error in panel ' + str(el) + ' (no further element expected)')
            print(action)
            print(elem.tag)
            print(elem.get('class', ''))
            return

        elemClass = elem.get('class', '')

        if action == 'start':

            # validate attributes of panel-heading
            # (populates panelId & panelIdNr)
            if elem.tag == 'div' and elemClass == 'panel-heading':
                panelId = elem.get('id', None)
                if panelId is None:
                    print('Missing panel id in accordion ' + accIdNr)
                    return
                cmpAccNr, panelIdNr, suffix = panelId.split('-')
                if cmpAccNr != accIdNr:
                    print('Panel has wrong accordion number: ' + panelId)
                    return
                if suffix != 'heading':
                    print('Panel has faulty id: ' + panelId)
                    return

            # validate attributes of accordion-toggle link
            if elem.tag == 'a' and 'accordion-toggle' in elemClass:
                href = elem.get('href', None)
                expected = '#{0}-{1}-body'.format(accIdNr, panelIdNr)
                if href != expected:
                    if repairIfPossible is True:
                        print('🗸 Faulty href in toggle link of panel ' + panelId)
                        elem.set('href', expected)
                    else:
                        print('Faulty href in toggle link of panel ' + panelId)
                        return
                dataParent = elem.get('data-parent', None)
                expected = '#{0}-accordion'.format(accIdNr)
                if dataParent != expected:
                    if repairIfPossible is True:
                        print('🗸 Faulty data-parent in toggle link of panel ' + panelId)
                        elem.set('data-parent', expected)
                    else:
                        print('Faulty data-parent in toggle link of panel ' + panelId)
                        return

            # validate attributes of panel-collapse
            if elem.tag == 'div' and 'panel-collapse' in elemClass:
                bodyId = elem.get('id', None)
                expected = '{0}-{1}-body'.format(accIdNr, panelIdNr)
                if bodyId != expected:
                    if repairIfPossible is True:
                        print('🗸 Faulty body id in panel ' + panelId)
                        elem.set('id', expected)
                    else:
                        print('Faulty body id in panel ' + panelId)
                        return

        if elem.tag == waitingFor['tag'] and \
           action == waitingFor['action']:
            # found expected element:
            classes = elemClass
            if waitingFor['class'] in classes:
                i += 1
                if i < len(schema):
                    waitingFor = schema[i]
                else:
                    waitingFor = None

        else:
            # found unexpected element (not in schema):
            if ignoreUnexpectedElements is False and i != 9:
                # is only allowed within panel body (ID 9 in schema)
                msg = 'Unexpected element'
                if panelId is not None:
                    msg += ' (in {0})'.format(panelId)
                msg += ': {0}.{1} - expected {2}'.format(elem.tag, elemClass, waitingFor)
                print(msg)

    if i != len(schema):
        print('Error in panel ' + str(el) + ' (missing ' + str(waitingFor) + ')')


def checkAccordion(el):
    accId = el.get('id', None)
    if accId is None:
        print('Missing accordion ID')
        return
    accIdNr, suffix = accId.split('-')
    if suffix != 'accordion':
        print('Accordion has faulty id: ' + accId)
        return
    panels = el.xpath('div[contains(@class, "panel-default")]')
    for panel in panels:
        checkAccPanel(panel, accIdNr)


parser = etree.HTMLParser(encoding='UTF-8')
tree = etree.parse('acc.html', parser)

accordions = tree.xpath('.//div[contains(@class, "panel-group")]')
for accordion in accordions:
    checkAccordion(accordion)

if repairIfPossible is True:
    with open('corrected.html', 'wb') as f:
        body = tree.xpath('//body')[0]
        bstr = etree.tostring(body, encoding='UTF-8')
        f.write(bstr[6:-7])
        # tree.write(f)