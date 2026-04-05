class Spirit:
    def __init__(self):
        self.name = ''
        self.rank = ''
        self.chunk = 12
        self.passage = ''
        self.raw_quote = ''
        self.needs_verification = False

    @property
    def provenance(self):
        return {
            'name': self.name,
            'rank': self.rank,
            'chunk': self.chunk,
            'passage': self.passage,
            'raw_quote': self.raw_quote,
            'needs_verification': self.needs_verification
        }
