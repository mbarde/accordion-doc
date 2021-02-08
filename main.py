from lxml import etree


def checkAccPanel(el, accIdNr):
    panelId = None

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

        if elem.tag == 'div' and elemClass == 'panel-heading':
            panelId = elem.get('id', None)
            if panelId is None:
                print('Missing panel id in accordion ' + accIdNr)
                return
            cmpAccNr, panelIdNr, suffix = panelId.split('-')
            if cmpAccNr != accIdNr:
                print('Panel has wrong accordion number: ' + str(panelId))
                return
            if suffix != 'heading':
                print('Panel has faulty id: ' + str(panelId))
                return
            # print('checking panel ' + panelId)

        if elem.tag == 'div' and 'panel-collapse' in elemClass:
            bodyId = elem.get('id', None)
            if bodyId is None:
                print('Missing body id in panel ' + panelId)
                return
            cmpAccNr, bodyIdNr, suffix = bodyId.split('-')
            if bodyIdNr != panelIdNr:
                print('Body has wrong panel number: ' + str(bodyId))
                return
            if cmpAccNr != accIdNr:
                print('Body has wrong accordion number: ' + str(bodyId))
                return
            if suffix != 'body':
                print('Body has faulty id: ' + str(bodyId))
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
            if i != 9:
                # is only allowed within panel body (ID 9 in schema)
                msg = 'Unexpected element'
                if panelId is not None:
                    msg += ' (in ' + str(panelId) + ')'
                msg += ': ' + elem.tag + '.' + elemClass
                print(msg)
                # print(etree.tostring(elem).decode('utf-8'))

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


parser = etree.HTMLParser()
tree = etree.parse('test.html', parser)

accordions = tree.xpath('.//div[contains(@class, "panel-group")]')
for accordion in accordions:
    checkAccordion(accordion)
