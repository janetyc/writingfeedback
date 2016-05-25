def enum(*sequential, **named):
    enums = dict(zip(sequential, range(len(sequential))), **named)
    reverse = dict((value, key) for key, value in enums.iteritems())
    enums['reverse_mapping'] = reverse
    return type('Enum', (), enums)

TaskType = enum(
    TOPIC="topic", RELEVANCE="relevance", RELATION="relation"
)

RelationType = enum(
    ADDITION="Addition", SEQUENTIAL_ORDER="Sequential/Process Order", COMPARE="Compare", CONTRAST="Contrast", CAUSE="Cause", EFFECT="Effect", GENERATION="Generalization", SPECIFICATION="Specification", OTHERS="Others")

Status = enum(WORKING=0, FINISH=1, ACCEPT=2, REJECT=3)

WorkflowType = enum(
    UNITY="unity", COHERENCE="coherence"
)
