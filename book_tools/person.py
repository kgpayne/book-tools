from nameparser import HumanName


class NameParseError(Exception):
    pass


class Name:

    def __init__(
        self, given_name, surname, middle_name=None,
        prefix=None, suffix=None, nickname=None
    ):
        self.given_name = given_name
        self.surname = surname
        self.middle_name = middle_name

        self.prefix = prefix
        self.suffix = suffix
        self.nickname = nickname

    def __repr__(self):
        return f"Name('{self.given_name} {self.surname}')"

    def __str__(self):
        return (
            f"{self.given_name} "
            + f"{self.middle_name}" if self.middle_name else "" +
            f"{self.surname}"
        )

    @classmethod
    def from_string(cls, text):
        hn = HumanName(text)
        return cls(
            given_name=hn.first,
            middle_name=hn.middle,
            surname=hn.last,

            prefix=hn.title,
            suffix=hn.suffix,
            nickname=hn.nickname
        )
